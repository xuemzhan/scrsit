# src/scrsit/core/interfaces/base_llm_provider.py
import abc
from typing import List, Dict, Any, AsyncGenerator, Generator

class BaseLLMProvider(abc.ABC):
    """
    大型语言模型 (LLM) 提供者接口定义。
    封装与 LLM API 或本地模型的交互。
    """

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        使用给定的 prompt 生成文本。

        Args:
            prompt (str): 输入给 LLM 的提示。
            **kwargs: LLM 的特定参数 (例如, temperature, max_tokens, model_name)。

        Returns:
            str: LLM 生成的文本响应。

        Raises:
            ProviderError: 如果与 LLM 交互失败。
        """
        pass

    @abc.abstractmethod
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """异步版本的 generate。"""
        pass

    # --- 可选的更高级接口 ---

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        进行多轮对话。

        Args:
            messages (List[Dict[str, str]]): 对话历史，通常是 [{'role': 'user'/'assistant', 'content': '...'}, ...]。
            **kwargs: LLM 的特定参数。

        Returns:
            str: LLM 的回复。

        Raises:
            NotImplementedError: 如果子类不支持此方法。
            ProviderError: 如果与 LLM 交互失败。
        """
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 chat 方法。")

    async def achat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """异步版本的 chat。"""
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 achat 方法。")

    def stream_generate(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        以流式方式生成文本。

        Args:
            prompt (str): 输入提示。
            **kwargs: LLM 特定参数。

        Yields:
            str: 生成的文本片段。

        Raises:
            NotImplementedError: 如果子类不支持此方法。
            ProviderError: 如果与 LLM 交互失败。
        """
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 stream_generate 方法。")


    async def astream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """异步流式生成文本。"""
        raise NotImplementedError(f"{self.__class__.__name__} 不支持 astream_generate 方法。")
        # 异步生成器的特殊写法
        if False: # pragma: no cover
            yield # pragma: no cover

    # 可以添加其他方法，如计算 token 数量等

class ProviderError(Exception):
    """与外部 AI Provider (LLM, OCR 等) 交互时发生的错误基类。"""
    pass