# src/scrsit/core/document/models.py

"""
定义核心领域数据模型 (使用 Pydantic)。
这些是在系统内部流转的数据结构，基于 UML 图设计。
"""
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
import datetime

from src.scrsit.core.utils.helpers import generate_uuid

# --- 基础元素 ---

class Element(BaseModel):
    """文档中可识别的基础内容元素的基类 (概念上的，实际嵌入到 Document 中)。"""
    id: str = Field(default_factory=lambda: generate_uuid()) # 元素唯一ID
    name: Optional[str] = None                               # 元素名称 (例如，图表标题)
    content: Optional[Union[str, bytes]] = None              # 元素原始内容 (文本或二进制)
    description: Optional[str] = None                        # 元素描述
    vectors: Optional[List[float]] = None                    # 元素的向量表示 (如果适用)
    version: str = "1.0"                                     # 数据模型版本
    embedding: Optional[List[float]] = Field(exclude=True, default=None) # 临时存储的 Embedding，不一定持久化

class Formula(Element):
    """公式元素。"""
    raw: str # 公式的原始表示 (例如 LaTeX, MathML 或 base64 图片)
    # GetFormula() 方法逻辑应在解析或分析阶段处理

class Picture(Element):
    """图片元素。"""
    content: bytes # 图片的二进制内容 (替代基类的 content)
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None # 文件大小 (bytes)

class Table(Element):
    """表格元素。"""
    # 表格内容建议结构化存储，例如 list of lists 或 list of dicts
    content: Optional[Any] = None # 表格数据 (例如，解析后的结构化数据)
    order_index: Optional[int] = None # 表格在文档中的顺序索引 (如果适用)

class Reference(Element):
    """文献引用元素。"""
    authors: List[str] = Field(default_factory=list) # 作者列表
    publisher: Optional[str] = None                  # 出版社
    url: Optional[str] = None                        # 链接 URL
    date: Optional[datetime.date] = None             # 出版日期

class Link(Element):
    """链接元素 (例如，内部引用或外部超链接)。"""
    target: str # 链接目标 (URL 或内部标识符)
    summary: Optional[str] = None # 链接内容的摘要 (可能由分析器生成)
    summary_vectors: Optional[List[float]] = None # 摘要的向量
    # GetLinkContent() 方法逻辑应在需要时由外部服务处理 (例如爬虫)


# --- 结构化内容 ---

class StructuredContent(BaseModel):
    """表示文档的结构化内容，例如章节、段落。"""
    id: str = Field(default_factory=lambda: generate_uuid())      # 结构唯一ID
    parent_id: Optional[str] = None                                # 父结构ID (用于构建层级)
    level: int = 0                                                 # 结构层级 (例如 0:文档, 1:章, 2:节)
    content: str                                                   # 该结构单元的文本内容
    # parent: Optional['StructuredContent'] = None # 避免循环引用，使用 parent_id
    children: List['StructuredContent'] = Field(default_factory=list) # 子结构列表

# --- 核心文档模型 ---

class DocumentType(str, Enum):
    """支持的文档类型枚举。"""
    PDF = "pdf"
    MARKDOWN = "markdown"
    EXCEL = "excel"
    WORD = "word"
    PPT = "ppt"
    HTML = "html"
    PICTURE = "picture"
    TEXT = "text"
    UNKNOWN = "unknown"

class EntityType(str, Enum):
    """实体类型枚举 (示例)。"""
    LOW = "Low"
    NEUTRAL = "Neutral"
    HIGH = "High"
    # 可以根据需求定义更具体的类型，如 PERSON, ORG, REQUIREMENT, CONSTRAINT 等

class Chunk(BaseModel):
    """文档内容的切片（块）。"""
    id: str = Field(default_factory=lambda: generate_uuid())      # Chunk 唯一 ID
    doc_id: str                                                    # 所属文档 ID
    order_index: int                                               # Chunk 在文档中的顺序
    tokens: Optional[int] = None                                   # Chunk 的 token 数量 (可选)
    content: str                                                   # Chunk 的文本内容
    vectors: Optional[List[float]] = None                          # Chunk 内容的向量表示
    embedding: Optional[List[float]] = Field(exclude=True, default=None) # 临时存储的 Embedding

