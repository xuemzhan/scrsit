# scrsit - Smart Customer Requirements Interpretation Tool

This project implements an AI system designed to interpret customer requirements based on various input formats and design principles. It aims to help system engineers analyze and process customer needs efficiently.

## Project Structure

The project follows a modular structure, with core logic residing in the `src` directory. Key modules include:

- `document`: Handles the representation and processing of different document types.
- `parser`: Contains classes for parsing various input formats.
- `analyzer`: Includes modules for analyzing the content and structure of requirements.
- `requirement`: Manages customer and platform requirements.
- `comparator`: Provides functionality for comparing requirements and documents.
- `proposal_generator`: Generates change proposals based on requirement analysis.
- `reviewer`: Offers tools for reviewing system requirements.
- `knowledge_base`: Stores industry-specific knowledge and compliance rules.
- `utils`: Contains utility functions and configuration loading.

## Project Structure
```plaintext
scrsit/
├── pyproject.toml          # Poetry 项目配置文件，定义了项目依赖、构建设置等
├── README.md               # 项目的说明文档，包含项目的概述、结构、使用方法等
├── LICENSE                 # 项目的许可证文件
├── .gitignore              # 指定 Git 仓库应该忽略的文件和目录
├── src/                    # 项目的源代码目录
│   └── scrsit/ #        项目的主要包目录
│       ├── __init__.py     # 标记 your_project_package 目录为一个 Python 包
│       ├── core/           # 包含核心业务逻辑的模块
│       │   ├── __init__.py # 标记 core 目录为一个 Python 包
│       │   ├── document/   # 负责处理文档表示和操作的模块
│       │   │   ├── __init__.py         # 标记 document 目录为一个 Python 包
│       │   │   ├── base_document.py  # 定义文档模块的基础抽象类和数据结构（如 Document、Chunk、Entity 等）
│       │   │   ├── pdf_document.py   # 实现了 PDF 文档的具体类，继承自 base_document.Document
│       │   │   ├── markdown_document.py # 实现了 Markdown 文档的具体类，继承自 base_document.Document
│       │   │   ├── html_document.py  # 实现了 HTML 文档的具体类，继承自 base_document.Document
│       │   │   ├── excel_document.py # 实现了 Excel 文档的具体类，继承自 base_document.Document
│       │   │   ├── word_document.py  # 实现了 Word 文档的具体类，继承自 base_document.Document
│       │   │   ├── ppt_document.py   # 实现了 PPT 文档的具体类，继承自 base_document.Document
│       │   │   ├── picture_document.py # 实现了图片文档的具体类，继承自 base_document.Document
│       │   │   ├── text_document.py  # 实现了纯文本文档的具体类，继承自 base_document.Document
│       │   ├── parser/     # 负责解析不同文档格式的模块
│       │   │   ├── __init__.py         # 标记 parser 目录为一个 Python 包
│       │   │   ├── base_parser.py    # 定义文档解析器的基础抽象类（BaseParser）
│       │   │   ├── pdf_parser.py     # 使用 mineru 和 ocrmypdf 解析 PDF 文档
│       │   │   ├── markdown_parser.py # 解析 Markdown 文档
│       │   │   ├── html_parser.py    # 使用 BeautifulSoup 解析 HTML 文档
│       │   │   ├── excel_parser.py   # 使用 openpyxl 解析 Excel 文档
│       │   │   ├── word_parser.py    # 使用 python-docx 解析 Word 文档
│       │   │   ├── ppt_parser.py     # 使用 python-pptx 解析 PPT 文档
│       │   │   ├── picture_parser.py # 使用 Pillow 和 pytesseract（或 paddleocr）解析图片
│       │   │   ├── text_parser.py    # 解析纯文本文件
│       │   ├── analyzer/   # 负责分析文档内容和结构的模块
│       │   │   ├── __init__.py         # 标记 analyzer 目录为一个 Python 包
│       │   │   ├── base_analyzer.py  # 定义分析器的基础抽象类（BaseAnalyzer）
│       │   │   ├── content_analyzer.py # 分析文档或需求的内容（例如字数、句数等）
│       │   │   ├── change_analyzer.py  # 分析文档或需求中潜在的变更
│       │   ├── requirement/ # 负责管理客户和平台需求的模块
│       │   │   ├── __init__.py         # 标记 requirement 目录为一个 Python 包
│       │   │   ├── base_requirement.py # 定义需求的基础抽象类（BaseRequirement）
│       │   │   ├── customer_requirement.py # 表示客户需求的具体类
│       │   │   ├── platform_requirement.py # 表示平台需求的具体类
│       │   │   ├── requirement_manager.py # 管理需求的存储和检索
│       │   ├── comparator/  # 负责比较文档和需求的模块
│       │   │   ├── __init__.py         # 标记 comparator 目录为一个 Python 包
│       │   │   ├── base_comparator.py # 定义比较器的基础抽象类（BaseComparator）
│       │   │   ├── document_comparator.py # 比较两个文档的差异
│       │   │   ├── requirement_comparator.py # 比较两个需求的差异
│       │   ├── proposal_generator/ # 负责生成变更提议的模块
│       │   │   ├── __init__.py         # 标记 proposal_generator 目录为一个 Python 包
│       │   │   ├── change_proposal_generator.py # 基于分析和比较结果生成变更提议
│       │   ├── reviewer/     # 负责评审系统需求的模块
│       │   │   ├── __init__.py         # 标记 reviewer 目录为一个 Python 包
│       │   │   ├── requirement_reviewer.py # 根据预定义规则评审需求
│       │   ├── knowledge_base/ # 负责存储和访问行业知识的模块
│       │   │   ├── __init__.py         # 标记 knowledge_base 目录为一个 Python 包
│       │   │   ├── industry_knowledge.py # 存储和提供行业特定知识
│       │   │   ├── compliance_rules.py # 存储和应用合规性规则
│       │   ├── utils/        # 包含实用工具函数和类的模块
│       │   │   ├── __init__.py         # 标记 utils 目录为一个 Python 包
│       │   │   ├── file_utils.py       # 文件操作相关的实用函数
│       │   │   ├── text_utils.py       # 文本处理相关的实用函数
│       │   │   ├── config_loader.py    # 加载和管理配置信息的模块
│       ├── models/         # 包含应用程序使用的数据模型（Pydantic models）
│       │   ├── __init__.py     # 标记 models 目录为一个 Python 包
│       │   ├── customer_requirement_model.py # 客户需求的数据模型
│       │   ├── platform_requirement_model.py # 平台需求的数据模型
│       │   ├── change_task_model.py    # 变更任务的数据模型
│       │   ├── difference_report_model.py # 差异报告的数据模型
│       │   ├── system_requirement_model.py # 系统需求的数据模型
│       ├── database/       # 负责数据库交互的模块
│       │   ├── __init__.py     # 标记 database 目录为一个 Python 包
│       │   ├── database_connector.py # 处理数据库连接
│       │   ├── models.py       # 定义数据库模型（如果使用 ORM）
│       ├── api/            # 包含 API 接口的模块（使用 FastAPI）
│       │   ├── __init__.py     # 标记 api 目录为一个 Python 包
│       │   ├── main.py         # FastAPI 应用程序的主要入口
│       │   ├── endpoints/      # 包含不同的 API 接口端点
│       │   │   ├── __init__.py # 标记 endpoints 目录为一个 Python 包
│       │   │   ├── requirement_analysis_api.py # 处理需求分析相关的 API 端点
│       │   │   ├── requirement_review_api.py # 处理需求评审相关的 API 端点
│       ├── cli.py            # 应用程序的命令行接口
├── tests/                  # 包含项目的测试代码
│   ├── __init__.py     # 标记 tests 目录为一个 Python 包
│   ├── core/           # 包含核心模块的测试
│   │   ├── __init__.py # 标记 core 测试目录为一个 Python 包
│   │   ├── document/   # 包含 document 模块的测试
│   │   │   ├── __init__.py             # 标记 document 测试目录为一个 Python 包
│   │   │   ├── test_base_document.py  # 测试 base_document.py 中的基础类
│   │   │   ├── test_pdf_document.py   # 测试 pdf_document.py
│   │   │   ├── test_markdown_document.py # 测试 markdown_document.py
│   │   │   └── ...                 # 其他文档类型的测试文件
│   ├── api/            # 包含 API 接口的测试
│   │   ├── __init__.py # 标记 api 测试目录为一个 Python 包
│   │   ├── test_endpoints/ # 包含 API 端点的测试
│   │   │   ├── __init__.py # 标记 endpoints 测试目录为一个 Python 包
│   │   │   └── ...         # 具体端点的测试文件
├── docs/                   # 包含项目的文档（使用 Sphinx）
│   ├── source/         # Sphinx 文档源文件
│   │   ├── index.rst     # Sphinx 文档的首页
│   │   ├── modules.rst   # Sphinx 自动生成的模块文档
│   │   ├── ...           # 其他文档文件
│   ├── Makefile          # 用于构建 Sphinx 文档的 Makefile
├── data/                   # 包含项目使用的数据文件（例如示例需求文档）
│   ├── example_customer_requirements/ # 示例客户需求文档
│   │   ├── pdf_example.pdf           # PDF 格式的示例文档
│   │   ├── word_example.docx         # Word 格式的示例文档
│   │   └── ...                       # 其他格式的示例文档
└── notebooks/              # 包含 Jupyter Notebooks，用于探索性分析和开发
```