# src/scrsit/core/interfaces/base_document_store.py
import abc
from typing import Optional, List

from src.scrsit.core.document.models import Document

class BaseDocumentStore(abc.ABC):
    """
    文档存储接口定义。
    负责持久化和检索完整的 Document 对象。
    """
    @abc.abstractmethod
    def save(self, document: Document, **kwargs) -> None:
        """
        保存或更新一个文档对象。

        Args:
            document (Document): 要保存的文档对象。
            **kwargs: 特定于存储后端的参数。

        Raises:
            StorageError: 如果保存失败。
        """
        pass

    def save_batch(self, documents: List[Document], **kwargs) -> None:
        """
        批量保存或更新文档对象 (可选优化)。

        Args:
            documents (List[Document]): 要保存的文档对象列表。
            **kwargs: 特定于存储后端的参数。

        Raises:
            StorageError: 如果保存失败。
            NotImplementedError: 如果子类不支持批处理。
        """
        # 默认实现是逐个调用 save
        for doc in documents:
            self.save(doc, **kwargs)


    @abc.abstractmethod
    def get(self, doc_id: str, **kwargs) -> Optional[Document]:
        """
        根据 ID 检索单个文档对象。

        Args:
            doc_id (str): 要检索的文档 ID。
            **kwargs: 特定于存储后端的参数。

        Returns:
            Optional[Document]: 找到的文档对象，如果不存在则返回 None。

        Raises:
            StorageError: 如果检索失败。
        """
        pass

    def get_batch(self, doc_ids: List[str], **kwargs) -> List[Optional[Document]]:
        """
        根据 ID 列表批量检索文档对象 (可选优化)。

        Args:
            doc_ids (List[str]): 要检索的文档 ID 列表。
            **kwargs: 特定于存储后端的参数。

        Returns:
            List[Optional[Document]]: 找到的文档对象列表，顺序与输入 ID 对应，
                                      对于不存在的 ID，对应位置为 None。

        Raises:
            StorageError: 如果检索失败。
            NotImplementedError: 如果子类不支持批处理。
        """
        # 默认实现是逐个调用 get
        return [self.get(doc_id, **kwargs) for doc_id in doc_ids]


    @abc.abstractmethod
    def delete(self, doc_id: str, **kwargs) -> bool:
        """
        根据 ID 删除单个文档对象。

        Args:
            doc_id (str): 要删除的文档 ID。
            **kwargs: 特定于存储后端的参数。

        Returns:
            bool: 如果成功删除则返回 True，如果文档不存在或删除失败则返回 False。

        Raises:
            StorageError: 如果删除过程中发生非预期的存储错误。
        """
        pass

    def delete_batch(self, doc_ids: List[str], **kwargs) -> int:
        """
        根据 ID 列表批量删除文档对象 (可选优化)。

        Args:
            doc_ids (List[str]): 要删除的文档 ID 列表。
            **kwargs: 特定于存储后端的参数。

        Returns:
            int: 成功删除的文档数量。

        Raises:
            StorageError: 如果删除过程中发生非预期的存储错误。
            NotImplementedError: 如果子类不支持批处理。
        """
        # 默认实现是逐个调用 delete
        count = 0
        for doc_id in doc_ids:
            if self.delete(doc_id, **kwargs):
                count += 1
        return count

    # 可以添加其他查询方法，例如根据 metadata 查询等
    def find(self, query: Dict[str, Any], **kwargs) -> List[Document]:
        """
        根据查询条件查找文档 (可选)。

        Args:
            query (Dict[str, Any]): 查询条件字典 (例如: {"metadata.author": "John Doe"})。
            **kwargs: 特定于存储后端的参数 (例如: limit, skip)。

        Returns:
            List[Document]: 匹配查询条件的文档列表。

        Raises:
            StorageError: 如果查询失败。
            NotImplementedError: 如果子类不支持此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 find 方法。")

from src.scrsit.core.exceptions import StorageError # 导入共享的异常类