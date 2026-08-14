# mapper.py

# 预设梯度 1：传统字符，暗 -> 亮
RAMP_1 = "@%#*+=-:. "

# 预设梯度 2：方块字符，暗 -> 亮（配合 --color 效果极佳）
RAMP_2 = "█▇▆▅▄▃▂▁"

DEFAULT_RAMP = RAMP_1


class GrayToASCII:
    """灰度图 -> 二维 ASCII 字符矩阵。"""

    def __init__(self, ramp: str = DEFAULT_RAMP, invert: bool = False):
        if not ramp:
            raise ValueError("ramp 不能为空")
        self.ramp = ramp
        self.invert = invert
        self._n = len(ramp)

    def map(self, gray_img) -> list[str]:
        pixels = gray_img.load()
        w, h = gray_img.size
        lines: list[str] = []
        for y in range(h):
            buf = []
            for x in range(w):
                v = pixels[x, y]
                if self.invert:
                    v = 255 - v
                idx = v * self._n // 256
                if idx >= self._n:
                    idx = self._n - 1
                buf.append(self.ramp[idx])
            lines.append("".join(buf))
        return lines


def luminance(r: int, g: int, b: int) -> int:
    """Rec. 601 亮度。"""
    return int(0.299 * r + 0.587 * g + 0.114 * b)