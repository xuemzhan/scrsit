import os

# 定义目录和文件结构
structure = {
    "src": {
        "scrsit": {
            "__init__.py": "",
            "core": {
                "__init__.py": "",
                "document": {
                    "__init__.py": "",
                    "base_document.py": "",
                    "pdf_document.py": "",
                    "markdown_document.py": "",
                    "html_document.py": "",
                    "excel_document.py": "",
                    "word_document.py": "",
                    "ppt_document.py": "",
                    "picture_document.py": "",
                    "text_document.py": "",
                },
                "parser": {
                    "__init__.py": "",
                    "base_parser.py": "",
                    "pdf_parser.py": "",
                    "markdown_parser.py": "",
                    "html_parser.py": "",
                    "excel_parser.py": "",
                    "word_parser.py": "",
                    "ppt_parser.py": "",
                    "picture_parser.py": "",
                    "text_parser.py": "",
                },
                "analyzer": {
                    "__init__.py": "",
                    "base_analyzer.py": "",
                    "content_analyzer.py": "",
                    "change_analyzer.py": "",
                },
                "requirement": {
                    "__init__.py": "",
                    "base_requirement.py": "",
                    "customer_requirement.py": "",
                    "platform_requirement.py": "",
                    "requirement_manager.py": "",
                },
                "comparator": {
                    "__init__.py": "",
                    "base_comparator.py": "",
                    "document_comparator.py": "",
                    "requirement_comparator.py": "",
                },
                "proposal_generator": {
                    "__init__.py": "",
                    "change_proposal_generator.py": "",
                },
                "reviewer": {
                    "__init__.py": "",
                    "requirement_reviewer.py": "",
                },
                "knowledge_base": {
                    "__init__.py": "",
                    "industry_knowledge.py": "",
                    "compliance_rules.py": "",
                },
                "utils": {
                    "__init__.py": "",
                    "file_utils.py": "",
                    "text_utils.py": "",
                    "config_loader.py": "",
                },
            },
            "models": {
                "__init__.py": "",
                "customer_requirement_model.py": "",
                "platform_requirement_model.py": "",
                "change_task_model.py": "",
                "difference_report_model.py": "",
                "system_requirement_model.py": "",
            },
            "database": {
                "__init__.py": "",
                "database_connector.py": "",
                "models.py": "",
            },
            "api": {
                "__init__.py": "",
                "main.py": "",
                "endpoints": {
                    "__init__.py": "",
                    "requirement_analysis_api.py": "",
                    "requirement_review_api.py": "",
                },
            },
            "cli.py": "",
        },
    },
    "tests": {
        "__init__.py": "",
        "core": {
            "__init__.py": "",
            "document": {
                "__init__.py": "",
                "test_base_document.py": "",
                "test_pdf_document.py": "",
                "test_markdown_document.py": "",
            },
        },
        "api": {
            "__init__.py": "",
            "test_endpoints": {
                "__init__.py": "",
            },
        },
    },
    "docs": {
        "source": {
            "index.rst": "",
            "modules.rst": "",
        },
        "Makefile": "",
    },
    "data": {
        "example_customer_requirements": {
            "pdf_example.pdf": "",
            "word_example.docx": "",
        },
    },
    "notebooks": {},
}

# 创建目录和文件
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w") as f:
                f.write(content)

# 确保 scripts 目录存在
scripts_dir = os.path.join(os.getcwd(), "scripts")
os.makedirs(scripts_dir, exist_ok=True)

# 将脚本保存到 scripts 目录
script_path = os.path.join(scripts_dir, "generate_project_structure.py")
with open(script_path, "w") as script_file:
    script_file.write("""\"\"\"This script generates the project structure based on the README.md.\"\"\"""" + "\n" + __file__)

# 执行生成
if __name__ == "__main__":
    create_structure(".", structure)
    print(f"Project structure generated successfully!")