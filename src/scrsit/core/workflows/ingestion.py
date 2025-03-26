# src/scrsit/core/workflows/ingestion.py

"""
文档摄入工作流。
协调 Parser -> Chunker -> Embedder -> Analyzers -> Stores 的过程。
"""
import logging
from typing import Union, IO, Optional, List, Dict, Any
import time
import traceback

from scrsit.core.document.models import Document, DocumentType
from scrsit.core.plugin_manager import PluginManager
from scrsit.core.exceptions import WorkflowError, ParsingError, EmbeddingError, AnalysisError, StorageError
from scrsit.core.interfaces import (
    BaseParser, BaseChunker, BaseEmbedder, BaseAnalyzer,
    BaseDocumentStore, BaseVectorStore, BaseStructuredStore
)

logger = logging.getLogger(__name__)

class IngestionWorkflow:
    """
    执行文档摄入流程的类。
    """
    def __init__(self, plugin_manager: PluginManager):
        """
        初始化摄入工作流。

        Args:
            plugin_manager (PluginManager): 用于获取所需插件实例的插件管理器。
        """
        self.plugin_manager = plugin_manager
        logger.info("IngestionWorkflow 初始化完成。")

    def _get_document_type(self, filename: Optional[str]) -> DocumentType:
        """根据文件名猜测文档类型。"""
        if not filename:
            return DocumentType.UNKNOWN
        ext = filename.split('.')[-1].lower()
        try:
            return DocumentType(ext)
        except ValueError:
            logger.warning(f"无法识别的文件扩展名: {ext}，文档类型设为 UNKNOWN。")
            return DocumentType.UNKNOWN

    def run(self,
            file_source: Union[str, IO[bytes]],
            filename: Optional[str] = None,
            doc_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            save_document: bool = True,
            save_chunks: bool = True,
            run_analysis: bool = True,
            ) -> Document:
        """
        执行完整的文档摄入流程。

        Args:
            file_source (Union[str, IO[bytes]]): 文件路径或二进制IO流。
            filename (Optional[str]): 原始文件名 (用于确定类型和名称)。
            doc_id (Optional[str]): 如果提供，则使用此 ID；否则生成新的 ID。
            metadata (Optional[Dict[str, Any]]): 要附加到文档的元数据。
            save_document (bool): 是否将解析后的 Document 对象保存到文档存储。
            save_chunks (bool): 是否将生成的 Chunks 及其 Embeddings 保存到向量存储。
            run_analysis (bool): 是否运行配置的分析器提取信息。

        Returns:
            Document: 处理完成的文档对象。

        Raises:
            WorkflowError: 如果流程中任何关键步骤失败。
            ParsingError, EmbeddingError, AnalysisError, StorageError: 更具体的错误类型。
        """
        start_time = time.time()
        logger.info(f"开始执行文档摄入工作流，文件名: {filename or '未知'}")

        # 1. 确定文档类型和名称
        doc_type = self._get_document_type(filename)
        doc_name = filename or f"document_{int(start_time)}"

        # 2. 获取解析器并解析文档
        parser: BaseParser = None
        try:
            parser = self.plugin_manager.get_parser(file_type=doc_type.value if doc_type != DocumentType.UNKNOWN else None)
            logger.info(f"使用解析器 '{parser.__class__.__name__}' 解析文档 '{doc_name}'...")
            document = parser.parse(file_source)

            # 补充/覆盖文档信息
            if doc_id: document.id = doc_id
            document.name = doc_name
            document.type = doc_type
            if metadata: document.metadata.update(metadata)
            if document.content: document.length = len(document.content) # 粗略长度

            logger.info(f"文档解析成功，ID: {document.id}")

        except Exception as e:
            logger.exception(f"文档解析失败: {e}", exc_info=True)
            raise ParsingError(f"解析文档 '{doc_name}' 失败: {e}") from e

        # 3. 获取分块器并分块
        try:
            chunker: BaseChunker = self.plugin_manager.get_chunker()
            logger.info(f"使用分块器 '{chunker.__class__.__name__}' 对文档进行分块...")
            chunks = chunker.chunk(document)
            document.chunks = chunks # 将分块结果存回 Document 对象
            if chunks:
                logger.info(f"文档成功分块，共生成 {len(chunks)} 个 Chunks。")
            else:
                logger.warning("分块器未生成任何 Chunks。")
        except Exception as e:
            logger.exception(f"文档分块失败: {e}", exc_info=True)
            raise WorkflowError(f"文档 '{document.id}' 分块失败: {e}") from e

        # 4. 获取 Embedder 并生成 Embeddings (如果需要保存 Chunks)
        embeddings: Optional[List[List[float]]] = None
        if save_chunks and document.chunks:
            try:
                embedder: BaseEmbedder = self.plugin_manager.get_embedder()
                logger.info(f"使用 Embedder '{embedder.__class__.__name__}' 为 Chunks 生成 Embeddings...")
                chunk_contents = [chunk.content for chunk in document.chunks]
                embeddings = embedder.embed(chunk_contents)

                if len(embeddings) == len(document.chunks):
                    for chunk, embedding in zip(document.chunks, embeddings):
                        chunk.vectors = embedding # 将 Embedding 存入 Chunk 对象
                    logger.info(f"成功为 {len(embeddings)} 个 Chunks 生成 Embeddings。")
                else:
                    logger.error(f"Embedder 返回的 Embeddings 数量 ({len(embeddings)}) 与 Chunks 数量 ({len(document.chunks)}) 不匹配。")
                    raise EmbeddingError("Embeddings 数量与 Chunks 数量不匹配。")

            except Exception as e:
                logger.exception(f"生成 Embeddings 失败: {e}", exc_info=True)
                raise EmbeddingError(f"为文档 '{document.id}' 的 Chunks 生成 Embeddings 失败: {e}") from e
        elif save_chunks and not document.chunks:
             logger.warning("配置了保存 Chunks，但没有 Chunks 可以生成 Embedding。")


        # 5. 运行分析器 (如果启用)
        if run_analysis:
            analyzers: List[BaseAnalyzer] = self.plugin_manager.get_enabled_analyzers()
            if analyzers:
                logger.info(f"开始运行 {len(analyzers)} 个启用的分析器...")
                for analyzer in analyzers:
                    try:
                        logger.info(f"运行分析器 '{analyzer.__class__.__name__}' (类型: {analyzer.analysis_type})...")
                        # 分析器可以作用于整个文档或每个 Chunk，这里以作用于文档为例
                        analysis_result = analyzer.analyze(document)

                        # 根据分析结果类型更新 Document 对象 (需要约定好数据结构)
                        # 例如，如果是实体提取器返回 Entity 列表
                        if analyzer.analysis_type == "entity_extraction" and isinstance(analysis_result, list):
                             document.entities.extend(analysis_result)
                             logger.info(f"实体提取器找到 {len(analysis_result)} 个实体。")
                        # elif analyzer.analysis_type == "relationship_extraction" ...
                        # ... 处理其他类型的分析结果 ...
                        else:
                             logger.warning(f"分析器 '{analyzer.__class__.__name__}' 返回了未知的或未处理的结果类型: {type(analysis_result)}")

                    except Exception as e:
                        logger.exception(f"运行分析器 '{analyzer.__class__.__name__}' 失败: {e}", exc_info=True)
                        # 根据策略决定是否继续运行其他分析器或抛出异常
                        # 这里选择记录错误并继续
                        # raise AnalysisError(f"运行分析器 '{analyzer.__class__.__name__}' 失败: {e}") from e
                logger.info("所有启用的分析器运行完成。")
            else:
                logger.info("没有启用任何分析器，跳过分析步骤。")

        # 6. 保存到存储 (如果配置)
        # 6.1 保存 Chunks 和 Embeddings 到向量存储
        if save_chunks and document.chunks and embeddings:
            try:
                vector_store: BaseVectorStore = self.plugin_manager.get_vector_store()
                logger.info(f"使用向量存储 '{vector_store.__class__.__name__}' 保存 Chunks 和 Embeddings...")
                added_ids = vector_store.add_embeddings(document.chunks, embeddings)
                logger.info(f"成功向向量存储添加了 {len(added_ids)} 个 Chunks。")
            except Exception as e:
                logger.exception(f"保存 Chunks 到向量存储失败: {e}", exc_info=True)
                raise StorageError(f"保存文档 '{document.id}' 的 Chunks 到向量存储失败: {e}") from e

        # 6.2 保存结构化分析结果 (如果需要，例如保存到结构化存储)
        if run_analysis and (document.entities or document.relationships): # 示例：如果有实体或关系
             try:
                 structured_store: BaseStructuredStore = self.plugin_manager.get_structured_store()
                 logger.info(f"使用结构化存储 '{structured_store.__class__.__name__}' 保存分析结果...")
                 if document.entities:
                     # 假设 Entity 模型可以直接序列化为字典
                     entity_data = [entity.model_dump() for entity in document.entities]
                     structured_store.save_batch("entities", entity_data)
                     logger.info(f"保存了 {len(document.entities)} 个实体到结构化存储。")
                 if document.relationships:
                     relationship_data = [rel.model_dump() for rel in document.relationships]
                     structured_store.save_batch("relationships", relationship_data)
                     logger.info(f"保存了 {len(document.relationships)} 个关系到结构化存储。")
                 # ... 保存其他结构化数据 ...
             except NotImplementedError:
                 logger.warning(f"默认结构化存储不支持保存操作或批处理操作，跳过保存分析结果。")
             except Exception as e:
                 logger.exception(f"保存分析结果到结构化存储失败: {e}", exc_info=True)
                 # 通常不应因为这个失败而中断整个流程，只记录错误
                 # raise StorageError(f"保存文档 '{document.id}' 的分析结果失败: {e}") from e

        # 6.3 保存完整 Document 对象到文档存储 (通常最后执行)
        if save_document:
            try:
                doc_store: BaseDocumentStore = self.plugin_manager.get_document_store()
                logger.info(f"使用文档存储 '{doc_store.__class__.__name__}' 保存完整文档对象...")
                # 在保存前，可以选择性地清理大数据字段，如 content 或 embeddings
                # doc_to_save = document.copy(deep=True)
                # doc_to_save.content = None # 如果不希望在文档库中存储原始内容
                # for chunk in doc_to_save.chunks: chunk.vectors = None # 向量存储在 VectorDB
                doc_store.save(document)
                logger.info(f"文档对象 '{document.id}' 成功保存到文档存储。")
            except Exception as e:
                logger.exception(f"保存文档对象到文档存储失败: {e}", exc_info=True)
                raise StorageError(f"保存文档 '{document.id}' 到文档存储失败: {e}") from e

        end_time = time.time()
        logger.info(f"文档摄入工作流执行完毕，总耗时: {end_time - start_time:.2f} 秒。")

        return document

