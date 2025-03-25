# src/scrsit/llm/openai_llm.py
from base_llm import BaseLLM, BaseEmbeddingLLM
from typing import List, Dict, Any, Optional
import os
from openai import OpenAI

class OpenAIGenerativeLLM(BaseLLM):
    """使用 OpenAI API 的生成式 LLM。"""

    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        初始化 OpenAIGenerativeLLM。

        Args:
            model_name (str): 要使用的 OpenAI 模型名称，默认为 "gpt-3.5-turbo"。
            api_key (Optional[str]): OpenAI API 密钥。如果为 None，则尝试从环境变量中获取。
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        使用 OpenAI API 生成文本。

        Args:
            prompt (str): 输入的提示文本。
            **kwargs (Any): 其他 OpenAI API 参数，例如 `max_tokens`, `temperature`。

        Returns:
            str: 生成的文本。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating text with OpenAI: {e}")

class OpenAIEmbeddingLLM(BaseEmbeddingLLM):
    """使用 OpenAI API 的 Embedding LLM。"""

    def __init__(self, model_name: str = "text-embedding-ada-002", api_key: Optional[str] = None):
        """
        初始化 OpenAIEmbeddingLLM。

        Args:
            model_name (str): 要使用的 OpenAI Embedding 模型名称，默认为 "text-embedding-ada-002"。
            api_key (Optional[str]): OpenAI API 密钥。如果为 None，则尝试从环境变量中获取。
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=self.api_key)

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用 OpenAI API 为文本列表创建嵌入向量。

        Args:
            texts (List[str]): 输入的文本列表。

        Returns:
            List[List[float]]: 嵌入向量的列表。
        """
        try:
            response = self.client.embeddings.create(input=texts, model=self.model_name)
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Error creating embeddings with OpenAI: {e}")

if __name__ == "__main__":
    # 确保您已设置 OPENAI_API_KEY 环境变量
    try:
        generator = OpenAIGenerativeLLM()
        prompt = "Explain the importance of unit tests in software development."
        output = generator.generate_text(prompt, max_tokens=150)
        print(f"Example OpenAI Generator Output:\n{output}")

        embedder = OpenAIEmbeddingLLM()
        texts_to_embed = ["This is the first sentence.", "Here is another sentence."]
        embeddings = embedder.create_embeddings(texts_to_embed)
        print(f"\nExample OpenAI Embedder Output (first embedding):\n{embeddings[0][:10]}...") # 打印前 10 个维度
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")