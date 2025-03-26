# src/scrsit/core/interfaces/base_parser.py
import abc
from typing import Union, IO, List

from src.scrsit.core.document.models import Document

class BaseParser(abc.ABC):
    """
    文档解析器接口定义。
    负责将不同格式的原始文档文件解析为统一的 Document 对象。
    """
    @abc.abstractmethod
    def parse(self, file_source: Union[str, IO[bytes]], **kwargs) -> Document:
        """
        解析给定的文件源。

        Args:
            file_source (Union[str, IO[bytes]]): 文件路径字符串或文件对象的二进制IO流。
            **kwargs: 其他特定于解析器的参数 (例如，密码、OCR选项)。

        Returns:
            Document: 解析后的核心文档对象。

        Raises:
            ParsingError: 如果解析过程中发生错误。
            FileNotFoundError: 如果 file_source 是路径且文件不存在。
            TypeError: 如果 file_source 类型不支持。
        """
        pass

    @property
    @abc.abstractmethod
    def supported_types(self) -> List[str]:
        """
        返回该解析器支持的文件类型扩展名列表 (小写, 例如 ['pdf', 'docx'])。
        """
        pass