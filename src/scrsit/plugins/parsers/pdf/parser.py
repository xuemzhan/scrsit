# src/scrsit/plugins/parsers/pdf/parser.py

import abc
import asyncio
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, IO, List, Dict, Any, Tuple, Optional
import hashlib

from src.scrsit.core.document.models import (
    Document, DocumentType, Element, Formula, Picture, Table, Link, Reference,
    Chunk, # Chunks 通常在后续步骤生成，但基础信息可能来自解析
    StructuredContent # 结构化内容可能需要更复杂的逻辑从 layout 构建
)
from src.scrsit.core.interfaces.base_parser import BaseParser
from src.scrsit.core.exceptions import ParsingError # 使用核心定义的通用解析错误
from src.scrsit.core.utils.helpers import generate_uuid # 引入 UUID 生成器

from .config import PdfParserSettings
from .exceptions import PdfParsingError, MagicPdfExecutionError, MagicPdfOutputError


logger = logging.getLogger(__name__)

class PdfParser(BaseParser):
    """
    使用外部 magic-pdf 工具解析 PDF 文件的解析器实现。
    """
    _settings: PdfParserSettings

    def __init__(self, settings: Optional[PdfParserSettings] = None):
        """
        初始化 PDF 解析器。

        Args:
            settings: PDF 解析器的配置。如果为 None，会尝试从环境变量加载。
        """
        # 优先使用传入的 settings，否则尝试从环境变量加载
        self._settings = settings or PdfParserSettings()
        logger.info(f"PDF 解析器已初始化。Magic-PDF 路径: {self._settings.magic_pdf_path}")
        # 确保 magic_pdf_path 存在且可执行
        if not os.path.isfile(self._settings.magic_pdf_path) or not os.access(self._settings.magic_pdf_path, os.X_OK):
             raise PdfParsingError(f"magic-pdf 可执行文件未找到或不可执行: {self._settings.magic_pdf_path}")


    @property
    def supported_types(self) -> List[str]:
        """返回支持的文件类型扩展名列表。"""
        return ['pdf']

    def parse(self, file_source: Union[str, IO[bytes]], **kwargs) -> Document:
        """
        解析给定的 PDF 文件源。

        Args:
            file_source: PDF 文件的路径字符串或二进制 IO 流。
            **kwargs: 其他参数 (当前未使用，为接口兼容性保留)。

        Returns:
            解析后的核心文档对象。

        Raises:
            ParsingError: 如果解析过程中发生任何错误。
            FileNotFoundError: 如果 file_source 是路径且文件不存在。
            TypeError: 如果 file_source 类型不支持。
        """
        logger.info(f"开始解析 PDF 文件源: {file_source if isinstance(file_source, str) else 'IO Stream'}")
        input_path: Path
        temp_input_dir: Optional[tempfile.TemporaryDirectory] = None
        original_filename: str = "unknown.pdf"
        checksum: Optional[str] = None

        try:
            # 1. 处理输入源 (路径或流)，获取输入文件路径和原始文件名
            if isinstance(file_source, str):
                input_path = Path(file_source)
                if not input_path.is_file():
                    raise FileNotFoundError(f"输入文件未找到: {file_source}")
                original_filename = input_path.name
                logger.debug(f"输入源是文件路径: {input_path}")
            elif hasattr(file_source, 'read') and callable(file_source.read):
                # 如果是 IO 流，保存到临时文件
                temp_input_dir = tempfile.TemporaryDirectory(prefix="scrsit_pdf_in_")
                input_path = Path(temp_input_dir.name) / "input.pdf"
                original_filename = getattr(file_source, 'name', 'unknown.pdf') # 尝试获取流的文件名
                logger.debug(f"输入源是 IO 流，保存到临时文件: {input_path}")
                try:
                    with open(input_path, "wb") as f:
                        # 重置流指针（如果可能）
                        if hasattr(file_source, 'seek') and callable(file_source.seek):
                             try:
                                 file_source.seek(0)
                             except Exception:
                                 logger.warning("无法重置输入流指针。")
                        shutil.copyfileobj(file_source, f)
                except Exception as e:
                    raise ParsingError(f"无法将输入流写入临时文件: {e}") from e
            else:
                raise TypeError(f"不支持的文件源类型: {type(file_source)}")

            # 计算校验和
            checksum = self._calculate_checksum(input_path)
            logger.debug(f"文件校验和 (SHA1): {checksum}")

            # 2. 文件大小检查 (根据配置)
            self._check_file_size(input_path)

            # 3. 准备 magic-pdf 输出目录
            output_dir_path, temp_output_obj = self._prepare_output_directory(input_path)
            logger.debug(f"Magic-PDF 输出目录: {output_dir_path}")

            # 4. 异步运行 magic-pdf
            try:
                logger.info(f"开始调用 magic-pdf 处理文件: {input_path}")
                asyncio.run(self._run_magic_pdf(input_path, output_dir_path))
                logger.info(f"Magic-pdf 处理完成: {input_path}")
            except Exception as e:
                # 捕获 asyncio.run 可能抛出的异常以及 _run_magic_pdf 内部的异常
                raise MagicPdfExecutionError(f"执行 magic-pdf 失败: {e}") from e

            # 5. 解析 magic-pdf 输出
            logger.info(f"开始解析 magic-pdf 输出文件于: {output_dir_path}")
            model_json_path = output_dir_path / f"{input_path.stem}_model.json"
            middle_json_path = output_dir_path / f"{input_path.stem}_middle.json"

            if not model_json_path.is_file():
                 raise MagicPdfOutputError(f"未找到 magic-pdf model 输出文件: {model_json_path}")
            if not middle_json_path.is_file():
                 raise MagicPdfOutputError(f"未找到 magic-pdf middle 输出文件: {middle_json_path}")

            try:
                with open(model_json_path, 'r', encoding='utf-8') as f_model, \
                     open(middle_json_path, 'r', encoding='utf-8') as f_middle:
                    model_data = json.load(f_model)
                    middle_data = json.load(f_middle)
            except json.JSONDecodeError as e:
                raise MagicPdfOutputError(f"解析 magic-pdf JSON 输出失败: {e}") from e
            except Exception as e:
                raise MagicPdfOutputError(f"读取 magic-pdf 输出文件时出错: {e}") from e

            logger.info(f"成功解析 magic-pdf 输出文件。")

            # 6. 将解析结果映射到 Document 模型
            logger.info("开始将 magic-pdf 输出映射到核心 Document 模型...")
            document = self._map_to_document(original_filename, checksum, model_data, middle_data, output_dir_path)
            logger.info(f"Document 模型映射完成。文档 ID: {document.id}")

            return document

        except (FileNotFoundError, TypeError, ParsingError, PdfParsingError) as e:
            logger.error(f"PDF 解析失败: {e}", exc_info=True)
            # 重新抛出，以便上层可以捕获特定类型的错误
            raise ParsingError(f"PDF 解析失败: {e}") from e # 包装成通用的 ParsingError
        except Exception as e:
            logger.error(f"PDF 解析过程中发生意外错误: {e}", exc_info=True)
            raise ParsingError(f"PDF 解析过程中发生意外错误: {e}") from e # 包装成通用的 ParsingError
        finally:
            # 7. 清理临时文件和目录
            if temp_input_dir:
                try:
                    temp_input_dir.cleanup()
                    logger.debug(f"已清理临时输入目录: {temp_input_dir.name}")
                except Exception as e:
                    logger.warning(f"清理临时输入目录失败: {temp_input_dir.name}, Error: {e}")

            # 根据配置清理 magic-pdf 输出目录 (仅当它是临时创建的)
            if self._settings.cleanup_magic_pdf_output and temp_output_obj:
                try:
                    temp_output_obj.cleanup()
                    logger.debug(f"已清理临时 magic-pdf 输出目录: {temp_output_obj.name}")
                except Exception as e:
                     logger.warning(f"清理临时 magic-pdf 输出目录失败: {temp_output_obj.name}, Error: {e}")
            elif output_dir_path and not temp_output_obj:
                 logger.debug(f"未清理指定的 magic-pdf 输出目录: {output_dir_path}")


    async def _run_magic_pdf(self, input_pdf_path: Path, output_dir_path: Path):
        """异步执行 magic-pdf 命令。"""
        command = [
            str(self._settings.magic_pdf_path),
            str(input_pdf_path),
            "--output-dir", str(output_dir_path)
        ]
        # 添加额外参数（如果提供）
        if self._settings.magic_pdf_extra_args:
             command.extend(self._settings.magic_pdf_extra_args.split())

        logger.info(f"执行命令: {' '.join(command)}")

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self._settings.magic_pdf_timeout_seconds
            )
            stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""

            if process.returncode == 0:
                logger.info(f"magic-pdf 执行成功。stdout:\n{stdout_str}")
                if stderr_str:
                     logger.warning(f"magic-pdf 执行有 stderr 输出:\n{stderr_str}")
            else:
                logger.error(f"magic-pdf 执行失败。Return Code: {process.returncode}")
                logger.error(f"stdout:\n{stdout_str}")
                logger.error(f"stderr:\n{stderr_str}")
                raise MagicPdfExecutionError(
                    f"magic-pdf 返回非零退出码: {process.returncode}. Stderr: {stderr_str[:500]}..." # 限制错误信息长度
                )
        except asyncio.TimeoutError:
            logger.error(f"magic-pdf 执行超时 ({self._settings.magic_pdf_timeout_seconds} 秒)")
            try:
                 process.terminate() # 尝试终止进程
                 await process.wait() # 等待终止完成
            except ProcessLookupError:
                 logger.warning("尝试终止超时进程时，进程已不存在。")
            except Exception as term_err:
                 logger.warning(f"终止超时进程时出错: {term_err}")
            raise MagicPdfExecutionError("magic-pdf 执行超时")
        except Exception as e:
            logger.error(f"执行 magic-pdf 过程中发生异常: {e}", exc_info=True)
            raise MagicPdfExecutionError(f"执行 magic-pdf 时发生异常: {e}") from e


    def _prepare_output_directory(self, input_path: Path) -> Tuple[Path, Optional[tempfile.TemporaryDirectory]]:
        """准备 magic-pdf 的输出目录。返回目录路径和临时目录对象（如果是临时创建的）。"""
        if self._settings.magic_pdf_output_base_dir:
            # 使用指定的基础目录，并创建一个唯一的子目录
            base_dir = Path(self._settings.magic_pdf_output_base_dir)
            # 使用输入文件名和UUID确保唯一性
            unique_subdir_name = f"{input_path.stem}_{generate_uuid()}"
            output_dir = base_dir / unique_subdir_name
            output_dir.mkdir(parents=True, exist_ok=True) # 创建目录
            logger.info(f"使用指定基础目录下的子目录作为输出: {output_dir}")
            return output_dir, None # 不是临时目录对象
        else:
            # 创建系统临时目录
            temp_output_dir = tempfile.TemporaryDirectory(prefix="scrsit_pdf_out_")
            logger.info(f"使用系统临时目录作为输出: {temp_output_dir.name}")
            return Path(temp_output_dir.name), temp_output_dir

    def _check_file_size(self, file_path: Path):
        """检查文件大小是否超过阈值。"""
        if self._settings.large_file_threshold_mb is not None:
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if file_size_mb > self._settings.large_file_threshold_mb:
                    logger.warning(
                        f"文件 '{file_path.name}' 大小 ({file_size_mb:.2f} MB) "
                        f"超过阈值 ({self._settings.large_file_threshold_mb} MB)。"
                        "处理可能需要较长时间或较多资源。"
                    )
                else:
                    logger.debug(f"文件大小检查通过 ({file_size_mb:.2f} MB).")
            except Exception as e:
                 logger.warning(f"无法检查文件大小: {file_path}, Error: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件的 SHA1 校验和。"""
        hasher = hashlib.sha1()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192): # Read in chunks
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"无法计算文件校验和: {file_path}, Error: {e}")
            return "checksum_error"

    def _map_to_document(self,
                         original_filename: str,
                         checksum: Optional[str],
                         model_data: List[Dict[str, Any]],
                         middle_data: Dict[str, Any],
                         output_dir: Path) -> Document:
        """
        将 magic-pdf 的 JSON 输出映射到核心 Document 模型。
        这是一个核心但复杂的步骤，需要根据 JSON 结构仔细提取信息。
        注意：此实现是一个基础版本，可能需要根据具体需求进行细化。
        """
        doc = Document(
            name=original_filename,
            type=DocumentType.PDF,
            checksum=checksum,
            metadata={
                "source_tool": "magic-pdf",
                "magic_pdf_version": middle_data.get("_version_name", "unknown"),
                "parse_type": middle_data.get("_parse_type", "unknown"),
                "page_count": len(middle_data.get("pdf_info", [])),
                # 可以从 model_data[0]['page_info'] 获取第一页尺寸等
            }
        )

        full_content_parts = []
        page_infos = {page['page_info']['page_no']: page['page_info'] for page in model_data}

        # 遍历 middle_data 中的页面信息
        for page_index, page_data in enumerate(middle_data.get("pdf_info", [])):
            page_no = page_data.get("page_idx", page_index) # 优先使用 page_idx
            page_info = page_infos.get(page_no) # 获取 model.json 中的页面信息
            page_width = page_info.get("width") if page_info else None
            page_height = page_info.get("height") if page_info else None

            doc.metadata.setdefault("page_dimensions", {})[page_no] = {
                "width": page_width,
                "height": page_height,
            }

            # 简单地拼接所有文本块内容作为文档主内容
            # 更高级：可以尝试根据 layout_bboxes 或标题类型构建 StructuredContent
            for block in page_data.get("para_blocks", []):
                block_text = self._extract_text_from_block(block)
                if block_text:
                    full_content_parts.append(block_text)

                # --- 提取特定元素 ---
                if block.get("type") == "image":
                    # 查找对应的 span 获取图像路径
                    img_span = self._find_span_by_type(block, "image")
                    if img_span and img_span.get("img_path"):
                        try:
                            img_abs_path = output_dir / img_span["img_path"]
                            if img_abs_path.is_file():
                                with open(img_abs_path, "rb") as img_f:
                                    img_content = img_f.read()
                                img = Picture(
                                    id=f"{doc.id}_img_{len(doc.pictures)}",
                                    name=img_span.get("content") or f"Image_{len(doc.pictures)}", # 尝试用 content 作 name
                                    content=img_content,
                                    size=len(img_content),
                                    description=self._extract_caption_footnote(page_data, block.get("bbox"), "image"),
                                    metadata={ # 添加元数据
                                        "page_number": page_no,
                                        "bbox": block.get("bbox"), # 父块的 bbox
                                        "source_path": img_span["img_path"],
                                    }
                                )
                                doc.pictures.append(img)
                            else:
                                logger.warning(f"图片文件未找到: {img_abs_path}")
                        except Exception as e:
                            logger.warning(f"处理图片时出错: {img_span.get('img_path')}, Error: {e}")

                elif block.get("type") == "table":
                    # 查找对应的 span 获取表格路径 (通常是截图) 或尝试解析内容
                    table_span = self._find_span_by_type(block, "table")
                    table_content = None
                    table_name = f"Table_{len(doc.tables)}"
                    metadata = {
                        "page_number": page_no,
                        "bbox": block.get("bbox"),
                        "source_image_path": None
                    }
                    if table_span and table_span.get("img_path"):
                        table_img_path = output_dir / table_span["img_path"]
                        metadata["source_image_path"] = table_span["img_path"]
                        if table_img_path.is_file():
                           # 可以考虑将图片路径或内容存入 Table，或尝试 OCR
                           logger.debug(f"找到表格图片: {table_img_path}")
                           # table_content = f"Table image reference: {table_span['img_path']}"
                           # 暂不直接读取图片内容放入 Table.content

                    # 尝试从 model.json 获取更精确的表格 bbox (如果需要)
                    # model_table = self._find_model_element(model_data, page_no, block.get("bbox"), 5) # Category 5 = table

                    tab = Table(
                        id=f"{doc.id}_tbl_{len(doc.tables)}",
                        name=table_span.get("content") or table_name,
                        content=table_content, # 目前为 None，需要后续处理或 OCR
                        description=self._extract_caption_footnote(page_data, block.get("bbox"), "table"),
                        order_index=len(doc.tables),
                        metadata=metadata,
                    )
                    doc.tables.append(tab)

            # --- 提取页面级元素 (不一定在 para_blocks 里) ---
            # 行间公式 (Interline Equations)
            for eq_block in page_data.get("interline_equations", []):
                 eq_span = self._find_span_by_type(eq_block, "interline_equation")
                 if eq_span and eq_span.get("content"): # middle.json 的 content 可能是公式文本
                     # 尝试在 model.json 中找到对应的公式并获取 LaTeX
                     model_formula = self._find_model_element(model_data, page_no, eq_block.get("bbox"), 8) # Category 8 = isolate_formula
                     latex_content = model_formula.get("latex") if model_formula else None

                     formula = Formula(
                         id=f"{doc.id}_form_{len(doc.formulas)}",
                         raw=latex_content or eq_span.get("content"), # 优先用 LaTeX
                         description=f"Interline equation on page {page_no}",
                         metadata={
                             "page_number": page_no,
                             "bbox": eq_block.get("bbox"),
                             "source_type": "latex" if latex_content else "text",
                             "score": model_formula.get("score") if model_formula else None,
                         }
                     )
                     doc.formulas.append(formula)

        # --- 合并文本内容 ---
        doc.content = "\n\n".join(full_content_parts) # 用双换行分隔来自不同块的文本
        doc.length = len(doc.content)

        # TODO: 未来可以实现从 layout_bboxes 或标题块构建 StructuredContent
        # TODO: 未来可以解析行内公式 (inline_equation spans) 并嵌入文本或创建 Element
        # TODO: 解析链接 (Links) 和文献引用 (References) - magic-pdf 输出似乎不直接提供这些

        return doc

    def _extract_text_from_block(self, block: Dict[str, Any]) -> str:
        """递归地从 block 及其子 block 中提取所有文本 span 的内容。"""
        block_text_parts = []
        # 处理当前层级的 lines 和 spans
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                # 只提取 'text' 类型的 span 内容，忽略图片、表格等的文本表示
                # 行内公式也暂时忽略，避免混淆
                if span.get("type") == "text" and span.get("content"):
                    block_text_parts.append(span["content"])
        # 递归处理子 blocks (如果存在) - 注意 block 结构定义可能嵌套
        if "blocks" in block: # 检查是否是一级块
            for sub_block in block.get("blocks", []):
                 block_text_parts.append(self._extract_text_from_block(sub_block))

        return "".join(block_text_parts) # 直接拼接，更复杂可以加换行

    def _find_span_by_type(self, block: Dict[str, Any], span_type: str) -> Optional[Dict[str, Any]]:
        """在 block 的 lines 中查找指定类型的第一个 span。"""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("type") == span_type:
                    return span
        # 递归查找子 block (如果是一级块)
        if "blocks" in block:
            for sub_block in block.get("blocks", []):
                found_span = self._find_span_by_type(sub_block, span_type)
                if found_span:
                    return found_span
        return None

    def _extract_caption_footnote(self, page_data: Dict[str, Any], element_bbox: List[float], element_type: str) -> Optional[str]:
        """
        尝试在页面数据中查找与给定元素 bbox 邻近的标题 (caption) 或脚注 (footnote) 块。
        这是一个简化的实现，实际可能需要更复杂的空间关系判断。
        """
        captions = []
        footnotes = []
        caption_type_name = f"{element_type}_caption" # e.g., image_caption, table_caption
        footnote_type_name = f"{element_type}_footnote" # e.g., image_footnote, table_footnote

        for block in page_data.get("para_blocks", []):
            block_type = block.get("type")
            if block_type == caption_type_name:
                # TODO: 添加基于 bbox 距离或位置的判断逻辑
                # 这里简化为：只要找到对应类型的 caption/footnote 就添加
                captions.append(self._extract_text_from_block(block))
            elif block_type == footnote_type_name:
                # TODO: 添加基于 bbox 距离或位置的判断逻辑
                footnotes.append(self._extract_text_from_block(block))

        desc = ""
        if captions:
            desc += "Caption: " + " ".join(captions)
        if footnotes:
            if desc: desc += "\n"
            desc += "Footnote: " + " ".join(footnotes)

        return desc if desc else None

    def _find_model_element(self, model_data: List[Dict[str, Any]], page_no: int, bbox: List[float], category_id: int) -> Optional[Dict[str, Any]]:
        """
        在 model.json 数据中查找指定页面、类别且与给定 bbox 大致匹配的元素。
        使用 Bbox 中心点距离或 IoU 进行匹配（简化实现：中心点距离）。
        """
        target_page = next((page for page in model_data if page.get("page_info", {}).get("page_no") == page_no), None)
        if not target_page or not bbox:
            return None

        target_cx = (bbox[0] + bbox[2]) / 2
        target_cy = (bbox[1] + bbox[3]) / 2
        min_dist = float('inf')
        best_match = None

        for det in target_page.get("layout_dets", []):
            if det.get("category_id") == category_id:
                poly = det.get("poly")
                if poly and len(poly) == 8:
                    # 计算 model.json 中元素的中心点 (近似)
                    det_cx = (poly[0] + poly[2] + poly[4] + poly[6]) / 4
                    det_cy = (poly[1] + poly[3] + poly[5] + poly[7]) / 4
                    dist_sq = (target_cx - det_cx)**2 + (target_cy - det_cy)**2

                    # 如果中心点非常接近，则认为是匹配
                    # TODO: 使用更鲁棒的匹配方法，如 IoU 或考虑 bbox 大小
                    if dist_sq < min_dist and dist_sq < 100: # 阈值需要调整
                        min_dist = dist_sq
                        best_match = det

        return best_match