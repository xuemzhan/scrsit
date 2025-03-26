# src/scrsit/core/interfaces/base_reviewer.py
import abc
from typing import Dict, Any

from src.scrsit.core.document.models import Document # 或其他表示需求的数据结构

class ReviewResult(BaseModel):
    """评审结果的数据模型。"""
    is_complete: bool = True         # 需求是否完整
    is_consistent: bool = True       # 需求内部是否一致
    is_clear: bool = True            # 需求是否清晰无歧义
    potential_issues: List[str] = Field(default_factory=list) # 发现的潜在问题描述列表
    suggestions: List[str] = Field(default_factory=list)    # 改进建议列表
    score: Optional[float] = None    # 综合评分 (可选)

class BaseReviewer(abc.ABC):
    """
    需求评审器接口定义。
    负责根据特定规则或模型评审需求的质量（完整性、一致性、清晰度等）。
    """
    @abc.abstractmethod
    def review(self, requirement_data: Union[Document, Dict[str, Any]], criteria: Dict[str, Any] = None, **kwargs) -> ReviewResult:
        """
        评审给定的需求数据。

        Args:
            requirement_data (Union[Document, Dict[str, Any]]): 待评审的需求数据，可以是 Document 对象或包含需求信息的字典。
            criteria (Dict[str, Any], optional): 评审标准或规则。
            **kwargs: 特定于评审器的参数。

        Returns:
            ReviewResult: 包含评审结果的对象。

        Raises:
            WorkflowError: 如果评审过程中发生错误。
        """
        pass

from src.scrsit.core.exceptions import WorkflowError
from pydantic import BaseModel, Field
from typing import List, Optional, Union