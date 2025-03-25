from typing import List, Dict, Any, Optional

from ordered_list import OrderedList

class StructuredContent:
    """
    表示文档中的结构化元素，形成层次结构。
    增加了 title 属性以及动态增删子节点、查找和转换为字典的功能。
    """
    def __init__(
        self,
        id: str,
        parent_id: Optional[str] = None,
        level: Optional[int] = None,
        title: Optional[str] = None,
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
            title (Optional[str]): 内容元素的标题，如章节标题。
            content (Optional[str]): 元素的文本内容（base64 编码或纯文本）。
            parent (Optional['StructuredContent']): 父 StructuredContent 对象引用。
            children (Optional[OrderedList['StructuredContent']]): 子 StructuredContent 对象列表。
        """
        self.id = id
        self.parent_id = parent_id
        self.level = level
        self.title = title
        self.content = content
        self.parent = parent
        self.children = children if children is not None else OrderedList()

    def add_child(self, child: 'StructuredContent') -> None:
        """
        添加子 StructuredContent 对象，并设置父引用。

        Args:
            child (StructuredContent): 要添加的子对象。
        """
        child.parent = self
        child.parent_id = self.id
        self.children.append(child)

    def remove_child(self, child: 'StructuredContent') -> None:
        """
        移除指定的子 StructuredContent 对象。

        Args:
            child (StructuredContent): 要移除的子对象。
        """
        self.children.remove(child)
        child.parent = None
        child.parent_id = None

    def find_by_id(self, search_id: str) -> Optional['StructuredContent']:
        """
        根据 id 查找 StructuredContent 对象（递归搜索）。

        Args:
            search_id (str): 要查找的 id。

        Returns:
            Optional[StructuredContent]: 找到的内容对象或 None。
        """
        if self.id == search_id:
            return self
        for child in self.children:
            found = child.find_by_id(search_id)
            if found:
                return found
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        将 StructuredContent 对象转换为字典（递归转换所有子节点）。

        Returns:
            Dict[str, Any]: 包含 id、parent_id、level、title、content 和 children 的字典。
        """
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "title": self.title,
            "content": self.content,
            "children": [child.to_dict() for child in self.children]
        }

    def update_content(self, new_content: str) -> None:
        """
        更新当前节点的内容。

        Args:
            new_content (str): 新的内容字符串。
        """
        self.content = new_content

    def get_catalogue(self, level: int) -> List[Dict[str, Any]]:
        """
        检索特定级别的目录（带有 id 和标题的字典列表）。

        Args:
            level (int): 要检索的层次级别。

        Returns:
            List[Dict[str, Any]]: 字典列表，每个字典包含指定级别的 StructuredContent 元素的 'id' 和 'title'。
        """
        catalogue = []
        if self.level == level:
            catalogue.append({"id": self.id, "title": self.title, "content": self.content})
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
            Optional[StructuredContent]: 父对象，如果是根元素则返回 None。
        """
        return self.parent

    def get_children(self) -> OrderedList['StructuredContent']:
        """
        返回子 StructuredContent 对象列表。

        Returns:
            OrderedList[StructuredContent]: 子对象列表。
        """
        return self.children

    def __repr__(self) -> str:
        t = self.title if self.title else self.content
        display = (t[:20] + "...") if t and len(t) > 20 else t
        return f"StructuredContent(id='{self.id}', level={self.level}, title='{display}')"


if __name__ == "__main__":
    # 示例：使用一篇论文的结构化存储构建文档结构

    # 创建根节点，论文的标题
    paper = StructuredContent(
        id="paper-001",
        level=0,
        title="Example Paper on AI",
        content="全文内容略..."
    )

    # 添加摘要节点
    abstract = StructuredContent(
        id="paper-001-abstract",
        level=1,
        title="Abstract",
        content="This paper presents an example paper on artificial intelligence..."
    )
    paper.add_child(abstract)

    # 添加章节：Introduction
    intro = StructuredContent(
        id="paper-001-intro",
        level=1,
        title="Introduction",
        content="The introduction section introduces the background and motivation..."
    )
    paper.add_child(intro)

    # 在 Introduction 下再添加子章节
    background = StructuredContent(
        id="paper-001-intro-bg",
        level=2,
        title="Background",
        content="Detailed background information..."
    )
    intro.add_child(background)

    # 添加章节： Methods
    methods = StructuredContent(
        id="paper-001-methods",
        level=1,
        title="Methods",
        content="This section describes the methods used in the paper..."
    )
    paper.add_child(methods)

    # 添加章节： Results
    results = StructuredContent(
        id="paper-001-results",
        level=1,
        title="Results",
        content="The experimental results are presented here..."
    )
    paper.add_child(results)

    # 测试：获取所有一级目录
    catalogue_level_1 = paper.get_catalogue(1)
    print("一级目录：")
    for item in catalogue_level_1:
        print(item)

    # 测试：查找节点
    found_node = paper.find_by_id("paper-001-intro-bg")
    print("\n查找 id 为 'paper-001-intro-bg' 的节点：")
    print(found_node)

    # 测试：转换为字典形式输出整个结构
    import json
    print("\n论文结构（JSON 格式）：")
    print(json.dumps(paper.to_dict(), indent=2, ensure_ascii=False))