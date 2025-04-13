# PDF 解析器插件 (pdf)

## 概述

本插件是 `scrsit` 核心解析器 (`BaseParser`) 的一个具体实现，专门用于处理 PDF 文档。它通过集成外部工具 `magic-pdf` 来执行底层的 PDF 内容和布局分析，然后将 `magic-pdf` 的输出结果转换为 `scrsit` 系统内部统一的 `Document` 数据模型。

## 主要功能

*   **PDF 解析**: 支持解析本地 PDF 文件（通过文件路径）或内存中的 PDF 数据（通过 IO 流）。
*   **集成 `magic-pdf`**: 异步调用配置好的 `magic-pdf` 可执行文件来处理 PDF，利用其强大的布局分析、文本提取、元素识别（图片、表格、公式等）能力。
*   **输出映射**: 解析 `magic-pdf` 生成的 `*_model.json` 和 `*_middle.json` 文件，提取关键信息。
*   **数据模型转换**: 将提取的信息（如文本内容、图片、表格、公式、元数据等）映射填充到 `scrsit.core.document.models.Document` 对象及其包含的元素（如 `Picture`, `Table`, `Formula`）中。
*   **配置驱动**: 插件行为（如 `magic-pdf` 路径、超时时间、输出目录等）可通过环境变量或 `.env` 文件进行配置。
*   **错误处理与日志**: 包含针对 `magic-pdf` 调用失败、输出文件缺失/错误、解析错误等的健壮错误处理机制，并记录详细日志。
*   **资源清理**: 自动管理和清理处理过程中产生的临时文件和 `magic-pdf` 输出目录（可配置）。

## 依赖项

*   **外部工具**:
    *   **`magic-pdf` 可执行文件**: 必须在运行 `scrsit` 系统的环境中安装并配置好其路径。插件需要调用此工具来完成实际的 PDF 解析工作。
*   **Python 库**:
    *   `pydantic` / `pydantic-settings`: 用于配置管理。
    *   (其他 `scrsit` 核心库依赖)
    *   *注意*: 具体的 Python 依赖项由项目根目录的 `pyproject.toml` 文件管理。

## 工作流程

1.  **接收输入**: 插件的 `parse` 方法接收一个 PDF 文件路径或一个包含 PDF 数据的二进制 IO 流。
2.  **输入处理**: 如果输入是 IO 流，会先将其保存到一个临时文件中。计算文件校验和。
3.  **文件检查**: (可选) 检查文件大小是否超过配置的阈值，并记录警告。
4.  **准备环境**: 确定或创建一个用于存放 `magic-pdf` 输出文件的目录（可以是指定的持久化目录或系统临时目录）。
5.  **调用 `magic-pdf`**: 异步执行 `magic-pdf` 命令，传入输入 PDF 文件路径和输出目录路径。设置了超时时间以防止进程卡死。
6.  **等待与结果检查**: 等待 `magic-pdf` 执行完成。检查其退出码，如果非零或超时，则记录错误并抛出异常。
7.  **定位输出**: 在 `magic-pdf` 输出目录中查找 `*_model.json` 和 `*_middle.json` 文件。如果找不到，则报错。
8.  **解析 JSON**: 读取并使用标准 `json` 库解析这两个核心 JSON 文件。
9.  **映射到 `Document`**: 调用内部的 `_map_to_document` 方法，遍历解析后的 JSON 数据：
    *   提取文档元数据（如页数、`magic-pdf` 版本）。
    *   从 `middle.json` 的 `para_blocks` 中提取文本内容，组合成 `Document.content`。
    *   识别 `image` 类型的块，找到对应的 `span` 获取图片路径，读取图片内容存入 `Picture` 对象，并尝试关联 `image_caption` 和 `image_footnote` 作为描述。
    *   识别 `table` 类型的块，创建 `Table` 对象，记录 bbox 和页面信息，并尝试关联 `table_caption` 和 `table_footnote`。注意：表格内容目前未直接解析，可能需要后续 OCR 或专门处理。
    *   识别 `interline_equations` 块，创建 `Formula` 对象，尝试从 `model.json` 匹配并获取 LaTeX 源码 (`raw` 字段)。
    *   其他元素如链接 (`Link`)、参考文献 (`Reference`)、结构化内容 (`StructuredContent`) 目前未在此版本中实现映射。
