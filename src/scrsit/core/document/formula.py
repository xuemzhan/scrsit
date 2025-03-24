class Formula:
    """
    表示文档中的数学或符号公式。
    """
    def __init__(self, raw: str):
        """
        初始化 Formula 对象。

        Args:
            raw (str): 公式的原始表示（base64 编码）。
        """
        self.raw = raw

    def get_formula(self) -> str:
        """
        返回原始公式。

        Returns:
            str: 原始公式字符串。
        """
        return self.raw

    def __repr__(self) -> str:
        return f"Formula(raw='{self.raw[:20]}...')"