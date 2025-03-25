from typing import Optional, Dict
from PyPDF2 import PdfReader
from base.document import Document, Chunk

class PdfDocument(Document):
    """
    表示一个 PDF 文档。
    """
    def __init__(self, file_path: str, metadata: Optional[Dict] = None):
        """
        初始化 PDF 文档。

        Args:
            file_path (str): PDF 文件的路径。
            metadata (Optional[Dict]): 与文档相关的元数据。
        """
        super().__init__(file_path, metadata)

    def load(self):
        """
        加载 PDF 文档的内容并将其分割成片段。
        """
        try:
            with open(self.file_path, 'rb') as file:
                reader = PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        self.add_chunk(Chunk(content=text, metadata={"page": page_num + 1}))
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF 文件未找到: {self.file_path}")
        except Exception as e:
            raise Exception(f"加载 PDF 文件时发生错误: {e}")