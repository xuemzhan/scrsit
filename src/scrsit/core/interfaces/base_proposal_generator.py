# src/scrsit/core/interfaces/base_proposal_generator.py
import abc
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.scrsit.core.document.models import Document # 或其他表示需求的数据结构

class ChangeProposal(BaseModel):
    """变更提议的数据模型。"""
    description: str               # 变更的描述
    reason: str                    # 变更的原因
    impact: Optional[str] = None   # 变更可能产生的影响
    suggested_change: str          # 建议的具体修改内容
    source_location: Optional[str] = None # 变更涉及的原始需求位置 (例如文档页码、章节)

class BaseProposalGenerator(abc.ABC):
    """
    变更提议生成器接口定义。
    根据评审结果或需求差异，生成具体的修改建议。
    """
    @abc.abstractmethod
    def generate_proposals(self, context: Dict[str, Any], **kwargs) -> List[ChangeProposal]:
        """
        生成变更提议。

        Args:
            context (Dict[str, Any]): 生成提议所需的上下文信息。
                                      可能包括原始需求、评审结果、差异分析报告等。
            **kwargs: 特定于生成器的参数。

        Returns:
            List[ChangeProposal]: 生成的变更提议列表。

        Raises:
            WorkflowError: 如果生成提议过程中发生错误。
        """
        pass

from src.scrsit.core.exceptions import WorkflowError
