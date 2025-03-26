# src/scrsit/core/interfaces/base_knowledge_provider.py
import abc
from typing import List, Dict, Any

class BaseKnowledgeProvider(abc.ABC):
    """
    知识提供者接口定义。
    用于访问和查询领域知识、行业规范、合规规则等。
    """
    @abc.abstractmethod
    def query(self, topic: str, context: Dict[str, Any] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        根据主题和上下文查询相关知识。

        Args:
            topic (str): 查询的主题或问题。
            context (Dict[str, Any], optional): 提供额外的上下文信息以辅助查询。
            **kwargs: 特定于知识库的查询参数。

        Returns:
            List[Dict[str, Any]]: 返回的相关知识片段或文档列表，每个包含内容和元数据。
                                  例如: [{'content': '...', 'source': 'Rulebook v1.2', 'score': 0.9}]

        Raises:
            ProviderError: 如果查询知识库失败。
        """
        pass

from src.scrsit.core.interfaces.base_llm_provider import ProviderError # 导入共享的异常类