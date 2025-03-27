# SCRSIT - AI 驱动的需求解读系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- 示例 Badge，请替换为你项目的实际 License -->
<!-- 可以添加其他 Badge，例如 Build Status, Coverage 等 -->

**SCRSIT (Source Requirement Interpretation System)** 是一个基于 AI 的系统，旨在自动化地解读、分析和管理来自多种格式文档（如 PDF, Word, Markdown 等）的客户原始需求。它通过模块化和插件化的架构，提供灵活、可扩展的需求处理能力。

## ✨ 主要特性

*   **模块化与插件化:** 核心框架与具体功能实现解耦，易于扩展和维护。支持通过插件添加新的文档格式解析、AI 模型、存储后端和分析功能。
*   **多种文档格式支持:** 通过插件支持解析 PDF, Word (.docx), Markdown, HTML, PowerPoint (.ppt), Excel (.xlsx), 图片, 纯文本等多种常见格式。
*   **AI 驱动的分析:** 利用大型语言模型 (LLM) 和其他 AI 技术进行：
    *   内容分块 (Chunking)
    *   向量嵌入 (Embedding) 生成
    *   实体识别 (Entity Extraction)
    *   关系抽取 (Relationship Extraction)
    *   关键词提取 (Keyword Extraction)
    *   需求评审（完整性、一致性、清晰度等）
    *   变更提议生成
*   **灵活的工作流:** 内置可配置的文档摄入 (Ingestion)、分析 (Analysis)、检索 (Retrieval) 和比较 (Comparison) 工作流。
*   **异步优先 (Async First):** 核心组件和工作流采用异步设计，以提高处理 I/O 密集型任务（文件处理、API调用、数据库交互）的性能和吞吐量。
*   **可配置性:** 通过环境变量和配置文件 (`.env`) 灵活选择和配置使用的插件（解析器、LLM、向量数据库、文档存储等）和工作流参数。
*   **统一数据模型:** 定义了标准化的核心数据模型 (`Document`, `Chunk`, `Entity`, `Relationship` 等) 用于系统内部数据流转。
*   **API & CLI 接口:** 提供 RESTful API (基于 FastAPI) 和命令行接口 (CLI) 用于与系统交互。

## 🏗️ 架构概览

系统采用分层和插件化的架构：

1.  **核心框架 (`src/scrsit/core`)**:
    *   定义所有插件必须遵守的接口 (`interfaces`)。
    *   定义核心数据模型 (`document/models.py`)。
    *   提供插件管理器 (`plugin_manager.py`)，负责发现、加载和管理插件。
    *   包含核心业务逻辑编排的工作流 (`workflows`)。
    *   处理配置加载 (`config`) 和通用工具 (`utils`)。
    *   定义标准异常 (`exceptions`)。
