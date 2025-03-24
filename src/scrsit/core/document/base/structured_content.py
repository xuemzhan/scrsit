from typing import List, Dict, Any, Optional

from .ordered_list import OrderedList

class StructuredContent:
    """
    表示文档中的结构化元素，形成层次结构。
    """
    def __init__(
        self,
        id: str,
        parent_id: Optional[str] = None,
        level: Optional[int] = None,
        content: Optional[str] = None,
        parent: Optional['StructuredContent'] = None,
        children: Optional[OrderedList['StructuredContent']] = None,
    ):
        """
        初始化 StructuredContent 对象。

        Args:
            id (str): 内容元素的唯一标识符。
            parent_id (Optional[str]): 父内容元素的标识符。
            level (Optional[int]): 内容元素的层次级别。
            content (Optional[str]): 元素的文本内容（base64 编码）。
            parent (Optional['StructuredContent']): 对父 StructuredContent 对象的引用。
            children (Optional[OrderedList['StructuredContent']]): 子 StructuredContent 对象列表。
        """
        self.id = id
        self.parent_id = parent_id
        self.level = level
        self.content = content
        self.parent = parent
        self.children = children if children is not None else OrderedList()

    def get_catalogue(self, level: int) -> List[Dict[str, Any]]:
        """
        检索特定级别的目录（带有 id 和 content 的字典列表）。

        Args:
            level (int): 要检索的层次级别。

        Returns:
            List[Dict[str, Any]]: 字典列表，每个字典包含指定级别的 StructuredContent 元素的 'id' 和 'content'。
        """
        catalogue = []
        if self.level == level:
            catalogue.append({"id": self.id, "content": self.content})
        for child in self.children:
            catalogue.extend(child.get_catalogue(level))
        return catalogue

    def get_content_by_catalogue(self, catalogue_id: str) -> Optional[str]:
        """
        通过目录 ID 检索 StructuredContent 元素的内容。

        Args:
            catalogue_id (str): 要检索的目录项的 ID。

        Returns:
            Optional[str]: 如果找到 StructuredContent 元素，则返回其内容，否则返回 None。
        """
        if self.id == catalogue_id:
            return self.content
        for child in self.children:
            content = child.get_content_by_catalogue(catalogue_id)
            if content:
                return content
        return None

    def get_parent(self) -> Optional['StructuredContent']:
        """
        返回父 StructuredContent 对象。

        Returns:
            Optional['StructuredContent']: 父对象，如果是根元素则返回 None。
        """
        return self.parent

    def get_children(self) -> OrderedList['StructuredContent']:
        """
        返回子 StructuredContent 对象列表。

        Returns:
            OrderedList['StructuredContent']: 子对象列表。
        """
        return self.children

    def __repr__(self) -> str:
        return f"StructuredContent(id='{self.id}', level={self.level}, content='{self.content[:20]}...')"