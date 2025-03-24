from typing import Optional

class Picture:
    """
    表示文档中的图像或图片。
    """
    def __init__(
        self,
        id: str,
        doc_id: str,
        chunk_id: Optional[str] = None,
        order_index: Optional[int] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        vectors: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        size: Optional[int] = None,
    ):
        """
        初始化 Picture 对象。

        Args:
            id (str): 图片的唯一标识符。
            doc_id (str): 图片所属文档的标识符。
            chunk_id (Optional[str]): 图片所属块的标识符。
            order_index (Optional[int]): 图片在文档中的顺序。
            name (Optional[str]): 图片的名称或文件名。
            content (Optional[str]): 图片的内容（base64 编码）。
            description (Optional[str]): 图片的描述。
            vectors (Optional[str]): 图片的向量表示。
            width (Optional[int]): 图片的宽度（像素）。
            height (Optional[int]): 图片的高度（像素）。
            size (Optional[int]): 图片的大小（字节）。
        """
        self.id = id
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.order_index = order_index
        self.name = name
        self.content = content
        self.description = description
        self.vectors = vectors
        self.width = width
        self.height = height
        self.size = size

    def embedding(self) -> str:
        """
        为图片生成嵌入向量。

        Returns:
            str: 嵌入向量。
        """
        # TODO: 替换为实际的嵌入逻辑
        return f"Embedding for picture {self.id}"

    def __repr__(self) -> str:
        return f"Picture(id='{self.id}', name='{self.name}')"