import base64
from typing import Optional, List

from scrsit.core.document.base import Element

class Formula(Element):
    """
    表示文档中的数学或符号公式。
    """
    def __init__(self, raw: str, formula_type: str = "inline", label: Optional[str] = None, numbered: bool = False, dependencies: Optional[List[str]] = None):
        """
        初始化 Formula 对象。

        Args:
            raw (str): 公式的原始表示（base64 编码）。
            formula_type (str, optional): 公式类型（"inline" 或 "block"）。默认为 "inline"。
            label (str, optional): 公式标签。默认为 None。
            numbered (bool, optional): 是否编号。默认为 False。
            dependencies (List[str], optional): 依赖的 LaTeX 宏包列表。默认为 None。

        Raises:
            ValueError: 如果 raw 不是有效的 Base64 字符串。
            ValueError: 如果 formula_type 不是 "inline" 或 "block"。
        """
        if not isinstance(raw, str):
            raise TypeError("raw must be a string")

        if formula_type not in ("inline", "block"):
            raise ValueError("formula_type must be 'inline' or 'block'")

        try:
            # 尝试解码以验证是否为有效的 Base64
            base64.b64decode(raw)
        except base64.binascii.Error:
            raise ValueError("raw must be a valid Base64 encoded string")

        self.raw = raw
        self.formula_type = formula_type
        self.label = label
        self.numbered = numbered
        self.dependencies = dependencies or []
        self._decoded_formula: Optional[str] = None

    def get_formula(self, decode: bool = False) -> str:
        """
        返回原始公式。

        Args:
            decode (bool, optional): 是否解码公式。默认为 False。

        Returns:
            str: 原始公式字符串。
        """
        if decode:
            if self._decoded_formula is None:
                self._decoded_formula = base64.b64decode(self.raw).decode('utf-8')  # 假设是 UTF-8 编码
            return self._decoded_formula
        return self.raw

    def get_latex(self) -> str:
        """
        返回 LaTeX 格式的公式。
        """
        formula = self.get_formula(decode=True)
        if self.formula_type == "inline":
            return f"${formula}$"
        else:
            if self.numbered:
                latex = f"\\begin{{equation}}\n{formula}\n"
            else:
                 latex = f"\\begin{{equation*}}\n{formula}\n"

            if self.label:
                latex += f"\\label{{{self.label}}}\n"
            latex += f"\\end{{equation*}}" if not self.numbered else f"\\end{{equation}}"
            return latex

    def __repr__(self) -> str:
        return f"Formula(raw='{self.raw[:20]}...', type='{self.formula_type}', label='{self.label}')"


if __name__ == '__main__':
    # 行内公式示例
    inline_formula = Formula(
        raw=base64.b64encode(r"E=mc^2".encode('utf-8')).decode('utf-8'),
        formula_type="inline"
    )
    print("Inline Formula LaTeX:", inline_formula.get_latex())

    # 块级公式示例（带编号）
    block_formula_numbered = Formula(
        raw=base64.b64encode(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}".encode('utf-8')).decode('utf-8'),
        formula_type="block",
        numbered=True,
        label="integral"
    )
    print("Block Formula (Numbered) LaTeX:", block_formula_numbered.get_latex())

    # 块级公式示例（不带编号）
    block_formula_unnumbered = Formula(
        raw=base64.b64encode(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}".encode('utf-8')).decode('utf-8'),
        formula_type="block"
    )
    print("Block Formula (Unnumbered) LaTeX:", block_formula_unnumbered.get_latex())