# --- 其他工作流的占位符 ---

# src/scrsit/core/workflows/analysis.py (示例结构)
class AnalysisWorkflow:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        logger.info("AnalysisWorkflow 初始化完成。")

    def run(self, doc_id: str, analysis_tasks: List[str], **kwargs):
        logger.info(f"开始执行文档 '{doc_id}' 的分析工作流，任务: {analysis_tasks}")
        # 1. 从 DocumentStore 加载文档
        # 2. 根据 analysis_tasks 获取对应的 Analyzers
        # 3. 依次执行分析任务
        # 4. (可选) 获取 KnowledgeProvider 进行知识增强或验证
        # 5. (可选) 获取 Reviewer 进行评审
        # 6. (可选) 获取 ProposalGenerator 生成提议
        # 7. 更新 DocumentStore 或 StructuredStore 中的结果
        pass

# src/scrsit/core/workflows/retrieval.py (示例结构)
class RetrievalWorkflow:
     def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        logger.info("RetrievalWorkflow 初始化完成。")

     def run(self, query: str, top_k: int = 5, **kwargs):
         logger.info(f"开始执行检索工作流，查询: '{query}'")
         # 1. 使用 Embedder 将查询文本转换为向量
         # 2. 使用 VectorStore 进行相似性搜索，获取 top_k Chunks
         # 3. (可选) 从 DocumentStore 获取相关 Chunk 的完整上下文或文档信息
         # 4. (可选) 使用 LLMProvider 进行 RAG (Retrieval-Augmented Generation) 生成答案
         pass

# src/scrsit/core/workflows/comparison.py (示例结构)
class ComparisonWorkflow:
     def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        logger.info("ComparisonWorkflow 初始化完成。")

     def run(self, doc_id_1: str, doc_id_2: str, **kwargs):
         logger.info(f"开始执行文档比较工作流，文档: '{doc_id_1}' vs '{doc_id_2}'")
         # 1. 从 DocumentStore 加载两个文档
         # 2. (可选) 对比元数据、结构化内容
         # 3. (可选) 对比 Chunks 或 Embeddings (可能需要特定算法)
         # 4. (可选) 对比提取的实体、关系等分析结果
         # 5. (可选) 使用 LLMProvider 分析差异并生成报告
         pass