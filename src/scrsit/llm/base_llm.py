# src/scrsit/llm/base_llm.py
from abc import ABC, abstractmethod
from typing import List, Any, Optional

class BaseLLM(ABC):
    """LLM 模型的抽象基类。"""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        根据给定的提示生成文本。

        Args:
            prompt (str): 输入的提示文本。
            **kwargs (Any): 其他模型参数。

        Returns:
            str: 生成的文本。
        """
        pass

class BaseEmbeddingLLM(ABC):
    """Embedding LLM 模型的抽象基类。"""

    @abstractmethod
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        为给定的文本列表创建嵌入向量。

        Args:
            texts (List[str]): 输入的文本列表。

        Returns:
            List[List[float]]: 嵌入向量的列表，每个文本对应一个向量。
        """
        pass
    
class BaseMultimodalLLM(ABC):
    """多模态 LLM 模型的抽象基类。"""

    @abstractmethod
    def generate_content(self, prompt: str, images: Optional[List[str]] = None, **kwargs: Any) -> str:
        """
        根据给定的文本提示和可选的图像列表生成内容。

        Args:
            prompt (str): 输入的文本提示。
            images (Optional[List[str]]): 可选的图像列表，可以是文件路径或 base64 编码的字符串。
            **kwargs (Any): 其他模型参数。

        Returns:
            str: 生成的文本内容。
        """
        pass

if __name__ == "__main__":
    class DummyGenerator(BaseLLM):
        def generate_text(self, prompt: str, **kwargs: Any) -> str:
            return f"Generated text for prompt: {prompt}"

    class DummyEmbedder(BaseEmbeddingLLM):
        def create_embeddings(self, texts: List[str]) -> List[List[float]]:
            return [[0.0] * 10 for _ in texts] # 返回一个包含10个0.0的向量列表

    class DummyMultimodal(BaseMultimodalLLM):
        def generate_content(self, prompt: str, images: Optional[List[str]] = None, **kwargs: Any) -> str:
            image_info = f" with {len(images)} images" if images else ""
            return f"Generated content for prompt: {prompt}{image_info}"

    generator = DummyGenerator()
    prompt = "Write a short poem."
    output = generator.generate_text(prompt, max_tokens=50)
    print(f"Example Generator Output: {output}")

    embedder = DummyEmbedder()
    texts_to_embed = ["Hello", "World"]
    embeddings = embedder.create_embeddings(texts_to_embed)
    print(f"Example Embedder Output: {embeddings}")

    multimodal_model = DummyMultimodal()
    multimodal_prompt = "Describe this scene."
    image_paths = ["path/to/image1.jpg", "path/to/image2.png"]
    multimodal_output = multimodal_model.generate_content(multimodal_prompt, images=image_paths, max_tokens=100)
    print(f"Example Multimodal Output: {multimodal_output}")