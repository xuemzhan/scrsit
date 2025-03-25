import uuid
from typing import Optional, List

from element import Element  # 确保导入路径正确


class Reference(Element):
    """
    表示文档中的参考文献，同时继承自 Element 类以获得通用属性。
    除了通用属性外，Reference 还记录了作者、发布者、URL 和日期等信息。
    """
    def __init__(
        self,
        id: Optional[str],
        doc_id: str,
        authors: Optional[List[str]] = None,
        publisher: Optional[str] = None,
        url: Optional[str] = None,
        date: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        vectors: Optional[str] = None,
    ):
        """
        初始化 Reference 对象。

        Args:
            id (Optional[str]): 参考文献的唯一标识符，若为 None 则自动生成。
            doc_id (str): 参考文献所属文档的标识符。
            authors (Optional[List[str]]): 参考文献的作者列表。
            publisher (Optional[str]): 参考文献的发布者。
            url (Optional[str]): 参考文献的 URL。
            date (Optional[str]): 参考文献的发布日期或访问日期。
            name (Optional[str]): 参考文献的名称或标题。
            content (Optional[str]): 参考文献的内容（例如引用的文本）。
            description (Optional[str]): 参考文献的描述信息。
            vectors (Optional[str]): 参考文献的向量表示。
        """
        if id is None:
            id = str(uuid.uuid4())
        # 调用父类 Element 初始化通用属性
        super().__init__(
            id=id,
            doc_id=doc_id,
            chunk_id=None,
            name=name,
            content=content,
            description=description,
            vectors=vectors,
        )
        self.authors = authors if authors is not None else []
        self.publisher = publisher
        self.url = url
        self.date = date

    def __repr__(self) -> str:
        return (
            f"Reference(id='{self.id}', name='{self.name}', authors={self.authors}, "
            f"publisher='{self.publisher}', url='{self.url}', date='{self.date}')"
        )


if __name__ == "__main__":
    # 测试用例

    # 用例1：传入所有参数
    ref1 = Reference(
        id="ref-1",
        doc_id="doc-001",
        authors=["Alice", "Bob"],
        publisher="Academic Press",
        url="https://example.com/reference1",
        date="2025-03-25",
        name="Reference Title 1",
        content="引用的文本内容……",
        description="详细描述该参考文献的信息",
        vectors="vector_data_ref1",
    )

    # 用例2：自动生成 id，部分参数使用默认值
    ref2 = Reference(
        id=None,
        doc_id="doc-002",
        authors=["Carol"],
        publisher="Science Publisher",
        url="https://example.com/reference2",
        date="2025-03-26",
        name="Reference Title 2",
    )

    print("参考文献示例：")
    print(ref1)
    print(ref2)