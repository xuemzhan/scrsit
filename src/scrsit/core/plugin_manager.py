# src/scrsit/core/plugin_manager.py

"""
插件管理器。
负责发现、加载、验证和提供插件实例。
依赖于 `pyproject.toml` 中定义的 entry points。
"""
import logging
import importlib.metadata
from typing import Type, Dict, List, Optional, TypeVar, Generic, cast, Any
from collections import defaultdict

from src.scrsit.core.config.settings import AppSettings, get_settings
from src.scrsit.core.exceptions import (
    PluginNotFoundError, PluginLoadError, PluginConfigurationError, ConfigurationError
)
from scrsit.core.interfaces import BasePluginInterface # 可选的基础接口
# 显式导入所有需要的接口类型
from scrsit.core.interfaces import (
    BaseParser, BaseChunker, BaseEmbedder, BaseAnalyzer,
    BaseLLMProvider, BaseOCRProvider, BaseMultimodalProvider,
    BaseDocumentStore, BaseVectorStore, BaseStructuredStore,
    BaseKnowledgeProvider, BaseReviewer, BaseProposalGenerator
)

logger = logging.getLogger(__name__)

# 类型变量用于泛型方法
T = TypeVar('T') #, bound=BasePluginInterface) # 如果使用 BasePluginInterface

# 定义插件组名称常量，应与 pyproject.toml 中的组名一致
PLUGIN_GROUPS = {
    "parsers": BaseParser,
    "chunkers": BaseChunker,
    "embedders": BaseEmbedder,
    "analyzers": BaseAnalyzer,
    "llm_providers": BaseLLMProvider,
    "ocr_providers": BaseOCRProvider,
    "multimodal_providers": BaseMultimodalProvider,
    "document_stores": BaseDocumentStore,
    "vector_stores": BaseVectorStore,
    "structured_stores": BaseStructuredStore,
    "knowledge_providers": BaseKnowledgeProvider,
    "reviewers": BaseReviewer,
    "proposal_generators": BaseProposalGenerator,
}

