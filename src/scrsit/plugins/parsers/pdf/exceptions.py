# src/scrsit/plugins/parsers/pdf/exceptions.py

"""
定义 PDF 解析器插件特定的异常类。
"""

from src.scrsit.core.exceptions import ParsingError

# 定义一个特定于 PDF 解析的基类，继承自通用的 ParsingError
# 这样可以捕获所有 PDF 解析错误，同时也能捕获所有解析错误
class PdfParsingError(ParsingError):
    """PDF 解析插件 (PdfParser) 特定的错误基类。"""
    def __init__(self, message: str = "PDF 解析失败。"):
        # 调用父类构造函数，明确插件名称
        super().__init__(plugin_name="PdfParser", message=message)

class MagicPdfExecutionError(PdfParsingError):
    """调用 magic-pdf 外部工具时发生错误。"""
    def __init__(self, message: str = "执行 magic-pdf 工具时出错。"):
        # 可以在这里添加更多上下文信息，例如 return code, stderr 等
        super().__init__(message=f"Magic-PDF 执行错误: {message}")
        self.return_code = None # 可以选择性地添加属性
        self.stderr = None      # 可以选择性地添加属性

class MagicPdfOutputError(PdfParsingError):
    """解析 magic-pdf 输出时发生错误。"""
    def __init__(self, message: str = "解析 magic-pdf 输出时出错。"):
        super().__init__(message=f"Magic-PDF 输出处理错误: {message}")

# 你可以根据需要添加更多特定于 PDF 解析过程的异常，例如：
class PdfPasswordError(PdfParsingError):
    """PDF 文件需要密码但未提供或密码错误。"""
    def __init__(self):
        super().__init__(message="PDF 文件受密码保护。")

class PdfCorruptedError(PdfParsingError):
    """PDF 文件已损坏或格式不正确。"""
    def __init__(self, details: str = ""):
        message = "PDF 文件损坏或格式无效。"
        if details:
            message += f" 细节: {details}"
        super().__init__(message=message)