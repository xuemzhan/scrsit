from typing import Optional, List

class Reference:
    """
    表示文档中的参考文献。
    """
    def __init__(
        self,
        authors: Optional[List[str]] = None,
        publisher: Optional[str] = None,
        url: Optional[str] = None,
        date: Optional[str] = None,
    ):
        """
        初始化 Reference 对象。

        Args:
            authors (Optional[List[str]]): 参考文献的作者列表。
            publisher (Optional[str]): 参考文献的发布者。
            url (Optional[str]): 参考文献的 URL。
            date (Optional[str]): 参考文献的发布或访问日期。
        """
        self.authors = authors if authors is not None else []
        self.publisher = publisher
        self.url = url
        self.date = date

    def __repr__(self) -> str:
        return f"Reference(authors={self.authors}, publisher='{self.publisher}')"