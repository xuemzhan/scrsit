from typing import Optional

class Element:
    """
    表示文档中的通用元素。
    """
    def __init__(
        self,
        id: str,
        doc_id: str,
        chunk_id: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        vectors: Optional[str] = None,
    ):
        """
        初始化 Element 对象。

        Args:
            id (str): 元素的唯一标识符。
            doc_id (str): 元素所属文档的标识符。
            chunk_id (Optional[str]): 元素所属块的标识符。
            name (Optional[str]): 元素的名称。
            content (Optional[str]): 元素的内容（base64 编码）。
            description (Optional[str]): 元素的描述。
            vectors (Optional[str]): 元素的向量表示。
        """
        self.id = id
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.name = name
        self.content = content
        self.description = description
        self.vectors = vectors

    def embedding(self) -> str:
        """
        为元素生成嵌入向量。

        Returns:
            str: 嵌入向量。
        """
        # TODO: 替换为实际的嵌入逻辑
        return f"Embedding for element {self.id}"

    def __repr__(self) -> str:
        return f"Element(id='{self.id}', name='{self.name}')"