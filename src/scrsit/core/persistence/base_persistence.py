# src/scrsit/core/persistence/base_persistence.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class StructuredDatabase(ABC):
    """结构化数据库的抽象基类。"""

    @abstractmethod
    def connect(self) -> None:
        """连接到数据库。"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开与数据库的连接。"""
        pass

    @abstractmethod
    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行 SQL 查询。"""
        pass

    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        """插入数据到指定的表。"""
        pass

    @abstractmethod
    def fetch_one(self, table_name: str, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """查询单条数据。"""
        pass

    @abstractmethod
    def fetch_all(self, table_name: str, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """查询所有数据。"""
        pass

class UnstructuredDatabase(ABC):
    """非结构化数据库的抽象基类。"""

    @abstractmethod
    def connect(self) -> None:
        """连接到数据库。"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开与数据库的连接。"""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """根据键获取数据。"""
        pass

    @abstractmethod
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """设置键值对。"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """根据键删除数据。"""
        pass

    @abstractmethod
    def all(self) -> List[Dict[str, Any]]:
        """获取所有数据。"""
        pass

class VectorDatabase(ABC):
    """向量数据库的抽象基类。"""

    @abstractmethod
    def connect(self) -> None:
        """连接到数据库。"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开与数据库的连接。"""
        pass

    @abstractmethod
    def add(self, ids: List[str], vectors: List[List[float]], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """添加向量和元数据。"""
        pass

    @abstractmethod
    def query(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """查询最相似的向量。"""
        pass

    @abstractmethod
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """根据 ID 获取向量和元数据。"""
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """根据 ID 删除向量。"""
        pass