"""
生成速度计算器
"""
import random
from decimal import Decimal, ROUND_HALF_UP

class GenerateSpeedCounter:
    generate_speed : float      # 生成速度的基准值(tokens/s)
    __range : float             # 生成速度波动范围(±__range tokens/s)

    def __init__(self, base: float, speed_range: float | None = None):
        if speed_range is None:
            speed_range = base*0.3    # 默认波动范围为30%
        self.generate_speed = base
        self.__range = speed_range

    def get_speed(self):
        sys_rand = random.SystemRandom()
        low = self.generate_speed-self.__range
        high = self.generate_speed+self.__range
        if low<=0:
            low = 0.05
        if high<low:
            high = low
        raw_value = sys_rand.uniform(low, high)
        rounded = Decimal(str(raw_value)).quantize(Decimal('0.0000000000001'), rounding=ROUND_HALF_UP)
        return float(rounded)