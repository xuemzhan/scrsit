```
scrsit/
├── pyproject.toml          # [核心] 项目配置文件 (Poetry/Hatch/etc.)。定义项目元数据、依赖，并 **极其重要地** 包含 [tool.poetry.plugins."scrsit.<plugin_type>"] (或类似) 部分来声明所有插件的入口点 (entry points)。这是插件发现的关键。
├── README.md               # 项目说明，包含架构概览、安装指南、如何开发和注册新插件的说明。
├── LICENSE                 # 项目许可证。
├── .gitignore              # 指定 Git 应忽略的文件和目录。
├── .env.example            # [配置] 环境变量示例文件，指导用户如何配置数据库连接、API密钥等。实际配置通常在 .env 文件中（被 .gitignore 忽略）。
├── Makefile                # (可选) 包含常用开发命令 (如 install, test, lint, run, build, docs)。
├── Dockerfile              # (可选) 用于构建应用 Docker 镜像。
├── docker-compose.yml      # (可选) 用于本地开发或部署，编排应用服务和依赖 (如数据库, 向量存储)。
│
├── src/                    # 主要源代码目录
│   └── scrsit/             # 项目主包
│       ├── __init__.py     # 包初始化文件。
│       │
│       ├── core/           # [核心] 框架核心，不包含任何具体实现，只包含接口、核心模型、工作流和插件管理。
│       │   ├── __init__.py # 包初始化文件。
│       │   ├── plugin_manager.py # [核心] 插件管理器。负责发现 (通过 entry points)、加载、验证和提供插件实例。包含获取特定类型插件或默认插件的逻辑。
│       │   │
│       │   ├── interfaces/   # [核心] 定义所有插件必须遵守的抽象基类 (ABC) 或协议 (Protocol)。这是核心与插件之间的契约。
│       │   │   ├── __init__.py
│       │   │   ├── base_parser.py    # 定义 `BaseParser` 接口，包含 `parse(file_path_or_stream) -> Document` 等方法。
│       │   │   ├── base_llm_provider.py # 定义 `BaseLLMProvider` 接口 (可能包含 `generate`, `chat` 方法)。
│       │   │   ├── base_ocr_provider.py # 定义 `BaseOCRProvider` 接口 (`extract_text(image) -> str`)。
│       │   │   ├── base_multimodal_provider.py # 定义 `BaseMultimodalProvider` 接口 (处理文本+图像等)。
│       │   │   ├── base_store.py     # (可选) 定义非常通用的存储接口，或直接使用下面更具体的接口。
│       │   │   ├── base_document_store.py # 定义 `BaseDocumentStore` 接口 (`save(doc)`, `get(doc_id)`, `delete(doc_id)`).
│       │   │   ├── base_vector_store.py # 定义 `BaseVectorStore` 接口 (`add_embeddings`, `search`, `delete_by_ids`).
│       │   │   ├── base_structured_store.py # 定义 `BaseStructuredStore` 接口 (用于存储和查询分析结果、元数据等)。
│       │   │   ├── base_chunker.py   # 定义 `BaseChunker` 接口 (`chunk(document) -> List[Chunk]`).
│       │   │   ├── base_embedder.py  # 定义 `BaseEmbedder` 接口 (`embed(texts_or_chunks) -> List[List[float]]`).
│       │   │   ├── base_analyzer.py  # 定义 `BaseAnalyzer` 接口 (`analyze(document_or_chunk) -> AnalysisResult`).
│       │   │   ├── base_knowledge_provider.py # 定义 `BaseKnowledgeProvider` 接口 (访问行业知识、合规规则)。
│       │   │   ├── base_reviewer.py  # 定义 `BaseReviewer` 接口 (评审需求)。
│       │   │   └── base_proposal_generator.py # 定义 `BaseProposalGenerator` 接口 (生成变更提议)。
│       │   │
│       │   ├── document/     # [核心] 核心领域数据模型 (使用 Pydantic 定义)。这些是在系统内部流转的数据结构。
│       │   │   ├── __init__.py
│       │   │   └── models.py     # 定义 `Document`, `Chunk`, `Entity`, `Relationship`, `StructuredContent`, `Element`, `Formula`, `Picture`, `Table`, `Reference`, `Link` 等核心数据类。
│       │   │
│       │   ├── workflows/    # [核心] 核心业务流程/服务编排。调用插件管理器获取插件实例并执行任务。
│       │   │   ├── __init__.py
│       │   │   ├── ingestion.py  # 文档摄入工作流 (协调 Parser -> Chunker -> Embedder -> Analyzers -> Stores)。
│       │   │   ├── analysis.py   # 需求分析工作流 (协调 Analyzers, KnowledgeProvider, Reviewer)。
│       │   │   ├── retrieval.py  # 信息检索工作流 (协调 VectorStore, DocumentStore, LLMProvider for RAG)。
│       │   │   └── comparison.py # 文档/需求比较工作流。
│       │   │
│       │   ├── config/       # [配置] 核心配置加载与管理。
│       │   │   ├── __init__.py
│       │   │   └── settings.py   # 使用 Pydantic 定义应用配置模型 (如 `AppSettings`)，加载来自 .env、环境变量等的配置。包括启用的插件、全局设置等。
│       │   │
│       │   ├── exceptions.py # [核心] 定义框架的核心自定义异常 (如 `PluginNotFoundError`, `ConfigurationError`, `WorkflowError`)。
│       │   │
│       │   └── utils/        # [核心] 核心通用工具函数或类，不依赖任何具体插件实现。
│       │       ├── __init__.py
│       │       ├── logging.py    # 配置全局日志记录器。
│       │       └── helpers.py    # 通用辅助函数。
│       │
│       ├── plugins/          # [插件] 内置/第一方插件的实现。每个子目录代表一类插件，其下的子目录是具体的插件实现。
│       │   ├── __init__.py   # 插件包根目录。
│       │   │
│       │   ├── parsers/      # 文档解析器插件实现
│       │   │   ├── __init__.py
│       │   │   ├── pdf/        # PDF 解析器插件
│       │   │   │   ├── __init__.py # 导出 `PdfParser` 类。
│       │   │   │   ├── parser.py   # 实现 `core.interfaces.BaseParser` 的 `PdfParser` 类。
│       │   │   │   └── config.py   # (可选) 该插件特定的 Pydantic 配置模型 (如 OCR 引擎选择)。
│       │   │   ├── docx/       # Word 解析器插件 (类似结构)
│       │   │   │   ├── __init__.py
│       │   │   │   ├── parser.py
│       │   │   │   └── config.py
│       │   │   ├── markdown/   # Markdown 解析器插件 (...)
│       │   │   ├── html/       # HTML 解析器插件 (...)
│       │   │   ├── ppt/        # PPT 解析器插件 (...)
│       │   │   ├── excel/      # Excel 解析器插件 (...)
│       │   │   ├── picture/    # 图片解析器插件 (可能依赖 OCR Provider) (...)
│       │   │   └── text/       # 纯文本解析器插件 (...)
│       │   │
│       │   ├── persistence/    # 数据持久化插件实现
│       │   │   ├── __init__.py
│       │   │   ├── memory/       # 内存存储插件 (用于开发/测试)
│       │   │   │   ├── __init__.py # 导出 `MemoryVectorStore`, `MemoryDocumentStore` 等。
│       │   │   │   └── store.py    # 实现 `BaseVectorStore`, `BaseDocumentStore` 等接口。
│       │   │   ├── filesystem/   # 文件系统存储插件 (简单场景)
│       │   │   │   ├── __init__.py
│       │   │   │   └── store.py
│       │   │   ├── mongodb/      # MongoDB 存储插件
│       │   │   │   ├── __init__.py
│       │   │   │   ├── document_store.py # 实现 `BaseDocumentStore`。
│       │   │   │   └── config.py   # MongoDB 连接配置。
│       │   │   ├── weaviate/     # Weaviate 向量存储插件
│       │   │   │   ├── __init__.py
│       │   │   │   ├── vector_store.py # 实现 `BaseVectorStore`。
│       │   │   │   └── config.py   # Weaviate 连接配置。
│       │   │   └── postgresql/   # PostgreSQL 插件 (可同时实现结构化和向量存储)
│       │   │       ├── __init__.py
│       │   │       ├── structured_store.py # 实现 `BaseStructuredStore` (使用 SQLAlchemy)。
│       │   │       ├── vector_store.py     # 实现 `BaseVectorStore` (使用 pgvector)。
│       │   │       ├── models.py           # SQLAlchemy ORM 模型 (实现细节)。
│       │   │       └── config.py           # PostgreSQL 连接配置。
│       │   │
│       │   ├── llm_providers/ # LLM 及相关 AI 模型提供者插件
│       │   │   ├── __init__.py
│       │   │   ├── openai/
│       │   │   │   ├── __init__.py # 导出 `OpenAIProvider`。
│       │   │   │   ├── provider.py # 实现 `BaseLLMProvider`, `BaseEmbedder` (或其一)。
│       │   │   │   └── config.py   # API Key, 模型名称等配置。
│       │   │   ├── huggingface/  # Hugging Face Provider (可能用于本地模型或 Hub 模型)
│       │   │   │   ├── __init__.py
│       │   │   │   ├── provider.py
│       │   │   │   └── config.py
│       │   │   ├── ocr/          # OCR 提供者插件 (如果独立于 LLM)
│       │   │   │   ├── __init__.py
│       │   │   │   ├── paddleocr_provider.py # 示例：PaddleOCR 实现 `BaseOCRProvider`。
│       │   │   │   └── config.py
│       │   │   └── local_llm/    # 本地 LLM Provider (如 Ollama, llama.cpp 包装器)
│       │   │       ├── __init__.py
│       │   │       ├── provider.py
│       │   │       └── config.py
│       │   │
│       │   ├── chunkers/     # 分块策略插件
│       │   │   ├── __init__.py
│       │   │   ├── recursive_text/
│       │   │   │   ├── __init__.py # 导出 `RecursiveTextChunker`。
│       │   │   │   ├── chunker.py  # 实现 `BaseChunker`。
│       │   │   │   └── config.py   # chunk_size, chunk_overlap 配置。
│       │   │   └── semantic/     # 语义分块插件 (可能依赖 Embedder)
│       │   │       ├── __init__.py
│       │   │       ├── chunker.py
│       │   │       └── config.py
│       │   │
│       │   ├── embedders/    # Embedding 生成插件 (如果需要独立于 LLM Provider 管理)
│       │   │   ├── __init__.py
│       │   │   ├── sentence_transformer/
│       │   │   │   ├── __init__.py # 导出 `SentenceTransformerEmbedder`。
│       │   │   │   ├── embedder.py # 实现 `BaseEmbedder`。
│       │   │   │   └── config.py   # 模型名称, device 配置。
│       │   │
│       │   └── analyzers/    # 内容分析器插件
│       │       ├── __init__.py
│       │       ├── entity_extraction/ # 实体提取分析器
│       │       │   ├── __init__.py # 导出 `EntityExtractor`。
│       │       │   ├── analyzer.py # 实现 `BaseAnalyzer` (可能依赖 LLM Provider)。
│       │       │   └── config.py   # (可选) 特定配置，如使用的 prompt 模板。
│       │       ├── keyword_extraction/ # 关键词提取分析器 (...)
│       │       └── change_detection/ # 变更检测分析器 (...)
│       │
│       ├── api/              # [应用层] API 接口 (如 FastAPI)。与核心交互，使用核心工作流和插件管理器。
│       │   ├── __init__.py
│       │   ├── main.py       # FastAPI 应用实例创建，挂载路由，初始化核心服务 (PluginManager, Settings)。
│       │   ├── dependencies.py # 定义 FastAPI 依赖项 (如 `get_settings`, `get_plugin_manager`, `get_ingestion_workflow`)。
│       │   ├── routers/      # API 路由定义
│       │   │   ├── __init__.py
│       │   │   ├── documents.py  # 处理文档上传、状态查询、内容获取等。
│       │   │   ├── analysis.py   # 触发需求分析、内容分析等。
│       │   │   └── search.py     # 处理搜索和检索请求。
│       │   └── schemas.py    # API 的请求体和响应体的 Pydantic 模型 (DTOs)，与 `core.document.models` 解耦。
│       │
│       ├── cli/              # [应用层] 命令行接口 (如 Typer/Click)。功能类似 API 层。
│       │   ├── __init__.py
│       │   ├── main.py       # CLI 应用入口。
│       │   └── commands/     # CLI 命令实现
│       │       ├── __init__.py
│       │       ├── documents.py
│       │       └── analyze.py
│       │
│       └── __main__.py       # (可选) 允许通过 `python -m scrsit` 运行 (通常启动 CLI 或 API)。
│
├── tests/                  # 测试代码目录，结构应镜像 src/
│   ├── __init__.py
│   ├── conftest.py         # Pytest 共享 fixtures (如模拟插件、数据库连接、API client)。
│   ├── core/               # 核心模块的单元测试和集成测试
│   │   ├── interfaces/
│   │   ├── document/
│   │   ├── workflows/
│   │   └── test_plugin_manager.py
│   ├── plugins/            # 各个内置插件的单元测试和集成测试
│   │   ├── parsers/
│   │   ├── persistence/
│   │   └── ...
│   ├── api/                # API 端点的集成测试
│   └── cli/                # CLI 命令的集成测试
│
├── docs/                   # 项目文档源文件 (如 Sphinx 或 MkDocs)
│   ├── index.rst / index.md
│   ├── configuration.rst / configuration.md
│   ├── architecture.rst / architecture.md
│   └── plugins/            # 插件开发和使用文档
│       ├── index.rst / index.md
│       └── developing_plugins.rst / developing_plugins.md
│
├── data/                   # 示例输入数据、测试数据 (非代码)。
│   ├── sample_docs/        # 各种格式的示例文档。
│   └── test_fixtures/      # 测试使用的固定数据。
│
└── notebooks/              # Jupyter Notebooks 用于探索、实验和演示。
    ├── 01_parsing_example.ipynb
    └── 02_rag_workflow_demo.ipynb
```