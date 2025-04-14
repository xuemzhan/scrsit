# src/scrsit/core/interfaces/base_structured_store.py
import abc
from typing import List, Dict, Any, Optional

# 可以定义具体的结构化数据模型，或者使用通用字典
StructuredData = Dict[str, Any]

class BaseStructuredStore(abc.ABC):
    """
    结构化数据存储接口定义。
    用于存储和查询分析结果、元数据、关系等结构化信息 (例如，存储 Entities, Relationships)。
    """
    @abc.abstractmethod
    def save(self, collection: str, data: StructuredData, **kwargs) -> str:
        """
        保存一条结构化数据记录到指定的集合/表中。

        Args:
            collection (str): 目标集合或表的名称 (例如 "entities", "relationships")。
            data (StructuredData): 要保存的数据记录 (通常是字典或 Pydantic 模型)。
                                   应包含一个唯一标识符字段 (如 'id') 或由存储自动生成。
            **kwargs: 特定于存储后端的参数。

        Returns:
            str: 保存记录的唯一 ID。

        Raises:
            StorageError: 如果保存失败。
        """
        pass

    def save_batch(self, collection: str, data_list: List[StructuredData], **kwargs) -> List[str]:
        """
        批量保存结构化数据记录 (可选优化)。

        Args:
            collection (str): 目标集合或表的名称。
            data_list (List[StructuredData]): 要保存的数据记录列表。
            **kwargs: 特定于存储后端的参数。

        Returns:
            List[str]: 成功保存记录的 ID 列表。

        Raises:
            StorageError: 如果保存失败。
            NotImplementedError: 如果子类不支持批处理。
        """
        # 默认实现是逐个调用 save
        return [self.save(collection, data, **kwargs) for data in data_list]

    @abc.abstractmethod
    def get(self, collection: str, record_id: str, **kwargs) -> Optional[StructuredData]:
        """
        根据 ID 从指定集合/表中检索单条记录。

        Args:
            collection (str): 目标集合或表的名称。
            record_id (str): 要检索的记录 ID。
            **kwargs: 特定于存储后端的参数。

        Returns:
            Optional[StructuredData]: 找到的记录，如果不存在则返回 None。

        Raises:
            StorageError: 如果检索失败。
        """
        pass

    @abc.abstractmethod
    def find(self, collection: str, query: Dict[str, Any], **kwargs) -> List[StructuredData]:
        """
        根据查询条件从指定集合/表中查找记录。

        Args:
            collection (str): 目标集合或表的名称。
            query (Dict[str, Any]): 查询条件字典 (格式依赖于具体实现)。
            **kwargs: 特定于存储后端的参数 (例如: limit, sort)。

        Returns:
            List[StructuredData]: 匹配查询条件的记录列表。

        Raises:
            StorageError: 如果查询失败。
        """
        pass

    @abc.abstractmethod
    def update(self, collection: str, record_id: str, updates: Dict[str, Any], **kwargs) -> bool:
        """
        更新指定集合/表中 ID 对应的记录。

        Args:
            collection (str): 目标集合或表的名称。
            record_id (str): 要更新的记录 ID。
            updates (Dict[str, Any]): 要更新的字段及其新值。
            **kwargs: 特定于存储后端的参数。

        Returns:
            bool: 如果成功更新则返回 True，如果记录不存在或更新失败则返回 False。

        Raises:
            StorageError: 如果更新过程中发生错误。
        """
        pass

    @abc.abstractmethod
    def delete(self, collection: str, record_id: str, **kwargs) -> bool:
        """
        删除指定集合/表中 ID 对应的记录。

        Args:
            collection (str): 目标集合或表的名称。
            record_id (str): 要删除的记录 ID。
            **kwargs: 特定于存储后端的参数。

        Returns:
            bool: 如果成功删除则返回 True，如果记录不存在或删除失败则返回 False。

        Raises:
            StorageError: 如果删除过程中发生错误。
        """
        pass