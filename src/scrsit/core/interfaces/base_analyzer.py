# src/scrsit/core/interfaces/base_analyzer.py
import abc
from typing import List, Union, Dict, Any

from src.scrsit.core.document.models import Document, Chunk, Entity, Relationship # 等分析结果

AnalysisResult = Union[List[Entity], List[Relationship], Dict[str, Any]] # 可扩展

class BaseAnalyzer(abc.ABC):
    """
    内容分析器接口定义。
    负责从文档或块中提取信息，如实体、关系、关键词等。
    """
    @abc.abstractmethod
    def analyze(self, content: Union[Document, Chunk, str], **kwargs) -> AnalysisResult:
        """
        分析给定的内容。

        Args:
            content (Union[Document, Chunk, str]): 需要分析的内容对象或文本。
            **kwargs: 其他特定于分析器的参数 (例如, prompt 模板, 提取目标)。

        Returns:
            AnalysisResult: 分析结果。具体类型取决于分析器的功能 (例如, 返回实体列表)。
                           建议返回 Pydantic 模型实例或其列表。

        Raises:
            AnalysisError: 如果分析过程中发生错误。
        """
        pass

    @property
    @abc.abstractmethod
    def analysis_type(self) -> str:
        """
        返回该分析器执行的分析类型 (例如, "entity_extraction", "keyword_extraction")。
        """
        pass