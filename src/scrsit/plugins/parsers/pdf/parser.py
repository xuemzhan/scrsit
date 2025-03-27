# src/scrsit/plugins/parsers/pdf/parser.py
"""
基于 MinerU (magic_pdf) 的 PDF 文档解析器实现。
"""
import logging
import tempfile
import asyncio
import os
import time
from typing import Union, IO, List, Optional, Dict, Any, Tuple
from pathlib import Path

import base64 # 确保导入 base64 用于处理图片数据

# 核心框架导入
from src.scrsit.core.interfaces import BaseParser
from src.scrsit.core.document.models import (
    Document, DocumentType, Picture, Table, StructuredContent
)
from src.scrsit.core.exceptions import ParsingError, ConfigurationError
from src.scrsit.core.utils.helpers import generate_uuid # 假设有这个工具函数

# 本插件配置
from config import PdfParserConfig

# 第三方库导入
try:
    import magic_pdf
except ImportError:
    magic_pdf = None # 稍后检查
    # print("警告：MinerU (magic_pdf) 未安装。PdfMinerUParser 将不可用。")
    # raise ImportError("请安装 'minerU' 或 'magic_pdf' 以使用此解析器: pip install minerU")

try:
    from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
except ImportError:
    # 如果 tenacity 未安装，提供一个简单的 retry 装饰器或禁用重试
    print("警告: 'tenacity' 库未安装，将禁用自动重试功能。建议安装: pip install tenacity")
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = None
    wait_fixed = None
    retry_if_exception_type = None

logger = logging.getLogger(__name__)

