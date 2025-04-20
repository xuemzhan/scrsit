# src/scrsit/plugins/parsers/pdf/config.py
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
from pydantic_settings import BaseSettings
from pydantic import Field, DirectoryPath, FilePath, ValidationError
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
        default=3600, # 默认 30 分钟超时
        description="调用 magic-pdf 的最大等待时间（秒）。"
    )
    magic_pdf_extra_args: Optional[str] = Field(
        default=None,
        description="传递给 magic-pdf 的额外命令行参数字符串。"
    )

    magic_pdf_result_dir: Optional[DirectoryPath] = Field(
        default=None,
        description="magic-pdf 结果目录。"
        # 注意：此字段在实际使用中可能会被覆盖或动态生成。
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

# ================================================================
#  测试代码区域
# ================================================================
if __name__ == "__main__":
    print("=" * 30)
    print("开始测试 PdfParserSettings")
    print("=" * 30)

    test_results = {'passed': 0, 'failed': 0}
    test_env_prefix = "SCRSIT_PLUGIN_PDF_" # 与 Config 中一致

    # --- 辅助函数和资源准备 ---
    temp_dir_obj = tempfile.TemporaryDirectory()
    temp_dir = Path(temp_dir_obj.name)
    dummy_executable_path = temp_dir / "dummy_magic_pdf"
    dummy_output_dir_path = temp_dir / "dummy_output"

    try:
        # 创建一个临时的假可执行文件用于路径验证
        dummy_executable_path.touch(mode=0o755, exist_ok=True) # mode=0o755 模拟可执行
        print(f"创建了临时可执行文件: {dummy_executable_path}")
        # 创建一个临时的假输出目录用于路径验证
        dummy_output_dir_path.mkdir(exist_ok=True)
        print(f"创建了临时输出目录: {dummy_output_dir_path}")

        # --- 测试场景 ---

        # 1. 测试只提供必需项，检查默认值
        print("\n--- 测试 1: 只提供必需项 (检查默认值) ---")
        test_env_1 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
        }
        # 使用 patch.dict 临时修改环境变量，并用 clear=True 清除其他变量
        with patch.dict(os.environ, test_env_1, clear=True):
            try:
                settings = PdfParserSettings()
                print("加载成功!")
                print(f"  magic_pdf_path = {settings.magic_pdf_path}")
                print(f"  magic_pdf_output_base_dir = {settings.magic_pdf_output_base_dir}")
                print(f"  magic_pdf_timeout_seconds = {settings.magic_pdf_timeout_seconds}")
                print(f"  large_file_threshold_mb = {settings.large_file_threshold_mb}")
                print(f"  cleanup_magic_pdf_output = {settings.cleanup_magic_pdf_output}")
                assert settings.magic_pdf_path == dummy_executable_path
                assert settings.magic_pdf_output_base_dir is None
                assert settings.magic_pdf_timeout_seconds == 300
                assert settings.large_file_threshold_mb == 500.0
                assert settings.cleanup_magic_pdf_output is True
                assert settings.magic_pdf_extra_args is None
                print("测试 1: PASS")
                test_results['passed'] += 1
            except ValidationError as e:
                print(f"测试 1: FAIL - 加载失败: {e}")
                test_results['failed'] += 1
            except Exception as e:
                print(f"测试 1: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 2. 测试通过环境变量覆盖所有字段
        print("\n--- 测试 2: 通过环境变量覆盖所有字段 ---")
        test_env_2 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
            f"{test_env_prefix}MAGIC_PDF_OUTPUT_BASE_DIR": str(dummy_output_dir_path),
            f"{test_env_prefix}MAGIC_PDF_TIMEOUT_SECONDS": "600",
            f"{test_env_prefix}MAGIC_PDF_EXTRA_ARGS": "--fast --ocr",
            f"{test_env_prefix}LARGE_FILE_THRESHOLD_MB": "1024.5",
            f"{test_env_prefix}CLEANUP_MAGIC_PDF_OUTPUT": "false", # 测试布尔值 'false'
        }
        with patch.dict(os.environ, test_env_2, clear=True):
            try:
                settings = PdfParserSettings()
                print("加载成功!")
                print(f"  magic_pdf_path = {settings.magic_pdf_path}")
                print(f"  magic_pdf_output_base_dir = {settings.magic_pdf_output_base_dir}")
                print(f"  magic_pdf_timeout_seconds = {settings.magic_pdf_timeout_seconds}")
                print(f"  magic_pdf_extra_args = {settings.magic_pdf_extra_args}")
                print(f"  large_file_threshold_mb = {settings.large_file_threshold_mb}")
                print(f"  cleanup_magic_pdf_output = {settings.cleanup_magic_pdf_output}")
                assert settings.magic_pdf_path == dummy_executable_path
                assert settings.magic_pdf_output_base_dir == dummy_output_dir_path
                assert settings.magic_pdf_timeout_seconds == 600
                assert settings.magic_pdf_extra_args == "--fast --ocr"
                assert settings.large_file_threshold_mb == 1024.5
                assert settings.cleanup_magic_pdf_output is False
                print("测试 2: PASS")
                test_results['passed'] += 1
            except ValidationError as e:
                print(f"测试 2: FAIL - 加载失败: {e}")
                test_results['failed'] += 1
            except Exception as e:
                print(f"测试 2: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 3. 测试缺少必需项
        print("\n--- 测试 3: 缺少必需项 (magic_pdf_path) ---")
        test_env_3 = {} # 不设置任何变量
        with patch.dict(os.environ, test_env_3, clear=True):
            try:
                settings = PdfParserSettings()
                print(f"测试 3: FAIL - 竟然加载成功了: {settings.model_dump()}")
                test_results['failed'] += 1
            except ValidationError as e:
                print(f"测试 3: PASS - 成功捕获 ValidationError: {e}")
                test_results['passed'] += 1
            except Exception as e:
                print(f"测试 3: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 4. 测试类型错误
        print("\n--- 测试 4: 无效类型 (timeout_seconds) ---")
        test_env_4 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
            f"{test_env_prefix}MAGIC_PDF_TIMEOUT_SECONDS": "not-an-integer",
        }
        with patch.dict(os.environ, test_env_4, clear=True):
            try:
                settings = PdfParserSettings()
                print(f"测试 4: FAIL - 竟然加载成功了: {settings.model_dump()}")
                test_results['failed'] += 1
            except ValidationError as e:
                print(f"测试 4: PASS - 成功捕获 ValidationError: {e}")
                test_results['passed'] += 1
            except Exception as e:
                print(f"测试 4: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 5. 测试路径验证（文件不存在）
        print("\n--- 测试 5: 路径验证 - 文件不存在 (magic_pdf_path) ---")
        non_existent_file = temp_dir / "non_existent_file"
        test_env_5 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(non_existent_file),
        }
        with patch.dict(os.environ, test_env_5, clear=True):
            try:
                # 确保文件确实不存在
                if non_existent_file.exists():
                     non_existent_file.unlink()

                settings = PdfParserSettings()
                print(f"测试 5: FAIL - 竟然加载成功了（可能Pydantic路径验证行为有变?）: {settings.model_dump()}")
                test_results['failed'] += 1
            except ValidationError as e:
                # 检查错误消息是否与路径不存在相关
                if "Path does not point to a file" in str(e) or "file_path_does_not_exist" in str(e):
                     print(f"测试 5: PASS - 成功捕获 ValidationError (文件不存在): {e}")
                     test_results['passed'] += 1
                else:
                    print(f"测试 5: FAIL - 捕获了 ValidationError，但原因不匹配: {e}")
                    test_results['failed'] += 1
            except Exception as e:
                print(f"测试 5: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 6. 测试路径验证（目录不存在）
        print("\n--- 测试 6: 路径验证 - 目录不存在 (magic_pdf_output_base_dir) ---")
        non_existent_dir = temp_dir / "non_existent_dir"
        test_env_6 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
            f"{test_env_prefix}MAGIC_PDF_OUTPUT_BASE_DIR": str(non_existent_dir),
        }
        with patch.dict(os.environ, test_env_6, clear=True):
            try:
                 # 确保目录确实不存在
                 if non_existent_dir.exists():
                     non_existent_dir.rmdir() # rmdir 用于空目录

                 settings = PdfParserSettings()
                 print(f"测试 6: FAIL - 竟然加载成功了（可能Pydantic路径验证行为有变?）: {settings.model_dump()}")
                 test_results['failed'] += 1
            except ValidationError as e:
                 # 检查错误消息是否与目录不存在相关
                 if "Path does not point to a directory" in str(e) or "dir_path_does_not_exist" in str(e):
                     print(f"测试 6: PASS - 成功捕获 ValidationError (目录不存在): {e}")
                     test_results['passed'] += 1
                 else:
                    print(f"测试 6: FAIL - 捕获了 ValidationError，但原因不匹配: {e}")
                    test_results['failed'] += 1
            except Exception as e:
                print(f"测试 6: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

        # 7. 测试布尔值处理
        print("\n--- 测试 7: 布尔值处理 (cleanup_magic_pdf_output) ---")
        results_7 = []
        for bool_val_str, expected_bool in [('true', True), ('1', True), ('yes', True), # Pydantic 通常支持这些
                                            ('false', False), ('0', False), ('no', False),
                                            ('TRUE', True), ('FALSE', False)]: # 大小写不敏感
            test_env_7 = {
                f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
                f"{test_env_prefix}CLEANUP_MAGIC_PDF_OUTPUT": bool_val_str,
            }
            with patch.dict(os.environ, test_env_7, clear=True):
                try:
                    settings = PdfParserSettings()
                    assert settings.cleanup_magic_pdf_output is expected_bool
                    results_7.append(True)
                    print(f"  '{bool_val_str}' -> {settings.cleanup_magic_pdf_output} (预期 {expected_bool}): PASS")
                except Exception as e:
                    results_7.append(False)
                    print(f"  '{bool_val_str}' -> 失败: {e}")
        if all(results_7):
            print("测试 7: PASS")
            test_results['passed'] += 1
        else:
            print("测试 7: FAIL (至少一个布尔值解析失败)")
            test_results['failed'] += 1


        # 8. 测试忽略额外变量
        print("\n--- 测试 8: 忽略额外环境变量 ---")
        test_env_8 = {
            f"{test_env_prefix}MAGIC_PDF_PATH": str(dummy_executable_path),
            f"{test_env_prefix}SOME_UNDEFINED_VARIABLE": "should_be_ignored",
        }
        with patch.dict(os.environ, test_env_8, clear=True):
            try:
                settings = PdfParserSettings()
                # 检查未定义的变量是否没有成为属性
                assert not hasattr(settings, 'some_undefined_variable')
                print("加载成功，并且未定义的变量被忽略。")
                print("测试 8: PASS")
                test_results['passed'] += 1
            except ValidationError as e:
                print(f"测试 8: FAIL - 加载失败: {e}")
                test_results['failed'] += 1
            except Exception as e:
                print(f"测试 8: FAIL - 发生意外错误: {e}")
                test_results['failed'] += 1

    finally:
        # --- 清理临时资源 ---
        print("\n--- 清理临时资源 ---")
        try:
            temp_dir_obj.cleanup()
            print(f"已清理临时目录: {temp_dir_obj.name}")
        except Exception as e:
            print(f"警告: 清理临时目录 {temp_dir_obj.name} 时出错: {e}")

    # --- 测试总结 ---
    print("\n" + "=" * 30)
    print("测试总结")
    print("=" * 30)
    print(f"测试通过: {test_results['passed']}")
    print(f"测试失败: {test_results['failed']}")
    print("=" * 30)

    # 如果有失败，以非零状态码退出，方便 CI/CD
    if test_results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)