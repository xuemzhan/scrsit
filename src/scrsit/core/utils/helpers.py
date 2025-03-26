# src/scrsit/core/utils/helpers.py

"""
核心通用工具函数或类。
"""
import uuid

def generate_uuid() -> str:
    """生成一个 UUID 字符串。"""
    return str(uuid.uuid4())

# 可以根据需要添加更多不依赖具体插件实现的通用函数