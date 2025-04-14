# src/scrsit/core/interfaces/base_vector_store.py
import abc
from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel # 用于定义结果类

from src.scrsit.core.document.models import Chunk # 通常存储 Chunk 的 Embedding

class VectorStoreQueryResult(BaseModel):
    """向量存储查询结果的单项。"""
    chunk: Chunk             # 相关的 Chunk 对象
    similarity: float        # 与查询向量的相似度得分

class BaseVectorStore(abc.ABC):
    """
    向量存储接口定义。
    负责存储、检索和管理向量 Embedding 及其关联的元数据（通常是 Chunk）。
    """
    @abc.abstractmethod
    def add_embeddings(self, chunks: List[Chunk], embeddings: List[List[float]], **kwargs) -> List[str]:
        """
        添加 Chunks 及其对应的 Embeddings 到向量存储。

        Args:
            chunks (List[Chunk]): 需要存储的 Chunk 对象列表。Chunk 对象应包含 id, doc_id 和 content。
            embeddings (List[List[float]]): 与 Chunks 对应的 Embedding 向量列表。
            **kwargs: 特定于存储后端的参数。

        Returns:
            List[str]: 成功添加的 Chunk 的 ID 列表。

        Raises:
            StorageError: 如果添加失败。
            ValueError: 如果 chunks 和 embeddings 列表长度不匹配。
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks 和 Embeddings 列表的长度必须匹配。")
        pass

    @abc.abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5, filter: Optional[Dict[str, Any]] = None, **kwargs) -> List[VectorStoreQueryResult]:
        """
        根据查询向量进行相似性搜索。

        Args:
            query_embedding (List[float]): 用于查询的 Embedding 向量。
            top_k (int): 返回最相似结果的数量。
            filter (Optional[Dict[str, Any]]): 用于过滤结果的元数据条件 (例如: {"doc_id": "some_doc_id"})。
                                                过滤条件的格式依赖于具体实现。
            **kwargs: 特定于存储后端的参数。

        Returns:
            List[VectorStoreQueryResult]: 查询结果列表，按相似度降序排列。

        Raises:
            StorageError: 如果搜索失败。
        """
        pass

    @abc.abstractmethod
    def delete_by_ids(self, chunk_ids: List[str], **kwargs) -> bool:
        """
        根据 Chunk ID 列表删除对应的向量和元数据。

        Args:
            chunk_ids (List[str]): 要删除的 Chunk ID 列表。
            **kwargs: 特定于存储后端的参数。

        Returns:
            bool: 操作是否成功 (可能部分成功，具体行为依赖实现)。

        Raises:
            StorageError: 如果删除过程中发生错误。
        """
        pass

    def delete_by_doc_id(self, doc_id: str, **kwargs) -> bool:
        """
        删除属于特定文档 ID 的所有向量和元数据 (可选)。

        Args:
            doc_id (str): 要删除其关联数据的文档 ID。
            **kwargs: 特定于存储后端的参数。

        Returns:
            bool: 操作是否成功。

        Raises:
            StorageError: 如果删除过程中发生错误。
            NotImplementedError: 如果子类不支持此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 delete_by_doc_id 方法。")