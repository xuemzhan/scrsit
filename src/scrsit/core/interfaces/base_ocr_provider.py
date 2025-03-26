# src/scrsit/core/interfaces/base_ocr_provider.py
import abc, logging
from typing import Union, List
from PIL import Image # 使用 PIL 处理图片

from base_llm_provider import ProviderError # 导入共享的异常类

logger = logging.getLogger(__name__)


class BaseOCRProvider(abc.ABC):
    """
    光学字符识别 (OCR) 提供者接口定义。
    负责从图片中提取文本。
    """
    @abc.abstractmethod
    def extract_text(self, image: Union[bytes, str, Image.Image], **kwargs) -> str:
        """
        从单个图片中提取文本。

        Args:
            image (Union[bytes, str, Image.Image]): 图片的二进制数据、文件路径或 PIL Image 对象。
            **kwargs: OCR 提供者的特定参数 (例如, language)。

        Returns:
            str: 提取出的文本内容。

        Raises:
            ProviderError: 如果 OCR 处理失败。
        """
        pass

    def extract_text_batch(self, images: List[Union[bytes, str, Image.Image]], **kwargs) -> List[str]:
        """
        从一批图片中提取文本 (可选优化)。

        Args:
            images (List[Union[bytes, str, Image.Image]]): 图片列表。
            **kwargs: OCR 提供者的特定参数。

        Returns:
            List[str]: 提取出的文本列表，顺序与输入图片对应。

        Raises:
            ProviderError: 如果 OCR 处理失败。
            NotImplementedError: 如果子类不支持批处理。
        """
        # 默认实现是逐个调用 extract_text
        results = []
        for img in images:
            try:
                results.append(self.extract_text(img, **kwargs))
            except Exception as e:
                # 根据需要决定是记录错误继续，还是直接抛出
                logging.error(f"处理图片时出错: {e}", exc_info=True)
                results.append("") # 或抛出异常
        return results

