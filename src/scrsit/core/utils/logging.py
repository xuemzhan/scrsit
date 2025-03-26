# src/scrsit/core/utils/logging.py

"""
配置全局日志记录器。
"""
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    """
    全局日志配置，设置日志级别和格式。

    :param level: 日志级别，如 "INFO", "DEBUG" 等。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

# 在模块加载时执行一次基础配置，防止完全没有日志输出
# 可以在应用启动时调用 setup_logging 进行更详细的配置
# logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s')