class PluginManager:
    """
    管理应用中的所有插件。
    """
    def __init__(self, settings: Optional[AppSettings] = None):
        """
        初始化插件管理器。

        Args:
            settings (Optional[AppSettings]): 应用配置。如果为 None，则尝试加载全局配置。
        """
        self.settings = settings or get_settings()
        self._plugins: Dict[Type, Dict[str, Type]] = defaultdict(dict) # {InterfaceType: {plugin_name: PluginClass}}
        self._instances: Dict[Type, Dict[str, Any]] = defaultdict(dict) # {InterfaceType: {plugin_name: PluginInstance}}
        self._load_all_plugins()

    def _load_all_plugins(self):
        """
        发现并加载所有在 pyproject.toml 中声明的插件。
        """
        logger.info("开始加载所有插件...")
        for group_name, interface_cls in PLUGIN_GROUPS.items():
            entry_point_group = f"scrsit.{group_name}"
            try:
                entry_points = importlib.metadata.entry_points(group=entry_point_group)
            except Exception as e:
                logger.warning(f"无法获取插件组 '{entry_point_group}' 的入口点: {e}", exc_info=True)
                continue

            if not entry_points:
                 logger.debug(f"在组 '{entry_point_group}' 中未找到插件入口点。")
                 continue

            logger.info(f"在组 '{entry_point_group}' 中发现 {len(entry_points)} 个入口点。")

            for ep in entry_points:
                plugin_name = ep.name
                try:
                    plugin_class = ep.load()
                    logger.debug(f"成功加载插件 '{plugin_name}' (类: {plugin_class.__name__}) 从入口点 '{ep.value}'。")

                    # 验证插件是否实现了预期的接口
                    if not issubclass(plugin_class, interface_cls):
                        logger.error(
                            f"插件 '{plugin_name}' (类: {plugin_class.__name__}) "
                            f"未实现预期的接口 '{interface_cls.__name__}'。将跳过此插件。"
                        )
                        continue

                    if hasattr(plugin_class, 'plugin_name'):
                         plugin_class.plugin_name = plugin_name # 将插件名称注入类中（如果需要）

                    self._plugins[interface_cls][plugin_name] = plugin_class
                    logger.info(f"已注册插件 '{plugin_name}' (类型: {interface_cls.__name__})。")

                except Exception as e:
                    logger.error(f"加载插件 '{plugin_name}' 从入口点 '{ep.value}' 时出错: {e}", exc_info=True)
                    # 可以选择抛出 PluginLoadError 或仅记录错误并继续
                    # raise PluginLoadError(ep.value, e) from e

        logger.info("所有插件加载完成。")

    def _get_plugin_config(self, plugin_type: str, plugin_name: str) -> Dict[str, Any]:
        """获取特定插件的配置字典。"""
        # 尝试从 settings 中获取特定插件类型的配置字典
        # 例如, settings.embedder_config, settings.persistence_config
        config_attr_name = f"{plugin_type}_config" # e.g., embedder_config
        specific_configs = getattr(self.settings, config_attr_name, {})
        if plugin_name in specific_configs:
             plugin_cfg_obj = specific_configs[plugin_name]
             if plugin_cfg_obj:
                 # 假设配置是 Pydantic 模型
                 return plugin_cfg_obj.model_dump(exclude_unset=True)
             else:
                 return {}

        # 尝试获取持久化插件的通用配置
        if plugin_type.endswith("_store") and plugin_name in self.settings.persistence_config:
             plugin_cfg_obj = self.settings.persistence_config[plugin_name]
             if plugin_cfg_obj:
                 return plugin_cfg_obj.model_dump(exclude_unset=True)
             else:
                 return {}

        # 如果没有找到特定配置，返回空字典
        logger.debug(f"未找到插件 '{plugin_name}' (类型: {plugin_type}) 的特定配置，将使用默认值。")
        return {}

    def _get_instance(self, interface_cls: Type[T], plugin_name: str) -> T:
        """获取或创建插件实例。"""
        if plugin_name in self._instances.get(interface_cls, {}):
            return cast(T, self._instances[interface_cls][plugin_name])

        if plugin_name not in self._plugins.get(interface_cls, {}):
            raise PluginNotFoundError(interface_cls.__name__, plugin_name)

        plugin_class = self._plugins[interface_cls][plugin_name]
        plugin_type_key = next((k for k, v in PLUGIN_GROUPS.items() if v == interface_cls), None)

        if not plugin_type_key:
             # 这理论上不应该发生，因为 interface_cls 来自 PLUGIN_GROUPS
             raise ConfigurationError(f"无法确定接口 '{interface_cls.__name__}' 对应的插件类型键。")

        config = self._get_plugin_config(plugin_type_key, plugin_name)

        try:
            logger.info(f"正在创建插件 '{plugin_name}' (类型: {interface_cls.__name__}) 的实例...")
            # 假设插件构造函数接受 config 字典
            instance = plugin_class(config=config)

            # 可选：调用配置验证方法
            if hasattr(instance, 'validate_config') and callable(instance.validate_config):
                 try:
                     instance.validate_config()
                 except Exception as e:
                     logger.error(f"插件 '{plugin_name}' 的配置验证失败: {e}", exc_info=True)
                     raise PluginConfigurationError(f"插件 '{plugin_name}' 配置无效: {e}") from e

            self._instances[interface_cls][plugin_name] = instance
            logger.info(f"插件 '{plugin_name}' (类型: {interface_cls.__name__}) 实例创建成功。")
            return cast(T, instance)
        except Exception as e:
            logger.exception(f"创建插件 '{plugin_name}' 实例时出错: {e}", exc_info=True)
            # 区分是配置错误还是其他实例化错误
            if isinstance(e, (PluginConfigurationError, ConfigurationError)):
                raise
            else:
                raise PluginLoadError(f"插件 '{plugin_name}' 实例化失败", e) from e


    def get_plugin(self, interface_cls: Type[T], name: Optional[str] = None) -> T:
        """
        获取指定接口类型和名称的插件实例。

        Args:
            interface_cls (Type[T]): 请求的插件接口类型 (例如 BaseParser)。
            name (Optional[str]): 请求的插件名称。如果为 None，则尝试获取默认插件。

        Returns:
            T: 插件实例。

        Raises:
            PluginNotFoundError: 如果找不到合适的插件。
            ConfigurationError: 如果默认插件未配置或配置错误。
            PluginLoadError: 如果插件加载或实例化失败。
        """
        if name:
            return self._get_instance(interface_cls, name)
        else:
            # 获取默认插件名称
            default_plugin_name = None
            plugin_type_key = next((k for k, v in PLUGIN_GROUPS.items() if v == interface_cls), None)

            if plugin_type_key:
                # 特殊处理存储类插件的名称获取
                if plugin_type_key == "document_stores":
                    default_plugin_name = self.settings.document_store_name
                elif plugin_type_key == "vector_stores":
                    default_plugin_name = self.settings.vector_store_name
                elif plugin_type_key == "structured_stores":
                    default_plugin_name = self.settings.structured_store_name
                else:
                    # 通用获取默认插件名称的逻辑 (例如 default_parser, default_embedder)
                    default_attr_name = f"default_{plugin_type_key[:-1]}" # e.g., default_parser
                    default_plugin_name = getattr(self.settings, default_attr_name, None)

            if not default_plugin_name:
                # 如果只有一个该类型的插件被注册，可以将其作为默认
                available_plugins = self._plugins.get(interface_cls, {})
                if len(available_plugins) == 1:
                     default_plugin_name = list(available_plugins.keys())[0]
                     logger.info(f"未配置默认 {interface_cls.__name__}，但只找到一个已注册插件 '{default_plugin_name}'，将其用作默认。")
                else:
                    raise ConfigurationError(f"未指定插件名称，且无法确定接口 '{interface_cls.__name__}' 的默认插件。请在配置中设置默认值或显式指定名称。可用插件: {list(available_plugins.keys())}")

            logger.debug(f"获取接口 '{interface_cls.__name__}' 的默认插件: '{default_plugin_name}'")
            return self._get_instance(interface_cls, default_plugin_name)

    def get_parser(self, file_type: Optional[str] = None, parser_name: Optional[str] = None) -> BaseParser:
        """
        获取文档解析器实例。
        如果提供了 parser_name，则直接获取该名称的解析器。
        否则，如果提供了 file_type，则根据配置的 parser_mapping 获取。
        否则，获取默认解析器。

        Args:
            file_type (Optional[str]): 文件类型扩展名 (例如 "pdf", "docx")。
            parser_name (Optional[str]): 解析器的显式名称。

        Returns:
            BaseParser: 解析器实例。

        Raises:
            PluginNotFoundError, ConfigurationError, PluginLoadError
        """
        if parser_name:
            return self.get_plugin(BaseParser, name=parser_name)

        if file_type:
            normalized_type = file_type.lower().lstrip('.')
            mapped_name = self.settings.parser_mapping.get(normalized_type)
            if mapped_name:
                logger.debug(f"根据文件类型 '{normalized_type}' 获取映射的解析器: '{mapped_name}'")
                return self.get_plugin(BaseParser, name=mapped_name)
            else:
                logger.warning(f"未找到文件类型 '{normalized_type}' 的特定解析器映射，将尝试获取默认解析器。")
                # 没有映射时回退到默认解析器或抛出错误？当前选择回退。

        # 获取默认解析器
        return self.get_plugin(BaseParser) # name=None

    def get_embedder(self, name: Optional[str] = None) -> BaseEmbedder:
        """获取 Embedder 实例。"""
        return self.get_plugin(BaseEmbedder, name=name)

    def get_chunker(self, name: Optional[str] = None) -> BaseChunker:
        """获取 Chunker 实例。"""
        return self.get_plugin(BaseChunker, name=name)

    def get_llm_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        """获取 LLM Provider 实例。"""
        return self.get_plugin(BaseLLMProvider, name=name)

    def get_document_store(self, name: Optional[str] = None) -> BaseDocumentStore:
        """获取 Document Store 实例。"""
        # 如果 name 为 None，get_plugin 会使用 settings.document_store_name
        return self.get_plugin(BaseDocumentStore, name=name)

    def get_vector_store(self, name: Optional[str] = None) -> BaseVectorStore:
        """获取 Vector Store 实例。"""
        # 如果 name 为 None，get_plugin 会使用 settings.vector_store_name
        return self.get_plugin(BaseVectorStore, name=name)

    def get_structured_store(self, name: Optional[str] = None) -> BaseStructuredStore:
        """获取 Structured Store 实例。"""
        # 如果 name 为 None，get_plugin 会使用 settings.structured_store_name
        return self.get_plugin(BaseStructuredStore, name=name)

    def get_analyzer(self, name: str) -> BaseAnalyzer:
        """获取指定名称的 Analyzer 实例。Analyzer 通常需要显式指定。"""
        return self.get_plugin(BaseAnalyzer, name=name)

    def get_enabled_analyzers(self) -> List[BaseAnalyzer]:
        """获取配置中所有启用的 Analyzer 实例列表。"""
        enabled_names = self.settings.enabled_analyzers
        analyzers = []
        for name in enabled_names:
            try:
                analyzers.append(self.get_analyzer(name))
            except PluginNotFoundError:
                logger.warning(f"配置中启用的分析器 '{name}' 未找到，将被忽略。")
        return analyzers

    # ... 为其他插件类型添加类似的 get_xxx 方法 ...

    def list_available_plugins(self) -> Dict[str, List[str]]:
        """列出所有已发现和加载的插件。"""
        available = defaultdict(list)
        for interface_cls, plugins in self._plugins.items():
            type_key = next((k for k, v in PLUGIN_GROUPS.items() if v == interface_cls), interface_cls.__name__)
            available[type_key] = sorted(list(plugins.keys()))
        return dict(available)