class Entity(BaseModel):
    """从文档中提取的实体。"""
    id: str = Field(default_factory=lambda: generate_uuid())      # 实体唯一 ID
    name: str                                                      # 实体名称/文本
    type: Union[EntityType, str] = EntityType.NEUTRAL              # 实体类型 (使用枚举或字符串)
    description: Optional[str] = None                              # 实体的描述
    vectors: Optional[List[float]] = None                          # 实体名称/描述的向量表示
    sources: Dict[str, List[str]] = Field(default_factory=dict)    # 来源信息 {doc_id: [chunk_id1, chunk_id2]}
    embedding: Optional[List[float]] = Field(exclude=True, default=None) # 临时存储的 Embedding

class Relationship(BaseModel):
    """实体之间的关系。"""
    id: str = Field(default_factory=lambda: generate_uuid())      # 关系唯一 ID
    from_entity_id: str                                            # 起始实体 ID
    to_entity_id: str                                              # 目标实体 ID
    weight: Optional[float] = None                                 # 关系权重/强度
    description: str                                               # 关系描述 (例如 "依赖", "包含", "导致")
    keywords: List[str] = Field(default_factory=list)              # 与关系相关的关键词
    sources: Dict[str, List[str]] = Field(default_factory=dict)    # 来源信息 {doc_id: [chunk_id1, chunk_id2]}
    embedding: Optional[List[float]] = Field(exclude=True, default=None) # 临时存储的 Embedding

class Document(BaseModel):
    """
    核心文档模型，代表一个被处理的文档及其分析结果。
    """
    id: str = Field(default_factory=lambda: generate_uuid())          # 文档唯一 ID
    name: str                                                          # 文档名称 (例如文件名)
    type: DocumentType = DocumentType.UNKNOWN                        # 文档类型 (根据文件扩展名或内容猜测)
    checksum: Optional[str] = None                                     # 文档内容的校验和 (例如 sha1)
    content: Optional[str] = None                                      # 文档的原始文本内容 (可能很大，考虑是否存储)
    structured_content: Optional[StructuredContent] = None             # 文档的结构化内容表示 (可选)
    length: Optional[int] = None                                       # 文档内容的长度 (字符数)
    tokens: Optional[int] = None                                       # 文档内容的 token 数 (可选)
    metadata: Dict[str, Any] = Field(default_factory=dict)             # 文档的元数据 (例如作者, 创建日期等)

    # --- 分析结果 ---
    entities: List[Entity] = Field(default_factory=list)               # 文档中提取的实体列表
    relationships: List[Relationship] = Field(default_factory=list)    # 文档中提取的关系列表
    formulas: List[Formula] = Field(default_factory=list)              # 文档中的公式列表
    pictures: List[Picture] = Field(default_factory=list)              # 文档中的图片列表
    tables: List[Table] = Field(default_factory=list)                  # 文档中的表格列表
    links: List[Link] = Field(default_factory=list)                    # 文档中的链接列表 (内/外部)
    references: List[Reference] = Field(default_factory=list)          # 文档中的文献引用列表

    # --- 处理过程产物 ---
    chunks: List[Chunk] = Field(default_factory=list)                  # 文档切分后的 Chunks 列表
    embedding: Optional[List[float]] = Field(exclude=True, default=None) # 整个文档的 Embedding (如果需要)

    # 注意：UML 图中的 ExtractContent, ExtractEntities, ExtractRelationships, Chunking, Embedding
    # 这些是动作/过程，应该由工作流 (Workflows) 或服务来协调调用相应的插件 (Parser, Analyzer, Chunker, Embedder) 完成，
    # 而不是作为 Document 模型的方法。Document 模型主要负责承载数据。

# 更新 StructuredContent 的前向引用
# StructuredContent.model_rebuild()

if __name__ == '__main__':
    # 测试 Entity 类
    test_entity = Entity(
        name="测试实体",
        type=EntityType.HIGH,
        description="这是一个高优先级测试实体"
    )
    print("Entity 对象:")
    print(test_entity.model_dump_json(indent=4))
    
    # 测试 Relationship 类
    test_entity2 = Entity(
        name="测试实体2",
        type="Neutral",
        description="这是另一个测试实体"
    )
    test_relationship = Relationship(
        from_entity_id=test_entity.id,
        to_entity_id=test_entity2.id,
        description="依赖关系测试"
    )
    print("Relationship 对象:")
    print(test_relationship.model_dump_json(indent=4))
    
    # 测试 Document 类，并关联以上实体和关系
    test_document = Document(
        name="测试文档",
        type=DocumentType.PDF,
        content="这是测试文档的内容。"
    )
    test_document.entities.extend([test_entity, test_entity2])
    test_document.relationships.append(test_relationship)
    
    print("Document 对象:")
    print(test_document.model_dump_json(indent=4))