10. **返回结果**: 返回构建好的 `Document` 对象。
11. **清理**: 在 `finally` 块中，清理之前创建的临时输入文件和（根据配置）`magic-pdf` 的输出目录。

## 配置

插件通过环境变量进行配置。推荐使用 `.env` 文件来管理这些变量。所有变量都以 `SCRSIT_PLUGIN_PDF_` 作为前缀。

| 环境变量                                       | 类型       | 必须 | 默认值                         | 描述                                                                 |
| :--------------------------------------------- | :--------- | :--- | :----------------------------- | :------------------------------------------------------------------- |
| `SCRSIT_PLUGIN_PDF_MAGIC_PDF_PATH`             | `FilePath` | **是** | -                              | `magic-pdf` 可执行文件的完整路径。                                  |
| `SCRSIT_PLUGIN_PDF_MAGIC_PDF_OUTPUT_BASE_DIR`  | `DirPath`  | 否   | `None` (使用系统临时目录)        | 指定 `magic-pdf` 输出文件的基础目录。插件会在此目录下创建唯一子目录。 |
| `SCRSIT_PLUGIN_PDF_MAGIC_PDF_TIMEOUT_SECONDS`  | `int`      | 否   | `300` (5 分钟)                 | 调用 `magic-pdf` 的最大等待时间（秒）。                              |
| `SCRSIT_PLUGIN_PDF_MAGIC_PDF_EXTRA_ARGS`       | `str`      | 否   | `None`                         | 传递给 `magic-pdf` 的额外命令行参数字符串 (例如 `--some-flag value`)。 |
| `SCRSIT_PLUGIN_PDF_LARGE_FILE_THRESHOLD_MB`    | `float`    | 否   | `500.0`                        | 文件大小警告阈值(MB)。超过此大小会打日志。设为 `None` 关闭检查。      |
| `SCRSIT_PLUGIN_PDF_CLEANUP_MAGIC_PDF_OUTPUT`   | `bool`     | 否   | `True`                         | 是否在解析完成后自动清理 `magic-pdf` 的输出目录。                   |

**示例 `.env` 文件:**

```dotenv
SCRSIT_PLUGIN_PDF_MAGIC_PDF_PATH=/usr/local/bin/magic-pdf
SCRSIT_PLUGIN_PDF_MAGIC_PDF_TIMEOUT_SECONDS=600
SCRSIT_PLUGIN_PDF_CLEANUP_MAGIC_PDF_OUTPUT=false # 调试时可以设置为 false 保留输出```

## 使用方式

该插件实现了 `scrsit.core.interfaces.BaseParser` 接口。通常，你不需要直接实例化或调用这个插件。`scrsit` 的核心框架（如 `PluginManager` 或 `IngestionWorkflow`）会自动发现、加载并在需要处理 PDF 文件时调用此插件的 `parse` 方法。

```python
# 伪代码示例：框架如何使用
from scrsit.core.plugin_manager import PluginManager

manager = PluginManager() # 假设管理器已初始化并发现插件
pdf_parser = manager.get_plugin("pdf", plugin_type="parsers") # 获取 PDF 解析器实例

# 假设 file_source 是 PDF 文件路径或 IO 流
document: Document = pdf_parser.parse(file_source)

# 后续处理 document 对象...
```

## 插件注册

为了让 `scrsit` 核心框架能够发现此插件，它需要在项目的 `pyproject.toml` 文件中通过 entry point 进行注册：

```toml
# pyproject.toml (Poetry 示例)

[tool.poetry.plugins."scrsit.parsers"]
"pdf" = "scrsit.plugins.parsers.pdf:PdfParser"
```

这里的 `"scrsit.parsers"` 是插件类型组，`"pdf"` 是此插件的唯一名称，`"scrsit.plugins.parsers.pdf:PdfParser"` 指向实现了 `BaseParser` 接口的 `PdfParser` 类。

## 输出映射详情

当前版本的映射逻辑主要关注以下 `magic-pdf` 输出内容：

