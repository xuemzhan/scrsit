from typing import Optional

class Chunk:
    """
    表示文档内容的片段或块。
    """
    def __init__(
        self,
        id: str,
        doc_id: str,
        order_index: int,
        content: str,
        tokens: int,
        vectors: Optional[str] = None,
    ):
        """
        初始化 Chunk 对象。

        Args:
            id (str): 块的唯一标识符。
            doc_id (str): 块所属文档的标识符。
            order_index (int): 块在文档中的顺序。
            content (str): 块的文本内容。
            tokens (int): 块中的 token 数量。
            vectors (Optional[str]): 块的向量表示。
        """
        self.id = id
        self.doc_id = doc_id
        self.order_index = order_index
        self.content = content
        self.tokens = tokens
        self.vectors = vectors

    def embedding(self) -> str:
        """
        为块生成嵌入向量。

        Returns:
            str: 嵌入向量。
        """
        # TODO: 替换为实际的嵌入逻辑
        return f"Embedding for chunk {self.id}"

    def __repr__(self) -> str:
        return f"Chunk(id='{self.id}', order_index={self.order_index}, content='{self.content[:20]}...')"