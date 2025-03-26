# src/scrsit/core/interfaces/base_chunker.py
import abc
from typing import List

from src.scrsit.core.document.models import Document, Chunk

class BaseChunker(abc.ABC):
    """
    文档分块器接口定义。
    负责将 Document 对象的内容切分成合适的 Chunk 列表。
    """
    @abc.abstractmethod
    def chunk(self, document: Document, **kwargs) -> List[Chunk]:
        """
        将文档内容切分成块。

        Args:
            document (Document): 待分块的文档对象。
            **kwargs: 其他特定于分块策略的参数 (例如, chunk_size, overlap)。

        Returns:
            List[Chunk]: 生成的块列表。这些 Chunk 对象应包含 doc_id 和 order_index。

        Raises:
            WorkflowError: 如果分块过程中发生错误。
        """
        pass