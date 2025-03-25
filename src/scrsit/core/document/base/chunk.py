import re
import uuid
from typing import List, Optional

from element import Element  # 确保导入路径正确

class Chunk(Element):
    """
    表示文档内容的片段或块。
    """
    def __init__(
        self,
        id: Optional[str],
        doc_id: str,
        order_index: int,
        content: str,
        tokens: int,
        vectors: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        初始化 Chunk 对象。

        Args:
            id (Optional[str]): 块的唯一标识符，若为 None 则自动生成。
            doc_id (str): 块所属文档的标识符。
            order_index (int): 块在文档中的顺序。
            content (str): 块的文本内容，不允许为空。
            tokens (int): 块中的 token 数量。
            vectors (Optional[str]): 块的向量表示。
            name (Optional[str]): 块的名称。
        """
        if not content:
            raise ValueError("Chunk content cannot be empty.")
        if id is None:
            id = str(uuid.uuid4())
        # 调用父类 Element 的构造方法以初始化通用属性
        super().__init__(
            id=id,
            doc_id=doc_id,
            chunk_id=None,
            name=name,
            content=content,
            description=None,
            vectors=vectors,
        )
        self.order_index = order_index
        self.tokens = tokens

    def embedding(self) -> str:
        """
        为块生成嵌入向量。
        
        Returns:
            str: 嵌入向量示例。
        """
        # TODO: 替换为实际的嵌入逻辑
        return f"Embedding for chunk {self.id}"

    def __repr__(self) -> str:
        return (
            f"Chunk(id='{self.id}', order_index={self.order_index}, "
            f"tokens={self.tokens}, content='{self.content[:20]}...')"
        )

    def segment_by_semantics(self) -> List['Chunk']:
        """
        根据语义（句子结束符）切分文本，此处采用简单的正则分句方法。

        Returns:
            List[Chunk]: 按句子切分后的 Chunk 列表
        """
        # 简单按照句子结束符（中文符号或英文标点）切分
        sentences = re.split(r'(?<=[。！？.!?])\s+', self.content)
        chunks = []
        for idx, sent in enumerate(sentences, start=1):
            sent = sent.strip()
            if sent:
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    doc_id=self.doc_id,
                    order_index=self.order_index * 100 + idx,
                    content=sent,
                    tokens=len(sent.split()),
                    vectors=self.vectors,
                    name=self.name
                )
                chunks.append(chunk)
        return chunks

    def segment_by_paragraph(self) -> List['Chunk']:
        """
        根据段落切分文本，以换行符为分隔符。

        Returns:
            List[Chunk]: 按段落切分后的 Chunk 列表
        """
        paragraphs = [p.strip() for p in self.content.split("\n") if p.strip()]
        chunks = []
        for idx, para in enumerate(paragraphs, start=1):
            chunk = Chunk(
                id=str(uuid.uuid4()),
                doc_id=self.doc_id,
                order_index=self.order_index * 100 + idx,
                content=para,
                tokens=len(para.split()),
                vectors=self.vectors,
                name=self.name
            )
            chunks.append(chunk)
        return chunks

    def segment_by_token_count(self, max_tokens: int) -> List['Chunk']:
        """
        按给定的 token 数量切分文本。Token 此处按空格拆分。

        Args:
            max_tokens (int): 每个子块的最大 token 数量

        Returns:
            List[Chunk]: 按 token 数切分后的 Chunk 列表
        """
        words = self.content.split()
        chunks = []
        for idx in range(0, len(words), max_tokens):
            # 组合出一个文本块
            chunk_content = " ".join(words[idx:idx + max_tokens])
            chunk = Chunk(
                id=str(uuid.uuid4()),
                doc_id=self.doc_id,
                order_index=self.order_index * 100 + (idx // max_tokens) + 1,
                content=chunk_content,
                tokens=len(chunk_content.split()),
                vectors=self.vectors,
                name=self.name
            )
            chunks.append(chunk)
        return chunks

    def adaptive_segmentation(self, token_threshold: int = 50) -> List['Chunk']:
        """
        自适应切分文本。若文本中包含换行符，则优先采用段落切分；否则，
        若 token 数超过给定阈值，则按 token 数切分；否则采用语义切分。

        Args:
            token_threshold (int): 判定文本较长的 token 阈值

        Returns:
            List[Chunk]: 自适应切分后的 Chunk 列表
        """
        if "\n" in self.content:
            return self.segment_by_paragraph()
        elif len(self.content.split()) > token_threshold:
            return self.segment_by_token_count(token_threshold)
        else:
            return self.segment_by_semantics()


if __name__ == "__main__":
    # 测试用例

    # 原始文本示例（多句、带段落）
    text = (
        "这是第一句。这是第二句！这是第三句？\n"
        "这是新的段落，具有第一句。这里继续第二句。\n"
        "最后一段，没有换行符，只有一句话。"
    )

    # 创建一个 Chunk
    original_chunk = Chunk(
        id=None,
        doc_id="doc-1",
        order_index=1,
        content=text,
        tokens=len(text.split()),
        name="Test Chunk"
    )

    print("原始 Chunk:")
    print(original_chunk)
    print("\n按照语义切分（句子）：")
    for c in original_chunk.segment_by_semantics():
        print(c)

    print("\n按照段落切分：")
    for c in original_chunk.segment_by_paragraph():
        print(c)

    print("\n按照 token 数切分，每块不超过 10 tokens：")
    for c in original_chunk.segment_by_token_count(10):
        print(c)

    print("\n自适应切分：")
    for c in original_chunk.adaptive_segmentation(token_threshold=20):
        print(c)