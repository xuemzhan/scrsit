import uuid
from typing import List, Optional

from element import Element  # 确保导入路径正确
from structured_content import StructuredContent

class Table(Element):
    """
    表示文档中的表格，同时继承自 Element 类以获得通用属性。
    表格解析后经过OCR提取转成结构化数据存储，
    表格可能跨页，即可能对应多张图片（images），
    若文档中嵌入了其他表格，则可将其作为子表格（embedded_tables）存储。
    """
    def __init__(
        self,
        id: Optional[str],
        doc_id: str,
        order_index: int,
        content: str,
        structured_content: Optional[StructuredContent] = None,
        images: Optional[List[str]] = None,
        embedded_tables: Optional[List['Table']] = None,
    ):
        """
        初始化 Table 对象。

        Args:
            id (Optional[str]): 表格的唯一标识符，若为 None 则自动生成。
            doc_id (str): 表格所属文档的标识符。
            order_index (int): 表格在文档中的顺序。
            content (str): 表格的文字内容（如OCR提取结果）。
            structured_content (Optional[StructuredContent]): 表格的结构化表示。
            images (Optional[List[str]]): 表格转换前对应的图片ID列表（跨页情况）。
            embedded_tables (Optional[List[Table]]): 嵌入在当前表格内的子表格列表。
        """
        if id is None:
            id = str(uuid.uuid4())
        # 调用父类 Element 初始化通用属性
        super().__init__(
            id=id,
            doc_id=doc_id,
            chunk_id=None,
            name="Table",
            content=content,
            description=None,
            vectors=None,
        )
        self.order_index = order_index
        self.structured_content = structured_content
        self.images = images if images is not None else []
        self.embedded_tables = embedded_tables if embedded_tables is not None else []

    def add_embedded_table(self, table: 'Table') -> None:
        """
        添加嵌入的子表格到当前表格中。

        Args:
            table (Table): 要添加的嵌入表格对象。
        """
        self.embedded_tables.append(table)

    def __repr__(self) -> str:
        content_snippet = (self.content[:20] + "...") if self.content and len(self.content) > 20 else self.content
        return (f"Table(id='{self.id}', order_index={self.order_index}, content='{content_snippet}', " 
                f"images={self.images}, embedded_tables_count={len(self.embedded_tables)})")


if __name__ == "__main__":
    # 测试用例1：基本表格，跨页情况存在多张图片
    table1 = Table(
        id=None,
        doc_id="doc-001",
        order_index=1,
        content="OCR提取的表格内容：Col1, Col2, Col3...",
        structured_content=None,
        images=["img-001", "img-002"]
    )

    # 测试用例2：含有嵌入表格
    # 构造一个嵌入表格对象
    embedded_table = Table(
        id=None,
        doc_id="doc-001",
        order_index=2,
        content="嵌入表格内容：SubCol1, SubCol2...",
        images=["img-003"]
    )
    # 将嵌入表格添加到 table1 中
    table1.add_embedded_table(embedded_table)

    print("表格对象测试：")
    print(table1)
    print("嵌入表格列表：")
    for et in table1.embedded_tables:
        print(et)