# src/scrsit/plugins/parsers/pdf/config.py
"""PDF 解析器插件 (MinerU/magic_pdf) 的配置模型。"""

from typing import Dict, Any, Optional
from pydantic import Field, BaseModel

# 如果核心框架定义了 PluginSetting，则继承它
# from scrsit.core.config.settings import PluginSetting
# class PdfParserConfig(PluginSetting):

# 否则，直接继承 BaseModel
class PdfParserConfig(BaseModel):
    """
    配置 PdfMinerUParser 的参数。
    """
    # MinerU/magic_pdf 相关配置
    # split_by_page: bool = Field(
    #     default=True,
    #     description="是否按页调用 magic_pdf 进行处理。这有助于处理大型文档和提供进度。"
    # )
    magic_pdf_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="传递给 magic_pdf.process 的额外参数字典。"
        "例如: {'output_markdown': True, 'visualize_output': False}"
    )
    # 请根据 magic_pdf 的实际可用参数调整这里的默认值和描述

    # 健壮性配置
    retry_attempts: int = Field(
        default=3,
        description="调用 magic_pdf 失败时的最大重试次数。"
    )
    retry_delay_seconds: float = Field(
        default=2.0,
        description="每次重试之间的延迟时间（秒）。"
    )
    page_batch_size: int = Field(
        default=1, # 默认为1，即逐页处理以提供更精细的进度和错误定位
        description="当按页处理时，一次传递给 magic_pdf 的页面数量。"
    )
    save_intermediate_files: bool = Field(
        default=False,
        description="是否在处理失败或调试时保存中间文件（例如，送入magic_pdf的临时PDF）。"
    )
    temp_file_dir: Optional[str] = Field(
        default=None,
        description="用于存储临时文件（如从内存数据创建的PDF）的目录。默认为系统临时目录。"
    )

    class Config:
        # Pydantic V2 配置方式
        extra = 'ignore' # 忽略settings中未在此定义的额外字段