from typing import Optional

from .base.structured_content import StructuredContent

class Table:
    """
    表示文档中的表格。
    """
    def __init__(
        self,
        order_index: int,
        content: str,
        structured_content: Optional[StructuredContent] = None,
    ):
        """
        初始化 Table 对象。

        Args:
            order_index (int): 表格在文档中的顺序。
            content (str): 表格的文本内容。
            structured_content (Optional[StructuredContent]): 表格内容的结构化表示。
        """
        self.order_index = order_index
        self.content = content
        self.structured_content = structured_content

    def __repr__(self) -> str:
        return f"Table(order_index={self.order_index}, content='{self.content[:20]}...')"