*   **文档元数据**: 页数 (`pdf_info` 列表长度), `magic-pdf` 版本 (`_version_name`)。
*   **整体文本内容**: 从 `pdf_info` -> `para_blocks` -> `lines` -> `spans` (type=`text`) 提取 `content` 并拼接。
*   **图片**: 从 `para_blocks` (type=`image`) -> `lines` -> `spans` (type=`image`) 获取 `img_path`，读取图片内容存入 `Picture.content`。尝试关联 `image_caption`/`footnote` 作为 `Picture.description`。
*   **表格**: 从 `para_blocks` (type=`table`) 创建 `Table` 对象，记录 bbox、页面号，并尝试关联 `table_caption`/`footnote`。表格内容本身未解析。
*   **行间公式**: 从 `pdf_info` -> `interline_equations` 块，查找 `model.json` 中对应 bbox 和 category_id=8 的 `layout_dets`，提取 `latex` 字段存入 `Formula.raw`。如果找不到 LaTeX，则使用 `middle.json` 中 span 的 `content`。

## 错误处理

插件定义了特定的异常类：

*   `PdfParsingError`: PDF 解析过程中的通用错误。
*   `MagicPdfExecutionError`: 调用 `magic-pdf` 外部命令失败（如找不到命令、执行超时、返回非零码）。
*   `MagicPdfOutputError`: `magic-pdf` 输出文件缺失或无法解析（如 JSON 格式错误）。

所有插件内部捕获的异常最终会以 `scrsit.core.exceptions.ParsingError` 的形式重新抛出，以便上层工作流统一处理。详细错误信息会记录在日志中。

## 故障排查

如果 PDF 解析失败，请检查以下方面：

1.  **日志文件**: 查看 `scrsit` 应用的日志，特别是与 `scrsit.plugins.parsers.pdf.parser` 相关的条目，获取详细错误信息和堆栈跟踪。
2.  **`magic-pdf` 路径**: 确认 `SCRSIT_PLUGIN_PDF_MAGIC_PDF_PATH` 环境变量设置正确，指向有效的、可执行的 `magic-pdf` 文件。
3.  **`magic-pdf` 依赖**: 确保 `magic-pdf` 本身及其所有依赖项已正确安装并且能在当前环境运行。可以尝试在命令行手动运行 `magic-pdf` 处理一个简单的 PDF 文件看是否成功。
4.  **权限**: 确保运行 `scrsit` 的用户有权限执行 `magic-pdf`，并有权限读写输入文件和指定的（或临时的）输出目录。
5.  **超时**: 如果遇到超时错误 (`MagicPdfExecutionError: magic-pdf 执行超时`)，尝试增加 `SCRSIT_PLUGIN_PDF_MAGIC_PDF_TIMEOUT_SECONDS` 的值，特别是对于大型或复杂的 PDF 文件。
6.  **`magic-pdf` 输出**: 如果配置了 `SCRSIT_PLUGIN_PDF_CLEANUP_MAGIC_PDF_OUTPUT=false`，检查 `magic-pdf` 输出目录中的文件 (`*_model.json`, `*_middle.json`, `*_layout.pdf` 等) 是否正常生成，内容是否符合预期。这有助于判断问题是出在 `magic-pdf` 本身还是在后续的 JSON 解析阶段。
7.  **输入文件**: 确认输入的 PDF 文件本身没有损坏。

## 局限性与未来工作

*   **结构化内容**: 当前未实现将 `magic-pdf` 的布局信息（如 `layout_bboxes` 或标题信息）转换为 `Document.structured_content`。
*   **表格内容提取**: 未实现对 `Table` 对象内容的结构化提取（例如，通过 OCR 表格图片或解析 HTML/LaTeX 输出）。
*   **链接与引用**: 未解析文档中的超链接 (`Link`) 或文献引用 (`Reference`)。
*   **行内公式**: `middle.json` 中的行内公式 (`inline_equation`) span 目前被忽略，未提取或转换为 `Formula`。
*   **映射逻辑**: `_map_to_document` 中的映射逻辑可能需要根据 `magic-pdf` 的版本更新或更具体的需求进行调整和增强。例如，更精确的标题、列表项识别，以及更复杂的元素关联逻辑。
*   **文件切分**: 当前只对大文件进行警告，未实现基于大小或页数的自动切分预处理。