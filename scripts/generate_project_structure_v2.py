import os

# 定义目录结构 (忽略最外层的 "scrsit" 目录)
structure = {
    "pyproject.toml": "",
    "README.md": "",
    "LICENSE": "",
    ".gitignore": "",
    ".env.example": "",
    "Makefile": "",
    "Dockerfile": "",
    "docker-compose.yml": "",
    "src": {
        "scrsit": {
            "__init__.py": "",
            "core": {
                "__init__.py": "",
                "plugin_manager.py": "",
                "exceptions.py": "",
                "interfaces": {
                    "__init__.py": "",
                    "base_parser.py": "",
                    "base_llm_provider.py": "",
                    "base_ocr_provider.py": "",
                    "base_multimodal_provider.py": "",
                    "base_store.py": "",
                    "base_document_store.py": "",
                    "base_vector_store.py": "",
                    "base_structured_store.py": "",
                    "base_chunker.py": "",
                    "base_embedder.py": "",
                    "base_analyzer.py": "",
                    "base_knowledge_provider.py": "",
                    "base_reviewer.py": "",
                    "base_proposal_generator.py": ""
                },
                "document": {
                    "__init__.py": "",
                    "models.py": ""
                },
                "workflows": {
                    "__init__.py": "",
                    "ingestion.py": "",
                    "analysis.py": "",
                    "retrieval.py": "",
                    "comparison.py": ""
                },
                "config": {
                    "__init__.py": "",
                    "settings.py": ""
                },
                "utils": {
                    "__init__.py": "",
                    "logging.py": "",
                    "helpers.py": ""
                }
            },
            "plugins": {
                "__init__.py": "",
                "parsers": {
                    "__init__.py": "",
                    "pdf": {
                        "__init__.py": "",
                        "parser.py": "",
                        "config.py": ""
                    },
                    "docx": {
                        "__init__.py": "",
                        "parser.py": "",
                        "config.py": ""
                    },
                    "markdown": {
                        "__init__.py": ""
                    },
                    "html": {
                        "__init__.py": ""
                    },
                    "ppt": {
                        "__init__.py": ""
                    },
                    "excel": {
                        "__init__.py": ""
                    },
                    "picture": {
                        "__init__.py": ""
                    },
                    "text": {
                        "__init__.py": ""
                    }
                },
                "persistence": {
                    "__init__.py": "",
                    "memory": {
                        "__init__.py": "",
                        "store.py": ""
                    },
                    "filesystem": {
                        "__init__.py": "",
                        "store.py": ""
                    },
                    "mongodb": {
                        "__init__.py": "",
                        "document_store.py": "",
                        "config.py": ""
                    },
                    "weaviate": {
                        "__init__.py": "",
                        "vector_store.py": "",
                        "config.py": ""
                    },
                    "postgresql": {
                        "__init__.py": "",
                        "structured_store.py": "",
                        "vector_store.py": "",
                        "models.py": "",
                        "config.py": ""
                    }
                },
                "llm_providers": {
                    "__init__.py": "",
                    "openai": {
                        "__init__.py": "",
                        "provider.py": "",
                        "config.py": ""
                    },
                    "huggingface": {
                        "__init__.py": "",
                        "provider.py": "",
                        "config.py": ""
                    },
                    "ocr": {
                        "__init__.py": "",
                        "paddleocr_provider.py": "",
                        "config.py": ""
                    },
                    "local_llm": {
                        "__init__.py": "",
                        "provider.py": "",
                        "config.py": ""
                    }
                },
                "chunkers": {
                    "__init__.py": "",
                    "recursive_text": {
                        "__init__.py": "",
                        "chunker.py": "",
                        "config.py": ""
                    },
                    "semantic": {
                        "__init__.py": "",
                        "chunker.py": "",
                        "config.py": ""
                    }
                },
                "embedders": {
                    "__init__.py": "",
                    "sentence_transformer": {
                        "__init__.py": "",
                        "embedder.py": "",
                        "config.py": ""
                    }
                },
                "analyzers": {
                    "__init__.py": "",
                    "entity_extraction": {
                        "__init__.py": "",
                        "analyzer.py": "",
                        "config.py": ""
                    },
                    "keyword_extraction": {
                        "__init__.py": ""
                    },
                    "change_detection": {
                        "__init__.py": ""
                    }
                }
            },
            "api": {
                "__init__.py": "",
                "main.py": "",
                "dependencies.py": "",
                "schemas.py": "",
                "routers": {
                    "__init__.py": "",
                    "documents.py": "",
                    "analysis.py": "",
                    "search.py": ""
                }
            },
            "cli": {
                "__init__.py": "",
                "main.py": "",
                "commands": {
                    "__init__.py": "",
                    "documents.py": "",
                    "analyze.py": ""
                }
            },
            "__main__.py": ""
        }
    },
    "tests": {
        "__init__.py": "",
        "conftest.py": "",
        "core": {
            "interfaces": {},
            "document": {},
            "workflows": {},
            "test_plugin_manager.py": ""
        },
        "plugins": {},
        "api": {},
        "cli": {}
    },
    "docs": {
        "index.rst": "",
        "configuration.rst": "",
        "architecture.rst": "",
        "plugins": {
            "index.rst": "",
            "developing_plugins.rst": ""
        }
    },
    "data": {
        "sample_docs": {},
        "test_fixtures": {}
    },
    "notebooks": {
        "01_parsing_example.ipynb": "",
        "02_rag_workflow_demo.ipynb": ""
    }
}

def create_structure(base_path, tree):
    for name, content in tree.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # 如果上层目录不存在则创建
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    base_dir = os.getcwd()  # 可根据需要修改基础路径
    create_structure(base_dir, structure)
    print("目录结构创建完成。")