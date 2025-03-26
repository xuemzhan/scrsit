# src/scrsit/core/config/settings.py

"""
使用 Pydantic 定义应用配置模型，加载来自 .env、环境变量等的配置。
"""
import logging
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.scrsit.core.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class PluginSetting(BaseSettings):
    """单个插件的配置基类，具体插件可以继承并添加字段。"""
    # model_config = SettingsConfigDict(env_prefix='SCRSIT_PLUGIN_') # 可选的前缀
    pass


class AppSettings(BaseSettings):
    """
    应用程序的核心配置。
    """
    # Pydantic V2 Settings Management
    model_config = SettingsConfigDict(
        env_file='.env',        # 加载 .env 文件
        env_prefix='SCRSIT_',   # 环境变量前缀，例如 SCRSIT_LOG_LEVEL
        extra='ignore'          # 忽略未定义的额外字段
    )

    # --- 日志配置 ---
    log_level: str = "INFO"

    # --- 插件选择与配置 ---
    # 解析器配置 (示例：可以指定默认或按类型指定)
    default_parser: Optional[str] = None # 例如 "pdf_default"
    parser_mapping: Dict[str, str] = {} # 例如 {"pdf": "pdf_poppler", "docx": "python_docx"}

    # 分块器配置
    default_chunker: str = "recursive_text" # 默认分块器名称
    chunker_config: Dict[str, PluginSetting] = {} # 具体分块器的配置

    # Embedding 配置
    default_embedder: str = "openai" # 默认 Embedding 模型提供者名称
    embedder_config: Dict[str, PluginSetting] = {} # 具体 Embedding 提供者的配置

    # LLM Provider 配置
    default_llm_provider: str = "openai" # 默认 LLM 提供者名称
    llm_provider_config: Dict[str, PluginSetting] = {} # 具体 LLM 提供者的配置

    # 分析器配置
    enabled_analyzers: List[str] = ["entity_extraction"] # 启用的分析器名称列表
    analyzer_config: Dict[str, PluginSetting] = {} # 具体分析器的配置

    # 持久化存储配置
    document_store_name: str = "memory" # 使用的文档存储插件名称
    vector_store_name: str = "memory"   # 使用的向量存储插件名称
    structured_store_name: str = "memory" # 使用的结构化数据存储插件名称
    persistence_config: Dict[str, PluginSetting] = {} # 具体存储插件的配置 (例如 DB 连接串)

    # --- 其他配置 (根据需要添加) ---
    # api_key_openai: Optional[str] = None # 直接在这里定义或让具体插件配置类处理

def load_settings() -> AppSettings:
    """
    加载并返回应用配置实例。

    Returns:
        AppSettings: 加载后的配置对象。

    Raises:
        ConfigurationError: 如果配置加载失败。
    """
    try:
        settings = AppSettings()
        logger.info("应用配置加载成功。")
        # 可以在这里添加更复杂的验证逻辑
        return settings
    except Exception as e:
        logger.exception("加载应用配置时出错。", exc_info=True)
        raise ConfigurationError(f"加载配置失败: {e}") from e

# 全局配置实例 (惰性加载)
_settings_instance: Optional[AppSettings] = None

def get_settings() -> AppSettings:
    """
    获取全局唯一的 AppSettings 实例。
    如果尚未加载，则加载它。
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = load_settings()
    return _settings_instance

if __name__ == '__main__':
    try:
        settings = get_settings()
        print("应用配置加载测试:")
        print(f"日志级别: {settings.log_level}")
        print(f"默认解析器: {settings.default_parser}")
        print(f"解析器映射: {settings.parser_mapping}")
        print(f"默认分块器: {settings.default_chunker}")
        print(f"分块器配置: {settings.chunker_config}")
        print(f"默认 Embedder: {settings.default_embedder}")
        print(f"Embedder 配置: {settings.embedder_config}")
        print(f"默认 LLM Provider: {settings.default_llm_provider}")
        print(f"LLM Provider 配置: {settings.llm_provider_config}")
        print(f"启用的分析器: {settings.enabled_analyzers}")
        print(f"分析器配置: {settings.analyzer_config}")
        print(f"文档存储插件: {settings.document_store_name}")
        print(f"向量存储插件: {settings.vector_store_name}")
        print(f"结构化存储插件: {settings.structured_store_name}")
        print(f"持久化配置: {settings.persistence_config}")
    except Exception as e:
        print(f"加载配置时发生错误: {e}")