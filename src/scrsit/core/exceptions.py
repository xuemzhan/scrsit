# src/scrsit/core/exceptions.py

"""
定义框架的核心自定义异常。
"""

class ScrsitError(Exception):
    """框架相关的基类异常。"""
    pass

class PluginError(Exception):
    """插件相关错误基类。"""
    pass

class PluginNotFoundError(PluginError):
    """未找到插件时抛出的异常。"""
    pass

class PluginLoadError(PluginError):
    """当加载插件失败时引发。"""
    def __init__(self, entry_point, error: Exception):
        message = f"加载插件入口点 '{entry_point}'失败: {error}"
        super().__init__(message)

class PluginConfigurationError(PluginError):
    """当插件配置无效时引发。"""
    pass

class ConfigurationError(Exception):
    """配置加载或验证错误。"""
    pass

class WorkflowError(Exception):
    """工作流执行过程中发生的错误。"""
    pass

class ParsingError(WorkflowError):
    """当文档解析失败时引发。"""
    pass

class AnalysisError(WorkflowError):
    """当内容分析失败时引发。"""
    pass

class EmbeddingError(WorkflowError):
    """当生成 Embedding 失败时引发。"""
    pass

class StorageError(ScrsitError):
    """与数据存储相关的基类异常。"""
    pass