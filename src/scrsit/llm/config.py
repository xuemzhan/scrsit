# src/scrsit/llm/config.py
from typing import Dict, Any
import os
import json

def load_llm_config(config_path: str = "config/llm_config.json") -> Dict[str, Any]:
    """
    加载 LLM 模块的配置信息。

    Args:
        config_path (str): 配置文件的路径，默认为 "config/llm_config.json"。

    Returns:
        Dict[str, Any]: 包含 LLM 配置信息的字典。
    """
    config: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        print(f"Warning: LLM config file not found at {config_path}. Using default settings.")
    return config

def get_llm_provider_config(config: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
    """
    获取特定 LLM 提供商的配置。

    Args:
        config (Dict[str, Any]): LLM 配置字典。
        provider_name (str): 提供商的名称 (例如 "openai", "huggingface").

    Returns:
        Dict[str, Any]: 提供商的配置字典，如果找不到则返回空字典。
    """
    return config.get(provider_name, {})

if __name__ == "__main__":
    # 假设在项目根目录下有一个 config 文件夹，其中包含 llm_config.json
    # llm_config.json 的内容示例:
    # {
    #   "openai": {
    #     "model_name": "gpt-4",
    #     "embedding_model": "text-embedding-ada-002"
    #   },
    #   "huggingface": {
    #     "generator_model": "facebook/bart-large-cnn",
    #     "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    #   }
    # }
    config = load_llm_config()
    print(f"Loaded LLM Config: {config}")

    openai_config = get_llm_provider_config(config, "openai")
    print(f"OpenAI Config: {openai_config}")

    huggingface_config = get_llm_provider_config(config, "huggingface")
    print(f"Hugging Face Config: {huggingface_config}")