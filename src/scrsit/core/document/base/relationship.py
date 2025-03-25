import uuid
from typing import Optional, List, Dict

from element import Element  # 确保导入路径正确

class Relationship(Element):
    """
    表示文档中两个实体之间的关系，同时继承自 Element 类以获得通用属性。
    除了通用属性外，Relationship 记录了源实体、目标实体、权重、关键字等信息。
    """
    def __init__(
        self,
        id: Optional[str],
        doc_id: str,
        from_entity_id: str,
        to_entity_id: str,
        weight: Optional[int] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        sources: Optional[Dict[str, str]] = None,
    ):
        """
        初始化 Relationship 对象。

        Args:
            id (Optional[str]): 关系的唯一标识符，若为 None 则自动生成。
            doc_id (str): 关系所属文档的标识符。
            from_entity_id (str): 源实体的标识符。
            to_entity_id (str): 目标实体的标识符。
            weight (Optional[int]): 关系的权重或强度。
            description (Optional[str]): 关系的描述信息，传递给 Element.description。
            keywords (Optional[List[str]]): 与关系关联的关键字列表。
            sources (Optional[Dict[str, str]]): 关系所在文档 ID 到块 ID 的映射。
        """
        if id is None:
            id = str(uuid.uuid4())
        # 设定默认名称为 "Rel(from->to)"
        name = f"Rel({from_entity_id}->{to_entity_id})"
        # 调用父类 Element 初始化通用属性
        super().__init__(
            id=id,
            doc_id=doc_id,
            chunk_id=None,
            name=name,
            content=None,
            description=description,
            vectors=None,
        )
        self.from_entity_id = from_entity_id
        self.to_entity_id = to_entity_id
        self.weight = weight
        self.keywords = keywords if keywords is not None else []
        self.sources = sources if sources is not None else {}

    def embedding(self) -> str:
        """
        为关系生成嵌入向量。

        Returns:
            str: 嵌入向量示例。
        """
        # TODO: 替换为实际的嵌入计算逻辑
        return f"Embedding for relationship {self.id}"

    def __repr__(self) -> str:
        return (
            f"Relationship(id='{self.id}', from_entity_id='{self.from_entity_id}', "
            f"to_entity_id='{self.to_entity_id}', weight={self.weight}, keywords={self.keywords})"
        )


if __name__ == "__main__":
    # 测试用例

    # 用例1：提供所有参数（不传入 id 则自动生成）
    rel1 = Relationship(
        id=None,
        doc_id="doc-001",
        from_entity_id="entity-A",
        to_entity_id="entity-B",
        weight=5,
        description="A strong relationship between A and B.",
        keywords=["strong", "A-B"],
        sources={"doc-001": "chunk-001"}
    )

    # 用例2：传入固定 id，缺省部分可选参数
    rel2 = Relationship(
        id="rel-2",
        doc_id="doc-002",
        from_entity_id="entity-X",
        to_entity_id="entity-Y",
        weight=3
    )

    print("Relationship 示例：")
    print(rel1)
    print(rel2)
    print(f"Embedding for rel1: {rel1.embedding()}")
    print(f"Embedding for rel2: {rel2.embedding()}")