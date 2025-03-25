import uuid
from typing import Optional

from element import Element  # 确保导入路径正确

class Picture(Element):
    """
    表示文档中的图像或图片，同时继承自 Element 类以获得通用属性。
    """
    def __init__(
        self,
        id: Optional[str],
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
            id (Optional[str]): 图片的唯一标识符，若为 None 则自动生成。
            doc_id (str): 图片所属文档的标识符。
            chunk_id (Optional[str]): 图片所属块的标识符。
            order_index (Optional[int]): 图片在文档中的顺序。
            name (Optional[str]): 图片的名称或文件名。
            content (Optional[str]): 图片的内容（如 base64 编码）。
            description (Optional[str]): 图片的描述。
            vectors (Optional[str]): 图片的向量表示。
            width (Optional[int]): 图片的宽度（像素）。
            height (Optional[int]): 图片的高度（像素）。
            size (Optional[int]): 图片的大小（字节）。
        """
        if id is None:
            id = str(uuid.uuid4())
        # 使用父类 Element 初始化通用属性
        super().__init__(
            id=id,
            doc_id=doc_id,
            chunk_id=chunk_id,
            name=name,
            content=content,
            description=description,
            vectors=vectors,
        )
        self.order_index = order_index
        self.width = width
        self.height = height
        self.size = size

    def embedding(self) -> str:
        """
        为图片生成嵌入向量。

        Returns:
            str: 嵌入向量示例。
        """
        # TODO: 替换为实际的图片嵌入逻辑
        return f"Embedding for picture {self.id}"

    def __repr__(self) -> str:
        return f"Picture(id='{self.id}', name='{self.name}', size={self.size})"


if __name__ == "__main__":
    # 测试用例

    # 用例1：提供全部参数
    picture1 = Picture(
        id="pic-1",
        doc_id="doc-001",
        chunk_id="chunk-001",
        order_index=1,
        name="sample_image_1.png",
        content="base64_image_data",
        description="Sample image number one",
        vectors="vector_data_pic1",
        width=1920,
        height=1080,
        size=204800,
    )

    # 用例2：自动生成 id，仅提供必要参数
    picture2 = Picture(
        id=None,
        doc_id="doc-002",
        name="sample_image_2.jpg",
    )

    print("图片示例：")
    print(picture1)
    print(picture2)
    print(f"Picture1 嵌入向量: {picture1.embedding()}")
    print(f"Picture2 嵌入向量: {picture2.embedding()}")