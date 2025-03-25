from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import json

from structured_content import StructuredContent
from chunk import Chunk
from entity import Entity
from relationship import Relationship
from formula import Formula
from picture import Picture
from table import Table
from reference import Reference
from link import Link
from element import Element
from ordered_list import OrderedList

class Document(ABC):
    """
    文档类型的抽象基类
    """
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        checksum: Optional[str] = None,
        content: Optional[str] = None,
        length: Optional[int] = None,
        tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        structured_content: Optional[StructuredContent] = None,
        chunks: Optional[OrderedList[Chunk]] = None,
        entities: Optional[List[Entity]] = None,
        relationships: Optional[List[Relationship]] = None,
        formulas: Optional[List[Formula]] = None,
        pictures: Optional[List[Picture]] = None,
        tables: Optional[OrderedList[Table]] = None,
        links: Optional[OrderedList[Link]] = None,
        references: Optional[List[Reference]] = None,
        authors: Optional[List[str]] = None,
        publisher: Optional[str] = None,
        url: Optional[str] = None,
        date: Optional[str] = None,
        version: Optional[str] = None,
        summary: Optional[str] = None,
        summary_vectors: Optional[str] = None,
        keywords: Optional[List[str]] = None,  # 新增属性：关键字列表
    ):
        """
        初始化 Document 对象。

        Args:
            id (str): 文档的唯一标识符。
            name (str): 文档的名称。
            type (str): 文档的类型（例如 "pdf", "txt"）。
            checksum (Optional[str]): 文档内容的 SHA1 校验和。
            content (Optional[str]): 文档的文本内容。
            length (Optional[int]): 文档内容的字符长度。
            tokens (Optional[int]): 文档内容中的 token 数量。
            metadata (Optional[Dict[str, Any]]): 与文档关联的元数据。
            structured_content (Optional[StructuredContent]): 结构化内容层次结构的根。
            chunks (Optional[OrderedList[Chunk]]): 文档中的内容块列表。
            entities (Optional[List[Entity]]): 从文档中提取的实体列表。
            relationships (Optional[List[Relationship]]): 从文档中提取的关系列表。
            formulas (Optional[List[Formula]]): 文档中找到的公式列表。
            pictures (Optional[List[Picture]]): 文档中找到的图片列表。
            tables (Optional[OrderedList[Table]]): 文档中找到的表格列表。
            links (Optional[OrderedList[Link]]): 文档中找到的链接列表。
            references (Optional[List[Reference]]): 文档中的参考文献列表。
            authors (Optional[List[str]]): 文档的作者列表。
            publisher (Optional[str]): 文档的发布者。
            url (Optional[str]): 文档的 URL。
            date (Optional[str]): 文档的发布或访问日期。
            version (Optional[str]): 文档的版本。
            summary (Optional[str]): 文档的摘要。
            summary_vectors (Optional[str]): 文档摘要的向量表示。
            keywords (Optional[List[str]]): 关键字列表。
        """
        self.id = id
        self.name = name
        self.type = type
        self.checksum = checksum
        self.content = content
        self.length = length
        self.tokens = tokens
        self.metadata = metadata if metadata is not None else {}
        self.structured_content = structured_content
        self.chunks = chunks if chunks is not None else OrderedList()
        self.entities = entities if entities is not None else []
        self.relationships = relationships if relationships is not None else []
        self.formulas = formulas if formulas is not None else []
        self.pictures = pictures if pictures is not None else []
        self.tables = tables if tables is not None else OrderedList()
        self.links = links if links is not None else OrderedList()
        self.references = references if references is not None else []
        self.authors = authors if authors is not None else []
        self.publisher = publisher
        self.url = url
        self.date = date
        self.version = version
        self.summary = summary
        self.summary_vectors = summary_vectors
        self.keywords = keywords if keywords is not None else []  # 初始化关键字

    def generate_toc(self, level: int = 1) -> List[Dict[str, Any]]:
        """
        生成指定层级的目录（Table of Contents）。

        Args:
            level (int): 指定要生成目录的层次级别。

        Returns:
            List[Dict[str, Any]]: 每个字典包含 id、title 和 content 信息。
        """
        if self.structured_content:
            return self.structured_content.get_catalogue(level)
        return []

    def to_dict(self) -> Dict[str, Any]:
        """
        将文档对象转换为字典形式，包含结构化内容及各部分列表。

        Returns:
            Dict[str, Any]: 文档信息的字典表示。
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "checksum": self.checksum,
            "content": self.content,
            "length": self.length,
            "tokens": self.tokens,
            "metadata": self.metadata,
            "structured_content": self.structured_content.to_dict() if self.structured_content else None,
            "chunks": [chunk.__repr__() for chunk in self.chunks],
            "entities": [entity.__repr__() for entity in self.entities],
            "relationships": [relationship.__repr__() for relationship in self.relationships],
            "formulas": [formula.__repr__() for formula in self.formulas],
            "pictures": [picture.__repr__() for picture in self.pictures],
            "tables": [table.__repr__() for table in self.tables],
            "links": [link.__repr__() for link in self.links],
            "references": [reference.__repr__() for reference in self.references],
            "authors": self.authors,
            "publisher": self.publisher,
            "url": self.url,
            "date": self.date,
            "version": self.version,
            "summary": self.summary,
            "summary_vectors": self.summary_vectors,
            "keywords": self.keywords,
        }

    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """
        更新文档元数据。

        Args:
            new_metadata (Dict[str, Any]): 新的元数据信息，键值对将更新现有 metadata。
        """
        self.metadata.update(new_metadata)

    def get_section_by_title(self, title: str) -> Optional[StructuredContent]:
        """
        根据标题查找结构化内容中的某个部分。

        Args:
            title (str): 要查找的标题。

        Returns:
            Optional[StructuredContent]: 如果找到对应章节则返回，否则返回 None。
        """
        if self.structured_content:
            return self._find_section_by_title(self.structured_content, title)
        return None

    def _find_section_by_title(self, node: StructuredContent, title: str) -> Optional[StructuredContent]:
        if node.title == title:
            return node
        for child in node.children:
            result = self._find_section_by_title(child, title)
            if result:
                return result
        return None

    def search_content(self, query: str) -> List[str]:
        """
        在文档正文、结构化内容和内容块中搜索指定关键字。

        Args:
            query (str): 查询的字符串内容。

        Returns:
            List[str]: 匹配的文本片段列表。
        """
        results = []
        if self.content and query in self.content:
            results.append(self.content)
        if self.structured_content:
            def search_node(node: StructuredContent):
                if node.content and query in node.content:
                    results.append(node.content)
                for child in node.children:
                    search_node(child)
            search_node(self.structured_content)
        for chunk in self.chunks:
            if chunk.content and query in chunk.content:
                results.append(chunk.content)
        return results

    @abstractmethod
    def extract_content(self, extractor: Any) -> str:
        """
        抽象方法，用于使用特定的提取器提取文档的主要内容。

        Args:
            extractor (Any): 适用于该文档类型的提取器类的实例。

        Returns:
            str: 提取的文档内容。
        """
        pass

    def extract_entities(self, provider: Any) -> List[Entity]:
        """
        使用语言模型提供者从文档内容中提取实体。

        Args:
            provider (Any): 语言模型提供者的实例。

        Returns:
            List[Entity]: 提取的 Entity 对象列表。
        """
        # 示例实现，需替换为实际的调用
        return [Entity(id="entity1", doc_id=self.id, name="示例实体", type="GENERIC")]

    def extract_relationships(self, provider: Any) -> List[Relationship]:
        """
        使用语言模型提供者从文档内容中提取实体之间的关系。

        Args:
            provider (Any): 语言模型提供者的实例。

        Returns:
            List[Relationship]: 提取的 Relationship 对象列表。
        """
        # 示例实现，需替换为实际的调用
        return [Relationship(id="rel1", doc_id=self.id, from_entity_id="entity1", to_entity_id="entity2")]

    def chunking(self, chunker: Any) -> OrderedList[Chunk]:
        """
        使用分块器将文档内容拆分为更小的块。

        Args:
            chunker (Any): Chunker 类的实例。

        Returns:
            OrderedList[Chunk]: 内容块的有序列表。
        """
        # 示例实现，需替换为实际的分块逻辑
        return OrderedList([Chunk(id="chunk1", doc_id=self.id, order_index=0, content="示例内容", tokens=10)])

    def embedding(self) -> str:
        """
        为整个文档生成嵌入向量。

        Returns:
            str: 文档嵌入向量示例。
        """
        # 示例实现，需替换为实际的嵌入逻辑
        return f"Embedding for document {self.id}"

    def get_link_content(self) -> str:
        """
        返回文档的摘要，用作链接内容的后备信息。

        Returns:
            str: 文档摘要或空字符串。
        """
        return self.summary or ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}', type='{self.type}')"


# 以下为具体子类示例，以论文为例实现 Document 的抽象方法 extract_content

class PaperDocument(Document):
    def extract_content(self, extractor: Any) -> str:
        """
        模拟使用提取器提取论文正文的实现，此处直接返回文档内容。

        Args:
            extractor (Any): 论文内容提取器（此示例未实际使用）。

        Returns:
            str: 论文的主要内容。
        """
        return self.content or ""

    def to_json(self) -> str:
        """
        将论文文档转换为 JSON 格式。

        Returns:
            str: JSON 字符串。
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 构造一篇论文的结构化存储示例

    # 创建论文结构根节点（论文标题）
    paper_sc = StructuredContent(
        id="paper-001",
        level=0,
        title="A Study on Artificial Intelligence",
        content="整篇论文的全文内容略..."
    )

    # 添加摘要节点
    abstract_sc = StructuredContent(
        id="paper-001-abstract",
        level=1,
        title="Abstract",
        content="This paper presents a study on artificial intelligence advances..."
    )
    paper_sc.add_child(abstract_sc)

    # 添加 Introduction 节点，并在其下添加子章节
    intro_sc = StructuredContent(
        id="paper-001-intro",
        level=1,
        title="Introduction",
        content="The introduction section introduces the background and motivation..."
    )
    paper_sc.add_child(intro_sc)
    background_sc = StructuredContent(
        id="paper-001-intro-bg",
        level=2,
        title="Background",
        content="Detailed background information of AI..."
    )
    intro_sc.add_child(background_sc)

    # 添加 Methods 节点
    methods_sc = StructuredContent(
        id="paper-001-methods",
        level=1,
        title="Methods",
        content="This section describes the research methodology..."
    )
    paper_sc.add_child(methods_sc)

    # 添加 Results 节点
    results_sc = StructuredContent(
        id="paper-001-results",
        level=1,
        title="Results",
        content="Experimental results are presented and analyzed..."
    )
    paper_sc.add_child(results_sc)

    # 构造论文文档
    paper_doc = PaperDocument(
        id="doc-001",
        name="AI Research Paper",
        type="pdf",
        content="Full text content of the paper...",
        structured_content=paper_sc,
        authors=["Alice", "Bob"],
        publisher="Academic Press",
        date="2025-03-25",
        summary="A research paper on artificial intelligence.",
        keywords=["AI", "Machine Learning", "Deep Learning"]
    )

    # 测试方法
    print("论文文档展示:")
    print(paper_doc)
    print("\n生成的目录（一级目录）:")
    for item in paper_doc.generate_toc(1):
        print(item)
    print("\n查询标题为 'Introduction' 的章节:")
    section = paper_doc.get_section_by_title("Introduction")
    print(section)
    print("\n搜索关键词 'AI' 在文档中的匹配结果:")
    results = paper_doc.search_content("AI")
    print(results)
    print("\n文档转换为字典形式:")
    print(json.dumps(paper_doc.to_dict(), indent=2, ensure_ascii=False))
    print("\n文档转换为 JSON 格式:")
    print(paper_doc.to_json())