from typing import TypeVar
from collections import UserList

T = TypeVar('T')

class OrderedList(UserList[T]):
    """
    一个保留元素顺序的列表。
    继承自 UserList，以便更容易地进行扩展。
    """
    def __repr__(self) -> str:
        return f"OrderedList({super().__repr__()})"