from typing import TypeVar, Callable, Optional
from collections import UserList

T = TypeVar('T')

class OrderedList(UserList[T]):
    """
    一个保留元素顺序的列表。
    继承自 UserList，以便更容易地进行扩展，并增加了查找、过滤、移除和去重等常用方法。
    """
    def __repr__(self) -> str:
        return f"OrderedList({super().__repr__()})"

    def find(self, condition: Callable[[T], bool]) -> Optional[T]:
        """
        返回第一个满足条件的元素，如果没有找到则返回 None。
        
        Args:
            condition (Callable[[T], bool]): 用于判定元素是否满足条件的函数。

        Returns:
            Optional[T]: 第一个满足条件的元素或 None。
        """
        for item in self.data:
            if condition(item):
                return item
        return None

    def filter(self, condition: Callable[[T], bool]) -> 'OrderedList[T]':
        """
        返回一个新的 OrderedList，其中包含所有满足条件的元素。
        
        Args:
            condition (Callable[[T], bool]): 用于过滤的条件函数。

        Returns:
            OrderedList[T]: 新的过滤结果列表。
        """
        filtered = [item for item in self.data if condition(item)]
        return OrderedList(filtered)

    def remove_all(self, condition: Callable[[T], bool]) -> int:
        """
        移除所有满足条件的元素，并返回删除的数量。
        
        Args:
            condition (Callable[[T], bool]): 用于判断是否删除的条件函数。

        Returns:
            int: 被删除元素的数量。
        """
        original_length = len(self.data)
        self.data = [item for item in self.data if not condition(item)]
        return original_length - len(self.data)

    def unique(self) -> 'OrderedList[T]':
        """
        返回一个新的 OrderedList，其中不包含重复的元素，保留原有顺序。
        
        Returns:
            OrderedList[T]: 去重后的列表。
        """
        seen = set()
        unique_list = []
        for item in self.data:
            if item not in seen:
                unique_list.append(item)
                seen.add(item)
        return OrderedList(unique_list)


if __name__ == "__main__":
    # 测试示例
    # 构造一个 OrderedList，包含重复数据
    ol = OrderedList([1, 2, 3, 4, 3, 2, 5, 6])
    print("原始 OrderedList:", ol)

    # 测试 find 方法：查找第一个大于 3 的元素
    result = ol.find(lambda x: x > 3)
    print("第一个大于 3 的元素:", result)

    # 测试 filter 方法：过滤所有奇数
    filtered = ol.filter(lambda x: x % 2 == 1)
    print("所有奇数:", filtered)

    # 测试 remove_all 方法：移除所有小于 3 的元素
    removed_count = ol.remove_all(lambda x: x < 3)
    print("移除元素个数:", removed_count, "修改后的 OrderedList:", ol)

    # 测试 unique 方法：返回去重后的 OrderedList
    unique_list = ol.unique()
    print("去重后的 OrderedList:", unique_list)