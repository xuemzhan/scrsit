# src/scrsit/core/exceptions.py

"""
定义框架的核心自定义异常。
"""

class ScrsitError(Exception):
    """应用的基础异常类，所有自定义业务异常应继承自此类。"""
    def __init__(self, message: str = "Scrsit 系统发生未知错误。"):
        super().__init__(message)

# --- 核心错误 ---

class ConfigurationError(ScrsitError):
    """配置相关的错误。"""
    def __init__(self, message: str = "系统配置错误。"):
        super().__init__(message)

class WorkflowError(ScrsitError):
    """工作流执行过程中发生的错误。"""
    def __init__(self, message: str = "工作流执行失败。"):
        super().__init__(message)

class PluginNotFoundError(ScrsitError):
    """请求的插件未找到或未注册。"""
    def __init__(self, plugin_type: str, plugin_name: str = None):
        message = f"未找到类型为 '{plugin_type}' 的插件"
        if plugin_name:
            message += f" (名称: '{plugin_name}')"
        message += "。请检查配置和插件注册。"
        super().__init__(message)

# --- 插件错误基类 ---

class PluginError(ScrsitError):
    """所有插件相关错误的基类。"""
    def __init__(self, plugin_name: str = "未知插件", message: str = "插件执行错误。"):
        self.plugin_name = plugin_name
        full_message = f"插件 '{plugin_name}' 发生错误: {message}"
        super().__init__(full_message)

# --- 接口相关的通用插件错误 ---
# 这些可以被具体插件实现中的错误继承

class ParsingError(PluginError):
    """文档解析过程中发生的通用错误。"""
    def __init__(self, plugin_name: str = "未知解析器", message: str = "文档解析失败。"):
        super().__init__(plugin_name=plugin_name, message=message)

class AnalysisError(PluginError):
    """内容分析过程中发生的通用错误。"""
    def __init__(self, plugin_name: str = "未知分析器", message: str = "内容分析失败。"):
        super().__init__(plugin_name=plugin_name, message=message)

class EmbeddingError(PluginError):
    """Embedding 生成过程中发生的通用错误。"""
    def __init__(self, plugin_name: str = "未知 Embedder", message: str = "Embedding 生成失败。"):
        super().__init__(plugin_name=plugin_name, message=message)

class ProviderError(PluginError):
    """与外部 AI Provider (LLM, OCR 等) 交互时发生的错误基类。"""
    def __init__(self, provider_name: str = "未知 Provider", message: str = "与 Provider 交互失败。"):
        # 注意：ProviderError 可能也适合直接继承 ScrsitError，取决于设计选择
        # 这里继承 PluginError 强调它是通过插件接口发生的
        super().__init__(plugin_name=provider_name, message=message)

class StoreError(PluginError):
    """与数据存储交互时发生的通用错误。"""
    def __init__(self, store_name: str = "未知存储", message: str = "数据存储操作失败。"):
        super().__init__(plugin_name=store_name, message=message)


# 可以根据需要添加更多特定的核心或通用插件异常