class PdfMinerUParser(BaseParser):
    """
    使用 MinerU (magic_pdf) 库解析 PDF 文档。

    支持特性：
    - 异步处理
    - 基于 tenacity 的自动重试
    - 按页（或批次）处理大型文档
    - 进度日志记录
    - 将 magic_pdf 输出映射到核心 Document 模型
    """
    plugin_name: str = "pdf_miner_u" # 插件的唯一名称，可被 PluginManager 使用

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化解析器。

        Args:
            config (Optional[Dict[str, Any]]): 从配置中传入的插件特定设置。
        """
        self.raw_config = config or {}
        try:
            self.config = PdfParserConfig(**self.raw_config)
            logger.debug(f"PdfMinerUParser 配置加载成功: {self.config.model_dump()}")
        except Exception as e: # 捕获 Pydantic ValidationError 等
            logger.error(f"PdfMinerUParser 配置无效: {e}", exc_info=True)
            raise ConfigurationError(f"PdfMinerUParser 配置错误: {e}") from e

        if magic_pdf is None:
            logger.error("MinerU (magic_pdf) 库未找到或导入失败。此解析器无法工作。")
            raise ImportError("请安装 'minerU' 或 'magic_pdf' 以使用 PdfMinerUParser。")

        # 配置 tenacity 重试装饰器 (如果 tenacity 可用)
        if retry_if_exception_type:
            self.retry_decorator = retry(
                stop=stop_after_attempt(self.config.retry_attempts),
                wait=wait_fixed(self.config.retry_delay_seconds),
                retry=retry_if_exception_type(Exception), # 可根据需要调整重试的异常类型
                before_sleep=lambda retry_state: logger.warning(
                    f"调用 magic_pdf 失败，正在重试第 {retry_state.attempt_number} 次..."
                    f"异常: {retry_state.outcome.exception()}"
                ),
                reraise=True # 重试耗尽后重新抛出原始异常
            )
        else:
            # 定义一个无操作的装饰器
            def noop_decorator(func):
                return func
            self.retry_decorator = noop_decorator


    @property
    def supported_types(self) -> List[str]:
        """返回支持的文件类型扩展名列表。"""
        return ["pdf"]

    async def _ensure_pdf_path(self, file_source: Union[str, IO[bytes], bytes], filename: Optional[str]) -> Path:
        """
        确保我们有一个 PDF 文件路径供 magic_pdf 使用。
        如果输入是 IO 流或 bytes，则保存到临时文件。
        """
        pdf_path: Path
        temp_file_handle = None

        if isinstance(file_source, (str, Path)):
            pdf_path = Path(file_source)
            if not pdf_path.is_file():
                raise FileNotFoundError(f"提供的 PDF 文件路径不存在: {pdf_path}")
            logger.debug(f"使用提供的文件路径: {pdf_path}")
        elif hasattr(file_source, 'read'): # IO 流
            logger.debug("输入是 IO 流，将内容保存到临时文件...")
            try:
                # 使用带名字的临时文件，确保 magic_pdf 能访问
                temp_file_handle = tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False, # 手动删除以确保 magic_pdf 处理完之前文件存在
                    dir=self.config.temp_file_dir # 使用配置的临时目录
                )
                content = file_source.read()
                if isinstance(content, str): # 如果是文本流，尝试编码
                    content = content.encode('utf-8', errors='ignore')
                temp_file_handle.write(content)
                pdf_path = Path(temp_file_handle.name)
                temp_file_handle.close() # 关闭句柄，但文件保留
                logger.debug(f"IO 流内容已保存到临时文件: {pdf_path}")
            except Exception as e:
                if temp_file_handle:
                     temp_file_handle.close()
                     if pdf_path and pdf_path.exists():
                         os.unlink(pdf_path) # 确保清理
                logger.error(f"无法将 IO 流保存到临时文件: {e}", exc_info=True)
                raise ParsingError(f"处理输入 IO 流时出错: {e}") from e
        elif isinstance(file_source, bytes):
            logger.debug("输入是 bytes，将内容保存到临时文件...")
            try:
                temp_file_handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=self.config.temp_file_dir)
                temp_file_handle.write(file_source)
                pdf_path = Path(temp_file_handle.name)
                temp_file_handle.close()
                logger.debug(f"Bytes 内容已保存到临时文件: {pdf_path}")
            except Exception as e:
                if temp_file_handle:
                     temp_file_handle.close()
                     if pdf_path and pdf_path.exists():
                         os.unlink(pdf_path)
                logger.error(f"无法将 bytes 保存到临时文件: {e}", exc_info=True)
                raise ParsingError(f"处理输入 bytes 时出错: {e}") from e
        else:
            raise TypeError(f"不支持的文件源类型: {type(file_source)}")

        # 返回路径和临时文件句柄（如果创建了）的名字用于后续清理
        return pdf_path, temp_file_handle.name if temp_file_handle else None


    async def _call_magic_pdf_with_retry(self, pdf_path: Path, page_indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        在线程池中异步调用 magic_pdf.process，并应用重试逻辑。
        """
        logger.debug(f"准备调用 magic_pdf.process (路径: {pdf_path}, 页面: {page_indices or '全部'})")
        options = self.config.magic_pdf_options.copy()
        if page_indices:
            options['page_indices'] = page_indices

        # 定义需要重试的同步函数
        @self.retry_decorator
        def sync_process():
            try:
                start_magic = time.time()
                result = magic_pdf.process(str(pdf_path), **options)
                end_magic = time.time()
                page_info = f"页面 {page_indices}" if page_indices else "全部页面"
                logger.debug(f"magic_pdf.process 调用成功 ({page_info})，耗时: {end_magic - start_magic:.2f} 秒")
                return result
            except Exception as e:
                logger.error(f"magic_pdf.process 调用失败 (路径: {pdf_path}, 页面: {page_indices}): {e}", exc_info=True)
                # 如果配置了保存中间文件，在这里可以实现保存逻辑
                if self.config.save_intermediate_files:
                    # 例如：将 pdf_path 复制到一个特定的错误文件目录
                    pass
                raise # 重新抛出异常，以便 tenacity 进行重试

        # 使用 asyncio.to_thread 在线程池中运行同步函数
        try:
            # 注意：如果 magic_pdf 内部已经是多线程或异步的，to_thread 可能不是最优选择
            # 但对于 CPU 密集型或阻塞型同步库，这是标准做法
            result_dict = await asyncio.to_thread(sync_process)
            return result_dict
        except Exception as e:
            # 重试耗尽后，异常会在这里被捕获
            logger.error(f"magic_pdf 处理失败（重试次数已用尽或未启用重试）", exc_info=True)
            raise ParsingError(f"magic_pdf 处理 PDF 时发生严重错误: {e}") from e

    def _map_result_to_document(self, doc: Document, magic_results: List[Dict[str, Any]]) -> Document:
        """
        将来自 magic_pdf 的（可能是分批的）结果映射到 Document 对象。

        Args:
            doc (Document): 初始的 Document 对象 (包含 id, name, type 等)。
            magic_results (List[Dict[str, Any]]): magic_pdf.process 返回的结果字典列表。

        Returns:
            Document: 更新后的 Document 对象。
        """
        aggregated_content = []
        all_pictures = []
        all_tables = []
        all_formulas = [] # 假设 magic_pdf 能提取公式

        logger.debug(f"开始将 {len(magic_results)} 个 magic_pdf 结果映射到 Document 模型...")

        for result in magic_results:
            if not isinstance(result, dict):
                logger.warning(f"magic_pdf 返回了非字典类型的结果，已跳过: {type(result)}")
                continue

            # 提取元数据 (假设 magic_pdf 返回类似结构)
            # 注意：magic_pdf 的确切输出结构需要参考其文档
            if 'doc_meta' in result and isinstance(result['doc_meta'], dict):
                 doc.metadata.update(result['doc_meta'])

            # 提取内容块 (假设 'content' 是包含文本块的列表)
            page_content_blocks = result.get('content', [])
            if isinstance(page_content_blocks, list):
                for block in page_content_blocks:
                     # 假设每个块是字典，包含 'text' 和 'bbox', 'type' 等
                     if isinstance(block, dict) and 'text' in block:
                         aggregated_content.append(block.get('text', ''))
                         # TODO: 更精细地处理块类型，构建 StructuredContent
                         # 例如：检查 block['type'] == 'paragraph', 'title', etc.
                         # 如果需要构建层级结构，需要更复杂的逻辑来处理块的顺序和关系

            # 提取图片 (假设 'images' 是图片信息列表)
            page_images = result.get('images', [])
            if isinstance(page_images, list):
                 for img_info in page_images:
                     if isinstance(img_info, dict) and 'base64' in img_info: # 或 'img_bytes'
                         try:
                             # 假设 img_info 包含 'bbox', 'base64' 等
                             pic_content = base64.b64decode(img_info['base64'])
                             picture = Picture(
                                 content=pic_content,
                                 # 可以尝试从 img_info 获取 name, description, width, height 等
                                 name=img_info.get('name'),
                                 # bbox 通常是 [x0, y0, x1, y1]
                                 # width = img_info.get('width') or (img_info.get('bbox')[2] - img_info.get('bbox')[0] if img_info.get('bbox') else None),
                                 # height = img_info.get('height') or (img_info.get('bbox')[3] - img_info.get('bbox')[1] if img_info.get('bbox') else None),
                             )
                             all_pictures.append(picture)
                         except Exception as e:
                             logger.warning(f"处理提取的图片数据时出错: {e}", exc_info=True)

            # 提取表格 (假设 'tables' 是表格信息列表)
            page_tables = result.get('tables', [])
            if isinstance(page_tables, list):
                 for tbl_info in page_tables:
                      if isinstance(tbl_info, dict): # 假设包含 'html' 或 'markdown' 或 'cells'
                          try:
                             # 优先使用结构化数据（如 cells），其次是 HTML/Markdown
                             table_content = tbl_info.get('cells') # 假设是 list of lists
                             if not table_content and 'html' in tbl_info:
                                 table_content = tbl_info['html'] # 备选：存储HTML
                             elif not table_content and 'markdown' in tbl_info:
                                  table_content = tbl_info['markdown'] # 备选：存储Markdown

                             table = Table(
                                 content=table_content,
                                 name=tbl_info.get('caption'), # 假设有标题
                                 # order_index 需要根据处理顺序或页面/位置信息设定
                             )
                             all_tables.append(table)
                          except Exception as e:
                              logger.warning(f"处理提取的表格数据时出错: {e}", exc_info=True)

            # 提取公式 (如果 magic_pdf 支持)
            # page_formulas = result.get('formulas', []) ...

        # 组合和赋值
        doc.content = "\n\n".join(aggregated_content) # 用换行符分隔不同块的文本
        doc.pictures = all_pictures
        doc.tables = all_tables
        doc.formulas = all_formulas # 如果有的话
        doc.length = len(doc.content)

        # TODO: 构建 StructuredContent (可选，较复杂)
        # 如果 magic_pdf 提供了足够详细的结构信息（如层级、块类型），可以在这里构建树状结构

        logger.debug("magic_pdf 结果映射到 Document 模型完成。")
        return doc


    async def aparse(self,
                     file_source: Union[str, IO[bytes], bytes],
                     filename: Optional[str] = None,
                     doc_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     **kwargs # 捕获任何额外的、特定于调用的参数
                     ) -> Document:
        """
        异步解析给定的 PDF 文件源。

        Args:
            file_source (Union[str, IO[bytes], bytes]): 文件路径、二进制IO流或 bytes。
            filename (Optional[str]): 原始文件名，用于生成 Document 名称和类型推断。
            doc_id (Optional[str]): 预设的文档 ID。
            metadata (Optional[Dict[str, Any]]): 附加到文档的元数据。
            **kwargs: 额外的解析参数 (目前未使用，但接口兼容)。

        Returns:
            Document: 解析后的核心文档对象。

        Raises:
            ParsingError: 如果解析过程中发生不可恢复的错误。
            FileNotFoundError: 如果 file_source 是路径且文件不存在。
            TypeError: 如果 file_source 类型不支持。
            ConfigurationError: 如果插件配置错误。
        """
        start_time = time.time()
        logger.info(f"开始使用 PdfMinerUParser 解析 PDF (文件名: {filename or '未知'})")

        pdf_path: Optional[Path] = None
        temp_file_name: Optional[str] = None
        total_pages = 0 # 用于进度计算

        try:
            # 1. 确保有可用的 PDF 文件路径
            pdf_path, temp_file_name = await self._ensure_pdf_path(file_source, filename)

            # 2. (可选但推荐) 获取总页数用于进度报告
            #    使用轻量级库如 pypdf 避免先用 magic_pdf 处理整个文档
            try:
                # 延迟导入 pypdf，仅在需要时加载
                from pypdf import PdfReader
                reader = PdfReader(pdf_path)
                total_pages = len(reader.pages)
                logger.info(f"PDF 总页数: {total_pages}")
            except ImportError:
                logger.warning("'pypdf' 未安装，无法获取总页数，将不提供基于页数的进度。建议安装: pip install pypdf")
            except Exception as page_count_error:
                 logger.warning(f"获取 PDF 总页数时出错: {page_count_error}，将不提供进度。")

            # 3. 初始化 Document 对象
            document = Document(
                id=doc_id or generate_uuid(),
                name=filename or pdf_path.name,
                type=DocumentType.PDF,
                metadata=metadata or {},
            )
            # 添加解析器元数据
            document.metadata['parser_info'] = {
                'parser_name': self.plugin_name,
                'parser_config': self.config.model_dump(exclude_unset=True),
                'parsed_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

            # 4. 调用 magic_pdf 处理
            magic_results = []
            processed_pages = 0

            if total_pages > 0 and self.config.page_batch_size > 0:
                # 按页或批次处理
                num_batches = (total_pages + self.config.page_batch_size - 1) // self.config.page_batch_size
                logger.info(f"将按批次处理 PDF，共 {num_batches} 批，每批最多 {self.config.page_batch_size} 页。")

                for i in range(num_batches):
                    batch_start_page = i * self.config.page_batch_size
                    batch_end_page = min((i + 1) * self.config.page_batch_size, total_pages)
                    # magic_pdf 的 page_indices 是 0-based
                    page_indices = list(range(batch_start_page, batch_end_page))

                    logger.info(f"开始处理批次 {i+1}/{num_batches} (页面 {batch_start_page + 1} 到 {batch_end_page})...")
                    batch_result = await self._call_magic_pdf_with_retry(pdf_path, page_indices=page_indices)
                    magic_results.append(batch_result)

                    processed_pages = batch_end_page
                    progress = (processed_pages / total_pages) * 100
                    logger.info(f"批次 {i+1}/{num_batches} 处理完成。进度: {progress:.1f}% ({processed_pages}/{total_pages} 页)")

            else:
                # 处理整个文档
                logger.info("处理整个 PDF 文档（无分页或无法获取总页数）...")
                full_result = await self._call_magic_pdf_with_retry(pdf_path)
                magic_results.append(full_result)
                logger.info("整个文档处理完成。")

            # 5. 映射结果到 Document 模型
            logger.info("开始将 magic_pdf 的输出映射到 Document 对象...")
            document = self._map_result_to_document(document, magic_results)

            end_time = time.time()
            logger.info(f"PDF 解析成功完成。总耗时: {end_time - start_time:.2f} 秒。文档 ID: {document.id}")
            return document

        except Exception as e:
            # 捕获所有在流程中可能出现的异常
            end_time = time.time()
            logger.exception(f"PDF 解析过程中发生未处理的错误。耗时: {end_time - start_time:.2f} 秒。", exc_info=True)
            # 包装为 ParsingError
            if not isinstance(e, ParsingError):
                 raise ParsingError(f"PDF 解析失败: {e}") from e
            else:
                 raise # 如果已经是 ParsingError，直接抛出

        finally:
            # 6. 清理临时文件（如果创建了）
            if temp_file_name and Path(temp_file_name).exists():
                try:
                    os.unlink(temp_file_name)
                    logger.debug(f"已清理临时文件: {temp_file_name}")
                except OSError as unlink_error:
                    logger.warning(f"清理临时文件失败: {unlink_error}")

    # (可选) 提供同步接口的包装
    def parse(self,
              file_source: Union[str, IO[bytes], bytes],
              filename: Optional[str] = None,
              doc_id: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None,
              **kwargs) -> Document:
        """同步解析接口 (包装异步实现)。"""
        logger.warning("调用同步 parse 接口，将在内部运行异步 aparse。建议直接使用 aparse 以获得更好性能。")
        try:
             # 尝试获取或创建一个事件循环来运行异步代码
             loop = asyncio.get_running_loop()
             return loop.create_task(self.aparse(file_source, filename, doc_id, metadata, **kwargs)).result() # 不推荐在库中这样做
        except RuntimeError: # 没有正在运行的事件循环
             # 创建新事件循环运行（注意：这在某些上下文下可能不是最佳选择）
             return asyncio.run(self.aparse(file_source, filename, doc_id, metadata, **kwargs))


