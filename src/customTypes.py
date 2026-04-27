"""
自定义的数据类型
序列化时保留指定位数小数的float
"""
from typing import Literal
from decimal import Decimal, ROUND_DOWN, ROUND_UP, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP, ROUND_HALF_EVEN

class FloatRx(float):
    decimal_places : int    # 保留的位数
    ROUND_MAP = {
        "down": ROUND_FLOOR,            # 向下（往负无穷）
        "up": ROUND_CEILING,            # 向上（往正无穷）
        "toward_zero": ROUND_DOWN,      # 靠近0（截断）
        "away_zero": ROUND_UP,          # 远离0（绝对值增大）
        "half_up": ROUND_HALF_UP,       # 四舍五入
        "half_even": ROUND_HALF_EVEN,   # 四舍六入五凑偶（银行家舍入）
    }

    def __new__(cls, value,
                decimal: int = 2,
                rounding: Literal["down", "up", "toward_zero", "away_zero", "half_up", "half_even"] = "half_up"):
        """
        Args:
            decimal : 序列化时保留的位数
            rounding : 保留指定位数小数时的舍入规则
        """
        # 1. 用 Decimal 进行精确舍入（保留 decimal 位小数）
        d = Decimal(str(value))
        mode = cls.ROUND_MAP.get(rounding, ROUND_HALF_UP)
        q = Decimal("1." + "0" * decimal) if decimal > 0 else Decimal("1")
        rounded = d.quantize(q, rounding=mode)

        # 2. 创建 float 实例
        instance = super().__new__(cls, float(rounded))

        # 3. 保存参数，并提前生成格式化字符串（用于 JSON 输出）
        instance.decimal_places = decimal
        instance._rounded_str = f"{float(rounded):.{decimal}f}"
        instance._rounding = rounding
        return instance

    def __repr__(self):
        return f"FloatRx({self._rounded_str})"

    def __format__(self, format_spec):
        # 让 print(f"{obj}") 这类格式化也能显示固定小数位
        if not format_spec:
            return self._rounded_str
        return super().__format__(format_spec)