"""
文档处理的基础模块，提供了文档结构化表示所需的核心类。
"""

# 基础类
from element import Element
from ordered_list import OrderedList

# 文档基类
from document import Document

# 文档内容组件
from chunk import Chunk
from structured_content import StructuredContent

# 文档元素
from entity import Entity
from formula import Formula
from link import Link
from ordered_list import OrderedList
from picture import Picture
from reference import Reference
from relationship import Relationship
from table import Table

__all__ = [
    # 基础类
    'Element',
    'OrderedList',
    
    # 文档基类
    'Document',
    
    # 文档内容组件
    'Chunk',
    'StructuredContent',
    
    # 文档元素
    'Entity',
    'Formula',
    'Link',
    'Picture',
    'Reference',
    'Relationship',
    'Table',
]