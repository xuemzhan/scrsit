# src/scrsit/llm/huggingface_llm.py
from base_llm import BaseLLM, BaseEmbeddingLLM
from typing import List, Dict, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModel

class HuggingFaceGenerativeLLM(BaseLLM):
    """使用 Hugging Face Transformers 库的本地生成式 LLM。"""

    def __init__(self, model_name: str = "gpt2", device: int = -1):
        """
        初始化 HuggingFaceGenerativeLLM。

        Args:
            model_name (str): 要使用的 Hugging Face 模型名称，默认为 "gpt2"。
            device (int): 模型运行的设备，-1 表示 CPU，其他数字表示 GPU 索引。
        """
        self.model_name = model_name
        self.generator = pipeline("text-generation", model=self.model_name, device=device)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """
        使用本地 Hugging Face 模型生成文本。

        Args:
            prompt (str): 输入的提示文本。
            **kwargs (Any): 其他生成参数，例如 `max_length`, `num_return_sequences`。

        Returns:
            str: 生成的文本。
        """
        try:
            results = self.generator(prompt, **kwargs)
            return results[0]["generated_text"] if results else ""
        except Exception as e:
            raise Exception(f"Error generating text with Hugging Face model {self.model_name}: {e}")

class HuggingFaceEmbeddingLLM(BaseEmbeddingLLM):
    """使用 Hugging Face Transformers 库的本地 Embedding LLM。"""

    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2", device: int = -1):
        """
        初始化 HuggingFaceEmbeddingLLM。

        Args:
            model_name (str): 要使用的 Hugging Face Embedding 模型名称，默认为 "sentence-transformers/all-mpnet-base-v2"。
            device (int): 模型运行的设备，-1 表示 CPU，其他数字表示 GPU 索引。
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to("cuda" if device >= 0 else "cpu")
        self.device = "cuda" if device >= 0 else "cpu"

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用本地 Hugging Face 模型为文本列表创建嵌入向量。

        Args:
            texts (List[str]): 输入的文本列表。

        Returns:
            List[List[float]]: 嵌入向量的列表。
        """
        try:
            encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(self.device)
            self.model.eval()
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                # Perform pooling. In this case, mean pooling.
                token_embeddings = model_output.last_hidden_state
                input_mask_expanded = encoded_input['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                mean_pooled = sum_embeddings / sum_mask
            return mean_pooled.cpu().tolist()
        except ImportError:
            raise ImportError("You need to install the 'torch' library to use HuggingFace embedding models.")
        except Exception as e:
            raise Exception(f"Error creating embeddings with Hugging Face model {self.model_name}: {e}")

if __name__ == "__main__":
    try:
        # Example using a generative model (requires transformers library)
        generator = HuggingFaceGenerativeLLM(model_name="gpt2")
        prompt = "The quick brown fox"
        output = generator.generate_text(prompt, max_length=30, num_return_sequences=1)
        print(f"Example Hugging Face Generator Output:\n{output}")
    except ImportError:
        print("Warning: transformers library is not installed. Skipping Hugging Face generative example.")
    except Exception as e:
        print(f"An error occurred with Hugging Face generative model: {e}")

    try:
        # Example using an embedding model (requires transformers and torch libraries)
        import torch
        embedder = HuggingFaceEmbeddingLLM()
        texts_to_embed = ["This is a sentence for embedding.", "Another sentence here."]
        embeddings = embedder.create_embeddings(texts_to_embed)
        print(f"\nExample Hugging Face Embedder Output (first embedding):\n{embeddings[0][:10]}...") # 打印前 10 个维度
    except ImportError as e:
        print(f"Warning: {e}. Skipping Hugging Face embedding example.")
    except Exception as e:
        print(f"An error occurred with Hugging Face embedding model: {e}")