# output.py
from mapper import DEFAULT_RAMP, luminance


def to_terminal(lines: list[str]) -> None:
    print("\n".join(lines))


def to_file(lines: list[str], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def to_ansi_color(rgb_img, ramp: str = DEFAULT_RAMP) -> str:
    """生成 24-bit ANSI 真彩色字符画，保留 emoji 原始颜色。"""
    pixels = rgb_img.load()
    w, h = rgb_img.size
    n = len(ramp)
    RESET = "\033[0m"
    out_lines: list[str] = []
    for y in range(h):
        parts = []
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            gray = luminance(r, g, b)
            idx = min(gray * n // 256, n - 1)
            ch = ramp[idx]
            parts.append(f"\033[38;2;{r};{g};{b}m{ch}")
        out_lines.append("".join(parts) + RESET)
    return "\n".join(out_lines)


def ansi_color_to_file(text: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)