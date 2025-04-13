# src/scrsit/plugins/parsers/pdf/config.py
import tempfile
from pydantic_settings import BaseSettings
from pydantic import Field, DirectoryPath, FilePath
from typing import Optional

class PdfParserSettings(BaseSettings):
    """
    PDF 解析器插件的配置模型。
    将从环境变量或 .env 文件加载，前缀为 'SCRSIT_PLUGIN_PDF_'。
    """
    # --- magic-pdf 配置 ---
    magic_pdf_path: FilePath = Field(
        description="magic-pdf 可执行文件的完整路径。"
    )
    magic_pdf_output_base_dir: Optional[DirectoryPath] = Field(
        default=None,
        description="magic-pdf 输出文件的基础目录。如果为 None，将使用系统临时目录。"
    )
    magic_pdf_timeout_seconds: int = Field(
        default=300, # 默认 5 分钟超时
        description="调用 magic-pdf 的最大等待时间（秒）。"
    )
    magic_pdf_extra_args: Optional[str] = Field(
        default=None,
        description="传递给 magic-pdf 的额外命令行参数字符串。"
    )

    # --- 文件处理配置 ---
    large_file_threshold_mb: Optional[float] = Field(
        default=500.0, # 默认 500MB
        description="文件大小阈值（MB）。超过此大小的文件在处理前会记录警告。设为 None 则不检查。"
    )
    # 注意：实际的文件切分逻辑在此未实现，magic-pdf 本身可能处理大文件，
    # 或者需要更复杂的预处理步骤。这里仅作大小检查示例。
    cleanup_magic_pdf_output: bool = Field(
        default=True,
        description="是否在解析完成后自动清理 magic-pdf 的输出目录。"
    )

    class Config:
        env_prefix = 'SCRSIT_PLUGIN_PDF_' # 环境变量前缀
        env_file = '.env'               # 如果使用 .env 文件
        extra = 'ignore'                # 忽略未定义的字段

# 实例化一个默认配置（可选，用于测试或默认行为）
# default_pdf_parser_settings = PdfParserSettings()