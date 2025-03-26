# src/scrsit/core/interfaces/base_multimodal_provider.py
import abc
from typing import List, Dict, Any, Union

# 定义多模态输入类型 (示例)
MultimodalInput = List[Dict[str, Union[str, bytes]]] # 例如 [{'type': 'text', 'content': '...'}, {'type': 'image', 'content': b'...'}]

class BaseMultimodalProvider(abc.ABC):
    """
    多模态模型提供者接口定义。
    处理包含多种类型内容（如文本和图像）的输入。
    """
    @abc.abstractmethod
    def process(self, inputs: MultimodalInput, **kwargs) -> Any:
        """
        处理多模态输入并返回结果。

        Args:
            inputs (MultimodalInput): 包含不同类型内容（文本、图像等）的输入列表。
                                     格式需要根据具体模型约定。
            **kwargs: 模型特定的参数 (例如, prompt, 输出格式要求)。

        Returns:
            Any: 模型的输出结果 (例如, 生成的文本、分析结果字典等)。

        Raises:
            ProviderError: 如果处理失败。
        """
        pass

    @abc.abstractmethod
    async def aprocess(self, inputs: MultimodalInput, **kwargs) -> Any:
        """异步版本的 process。"""
        pass

from base_llm_provider import ProviderError # 导入共享的异常类