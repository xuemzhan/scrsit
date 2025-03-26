# src/scrsit/core/interfaces/__init__.py
# 插件接口定义包
from src.scrsit.core.interfaces.base_analyzer import BaseAnalyzer
from src.scrsit.core.interfaces.base_chunker import BaseChunker
from src.scrsit.core.interfaces.base_document_store import BaseDocumentStore
from src.scrsit.core.interfaces.base_embedder import BaseEmbedder
from src.scrsit.core.interfaces.base_knowledge_provider import BaseKnowledgeProvider
from src.scrsit.core.interfaces.base_llm_provider import BaseLLMProvider
from src.scrsit.core.interfaces.base_multimodal_provider import BaseMultimodalProvider
from src.scrsit.core.interfaces.base_ocr_provider import BaseOCRProvider
from src.scrsit.core.interfaces.base_parser import BaseParser
from src.scrsit.core.interfaces.base_proposal_generator import BaseProposalGenerator
from src.scrsit.core.interfaces.base_reviewer import BaseReviewer
from src.scrsit.core.interfaces.base_structured_store import BaseStructuredStore
from src.scrsit.core.interfaces.base_vector_store import BaseVectorStore

from typing import Dict, Optional, Any

# 可以定义一个所有插件接口的基类，如果需要统一处理
class BasePluginInterface:
    """所有插件接口的抽象基类 (可选)。"""
    plugin_name: str # 插件的唯一名称

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化插件。

        Args:
            config (Optional[Dict[str, Any]]): 插件特定的配置字典。
        """
        self.config = config or {}

    def validate_config(self) -> bool:
        """
        验证插件配置是否有效 (可选实现)。
        返回 True 表示有效，否则应引发 ConfigurationError。
        """
        return True