2.  **插件实现 (`src/scrsit/plugins` 或第三方包)**:
    *   提供对核心接口的具体实现，例如 `PdfParser`, `OpenAIProvider`, `WeaviateVectorStore` 等。
    *   通过 Python 的 [entry points](https://packaging.python.org/en/latest/specifications/entry-points/) 机制在 `pyproject.toml` 中声明，以便核心框架发现。
3.  **应用层 (`src/scrsit/api`, `src/scrsit/cli`)**:
    *   提供面向用户的接口（HTTP API 或命令行）。
    *   调用核心工作流和插件管理器来完成用户请求。

详细架构设计请参考 `docs/architecture.md` (如果存在)。

## 📁 目录结构

```
scrsit/
├── pyproject.toml          # 项目配置与依赖，关键的插件入口点声明
├── README.md               # 就是你正在看的这个文件
├── LICENSE                 # 项目许可证
├── .gitignore              # Git 忽略配置
├── .env.example            # 环境变量示例文件
├── src/                    # 主要源代码
│   └── scrsit/
│       ├── core/           # [核心] 框架核心 (接口, 模型, 工作流, 插件管理)
│       ├── plugins/        # [插件] 内置插件实现 (解析器, 存储, LLM等)
│       ├── api/            # [应用] FastAPI 应用和路由
│       ├── cli/            # [应用] 命令行接口实现
│       └── __main__.py     # CLI 或 API 启动入口 (可选)
├── tests/                  # 测试代码
├── docs/                   # 文档
├── data/                   # 示例/测试数据
└── notebooks/              # Jupyter Notebooks (示例, 实验)
```

## 🚀 快速开始

### 1. 环境准备

*   Python 3.9+
*   [Poetry](https://python-poetry.org/) (推荐) 或 pip 用于依赖管理。
*   (可选) Git 用于克隆代码库。

### 2. 安装

```bash
# 1. 克隆代码库 (如果需要)
git clone https://your-repository-url/scrsit.git
cd scrsit

# 2. (推荐使用 Poetry) 安装依赖
# 这会自动创建一个虚拟环境并安装所有依赖项
poetry install

# 或者 (使用 pip 和 venv)
# python -m venv venv
# source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows
# pip install -e .          # 安装项目及其依赖
```

### 3. 配置

系统配置通过环境变量加载，通常定义在项目根目录的 `.env` 文件中。

```bash
# 1. 复制示例配置文件
cp .env.example .env

# 2. 编辑 .env 文件
# 根据需要修改以下配置项：
# - AI 服务提供商的 API 密钥 (例如 SCRSIT_LLM_PROVIDER_CONFIG__OPENAI__API_KEY)
# - 数据库连接字符串 (例如 SCRSIT_PERSISTENCE_CONFIG__POSTGRESQL__DATABASE_URL)
# - 选择使用的默认插件 (例如 SCRSIT_DEFAULT_EMBEDDER="openai")
# - 其他插件特定配置...

# 查看 core/config/settings.py 和 .env.example 获取所有可用配置项。
```

### 4. 运行

#### 启动 API 服务 (FastAPI)

```bash
# 使用 uvicorn 启动 (在项目根目录下运行)
# --reload 会在代码变动时自动重启，适合开发环境
uvicorn scrsit.api.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后，可以通过浏览器访问 `http://localhost:8000/docs` 查看和交互 API 文档 (Swagger UI)。

#### 使用命令行接口 (CLI)

```bash
# 查看可用命令
python -m scrsit --help

# 示例：摄入一个文档
python -m scrsit ingest ./data/sample_docs/my_requirement.pdf

# 示例：触发特定文档的分析 (假设已摄入)
python -m scrsit analyze <document_id> --tasks entity_extraction keyword_extraction

# 示例：进行语义搜索
python -m scrsit search "告诉我关于用户登录的需求"
```

## ✅ 运行测试

```bash
# 确保已安装开发依赖 (poetry install 或 pip install -e '.[test]')
pytest tests/
```

## 🧩 开发插件

SCRSIT 的核心优势在于其插件系统。开发新插件通常涉及以下步骤：

1.  **选择接口:** 从 `src/scrsit/core/interfaces/` 中选择一个或多个需要实现的插件接口 (例如 `BaseParser`, `BaseEmbedder`, `BaseVectorStore`)。
2.  **实现接口:** 创建一个新的 Python 类，继承所选接口并实现其抽象方法。
3.  **放置代码:**
    *   对于内置插件，可以放在 `src/scrsit/plugins/` 下相应的子目录中。
    *   对于第三方插件，可以创建独立的 Python 包。
4.  **声明入口点:** 在你的包的 `pyproject.toml` 文件中，使用 `[tool.poetry.plugins."scrsit.<plugin_type>"]` (或类似工具的配置) 来声明插件的入口点。例如，为 PDF 解析器声明：
    ```toml
    [tool.poetry.plugins."scrsit.parsers"]
    "my_pdf_parser" = "my_package.parsers.pdf:MyPdfParser"
    ```
    其中 `<plugin_type>` 对应 `core/plugin_manager.py` 中 `PLUGIN_GROUPS` 的键 (如 `parsers`, `embedders`, `vector_stores` 等)。
5.  **添加配置 (可选):** 如果插件需要配置，可以在 `core/config/settings.py` 中的 `AppSettings` 里添加相应的配置模型（通常继承自 `PluginSetting`）。
6.  **编写测试:** 为你的插件编写单元测试和集成测试。

更详细的插件开发指南请参考 `docs/plugins/developing_plugins.md` (如果存在)。

## 🤝 贡献

欢迎各种形式的贡献！请先阅读 `CONTRIBUTING.md` (如果存在) 了解提交流程、代码规范等。

*   发现 Bug 或有功能建议？请提交 [Issue](https://your-repository-url/scrsit/issues)。
*   想要贡献代码？请 Fork 本仓库并发起 [Pull Request](https://your-repository-url/scrsit/pulls)。

## 📄 许可证

本项目采用 [Apache License Version 2.0] 许可证授权。详情请参阅 [LICENSE](LICENSE) 文件。
