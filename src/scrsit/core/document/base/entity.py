import uuid
from typing import Optional, Dict

from element import Element  # 确保导入路径正确

class Entity(Element):
    """
    表示从文档中提取的实体，同时继承自 Element 类以获得通用属性。
    """
    def __init__(
        self,
        id: Optional[str],
        doc_id: str,
        name: str,
        type: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
        vectors: Optional[str] = None,
        sources: Optional[Dict[str, str]] = None,
    ):
        """
        初始化 Entity 对象。

        Args:
            id (Optional[str]): 实体的唯一标识符，若为 None 则自动生成。
            doc_id (str): 实体所属文档的标识符。
            name (str): 实体的名称。
            type (str): 实体的类型（例如 "Low", "Neutral", "High"）。
            content (Optional[str]): 组件的内容。
            description (Optional[str]): 实体的描述。
            vectors (Optional[str]): 实体的向量表示。
            sources (Optional[Dict[str, str]]): 实体所在文档 ID 到块 ID 的映射。
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
        self.type = type
        self.sources = sources if sources is not None else {}

    def embedding(self) -> str:
        """
        为实体生成嵌入向量。
        
        Returns:
            str: 嵌入向量示例。
        """
        # TODO: 替换为实际的嵌入计算逻辑
        return f"Embedding for entity {self.id} of type {self.type}"

    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', name='{self.name}', type='{self.type}')"


if __name__ == "__main__":
    # 测试用例

    # 用例1：提供所有参数
    entity1 = Entity(
        id="entity-1",
        doc_id="doc-001",
        name="Test Entity 1",
        type="High",
        content="This is the content of entity one.",
        description="描述信息",
        vectors="vector_data_1",
        sources={"doc-001": "chunk-001"}
    )

    # 用例2：自动生成 id，部分参数使用默认值
    entity2 = Entity(
        id=None,
        doc_id="doc-002",
        name="Test Entity 2",
        type="Low",
        content="Content of entity two."
    )

    print("实体示例：")
    print(entity1)
    print(entity2)
    print(f"Embedding for entity1: {entity1.embedding()}")
    print(f"Embedding for entity2: {entity2.embedding()}")