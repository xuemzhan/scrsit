# src/scrsit/llm/ollama_llm.py
from base_llm import BaseLLM, BaseEmbeddingLLM
from typing import List, Dict, Any, Optional
import requests
import json

class OllamaLLM(BaseLLM):
    """与本地 Ollama 服务进行交互的生成式 LLM。"""

    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        初始化 OllamaLLM。

        Args:
            model_name (str): 要使用的 Ollama 模型名称，默认为 "llama2"。
            base_url (str): Ollama API 的基础 URL，默认为 "http://localhost:11434"。
        """
        self.model_name = model_name
        self.base_url = base_url
        self.generate_url = f"{self.base_url}/api/generate"

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        使用 Ollama API 生成文本。

        Args:
            prompt (str): 输入的提示文本。
            **kwargs (Any): 其他 Ollama API 参数，例如 `stream`, `raw`, `format`, `options`。

        Returns:
            str: 生成的文本。
        """
        payload = {
            "prompt": prompt,
            "model": self.model_name,
            **kwargs,
        }
        try:
            response = requests.post(self.generate_url, json=payload, stream=True)
            response.raise_for_status()
            generated_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            generated_text += data['response']
                        if data.get('done'):
                            break
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {line}")
                        continue
            return generated_text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Ollama API: {e}")

class OllamaEmbeddingLLM(BaseEmbeddingLLM):
    """与本地 Ollama 服务进行交互的 Embedding LLM。"""

    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        初始化 OllamaEmbeddingLLM。

        Args:
            model_name (str): 要使用的 Ollama 模型名称，默认为 "llama2" (需要模型支持 embeddings)。
            base_url (str): Ollama API 的基础 URL，默认为 "http://localhost:11434"。
        """
        self.model_name = model_name
        self.base_url = base_url
        self.embeddings_url = f"{self.base_url}/api/embeddings"

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用 Ollama API 为文本列表创建嵌入向量。

        Args:
            texts (List[str]): 输入的文本列表。

        Returns:
            List[List[float]]: 嵌入向量的列表。
        """
        payload = {
            "model": self.model_name,
            "prompt": texts,
        }
        try:
            response = requests.post(self.embeddings_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('embeddings',)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Ollama API: {e}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON response from Ollama: {response.text}")

if __name__ == "__main__":
    try:
        # Example using a generative model
        generator = OllamaLLM()
        prompt = "Write a very short story about a cat."
        output = generator.generate_text(prompt, max_length=100)
        print(f"Example Ollama Generator Output:\n{output}")
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to Ollama server at http://localhost:11434. Make sure Ollama is running.\n{e}")
    except Exception as e:
        print(f"An error occurred with Ollama generative model: {e}")

    try:
        # Example using an embedding model (ensure the model supports embeddings)
        embedder = OllamaEmbeddingLLM(model_name="nomic-embed-text") # You might need to pull this model first: `ollama pull nomic-embed-text`
        texts_to_embed = ["This is a test sentence for embedding.", "Another example text."]
        embeddings = embedder.create_embeddings(texts_to_embed)
        print(f"\nExample Ollama Embedder Output (first embedding):\n{embeddings[0][:10]}...") # 打印前 10 个维度
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to Ollama server at http://localhost:11434. Make sure Ollama is running.\n{e}")
    except Exception as e:
        print(f"An error occurred with Ollama embedding model: {e}")