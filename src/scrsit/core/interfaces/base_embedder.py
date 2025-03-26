# src/scrsit/core/interfaces/base_embedder.py
import abc
from typing import List, Union

from src.scrsit.core.document.models import Chunk, Document, Entity # 等需要 Embedding 的对象

EmbeddableContentType = Union[str, List[str], Chunk, List[Chunk], Document] # 可扩展

class BaseEmbedder(abc.ABC):
    """
    Embedding 生成器接口定义。
    负责为文本或其他内容生成向量表示。
    """
    @abc.abstractmethod
    def embed(self, content: EmbeddableContentType, **kwargs) -> Union[List[float], List[List[float]]]:
        """
        为输入内容生成 Embedding。

        Args:
            content (EmbeddableContentType): 需要生成 Embedding 的内容。
                                            可以是单个字符串、字符串列表、Chunk、Chunk列表等。
            **kwargs: 其他特定于 Embedding 模型的参数。

        Returns:
            Union[List[float], List[List[float]]]:
                - 如果输入是单个内容，返回单个 Embedding 向量。
                - 如果输入是列表，返回 Embedding 向量的列表，顺序与输入对应。

        Raises:
            EmbeddingError: 如果生成 Embedding 过程中发生错误。
        """
        pass

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """
        返回 Embedding 向量的维度。
        """
        pass