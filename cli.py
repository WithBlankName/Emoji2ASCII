# cli.py
import argparse
import sys
import datetime
import platform
import re

from renderer import EmojiRenderer
from processor import ImageProcessor
from mapper import GrayToASCII, RAMP_1, RAMP_2
from output import to_terminal, to_file, to_ansi_color, ansi_color_to_file


def run_neofetch():
    """彩蛋：输出类似 neofetch 风格的系统信息与彩色 emoji 图标。"""
    now = datetime.datetime.now()
    hour = now.hour

    # 根据时间决定背景色：1-12点白底，其他时间(13-23, 0点)黑底
    if 1 <= hour <= 12:
        bg = "white"
    else:
        bg = "black"

    print("\n\033[1;35m系统正在感知时空扭曲... 🌀\033[0m\n")

    try:
        # 渲染 🌀 图标，强制使用 setup2 (方块字符), 彩色, 宽度 36
        with EmojiRenderer(device_scale_factor=4, font_size=240) as renderer:
            png_bytes = renderer.render("🌀")
            processor = ImageProcessor(background=bg)
            gray, rgb = processor.process(png_bytes, target_width=36)
            art_lines = to_ansi_color(rgb, RAMP_2).split('\n')
    except Exception as e:
        print(f"\033[1;31m渲染彩蛋失败: {e}\033[0m", file=sys.stderr)
        sys.exit(1)

    # 构造文字信息
    info_lines = [
        f"\033[1;36m{platform.node()}\033[0m",
        "-----------------------------",
        f"\033[1;33mOS:\033[0m {platform.system()} {platform.release()}",
        f"\033[1;33mHost:\033[0m {platform.machine()}",
        f"\033[1;33mKernel:\033[0m {platform.version().split()[0]}",
        f"\033[1;33mPython:\033[0m {platform.python_version()}",
        f"\033[1;33mProject:\033[0m Emoji2ASCII",
        f"\033[1;33mShell:\033[0m /bin/python",
        f"\033[1;33mUptime:\033[0m {now.strftime('%H:%M:%S')}",
        "",
        "\033[1;31m●\033[0m\033[1;32m●\033[0m\033[1;33m●\033[0m\033[1;34m●\033[0m\033[1;35m●\033[0m\033[1;36m●\033[0m"
    ]

    # 用于计算字符串在终端中的实际显示宽度（去除 ANSI 颜色代码）
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    max_art_width = max(len(ansi_escape.sub('', line)) for line in art_lines)

    print()
    # 并排打印图标和信息
    for i in range(max(len(art_lines), len(info_lines))):
        art_line = art_lines[i] if i < len(art_lines) else ""
        info_line = info_lines[i] if i < len(info_lines) else ""

        real_len = len(ansi_escape.sub('', art_line))
        padding = " " * (max_art_width - real_len)

        print(f"  {art_line}{padding}  {info_line}")
    print("\n")


def render_one(emoji: str, args, renderer: EmojiRenderer):
    """对单个 emoji 进行端到端处理，返回 (ascii_lines, rgb_img)。"""
    png_bytes = renderer.render(emoji)
    processor = ImageProcessor(background=args.bg)
    gray, rgb = processor.process(
        png_bytes,
        target_width=args.width,
        contrast_stretch=args.contrast,
        equalize=args.equalize,
    )
    mapper = GrayToASCII(ramp=args.ramp, invert=args.invert)
    lines = mapper.map(gray)
    return lines, rgb


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # 拦截 --neofetch 彩蛋参数
    if "--neofetch" in argv:
        if len(argv) > 1:
            print("错误: --neofetch 不能与其他参数一起使用。", file=sys.stderr)
            sys.exit(1)
        run_neofetch()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="将 emoji 渲染为 ASCII 字符画（Playwright + MSAA 超采样）"
    )
    parser.add_argument("emojis", nargs="+", help="一个或多个 emoji 字符")
    parser.add_argument("-w", "--width", type=int, default=60,
                        help="字符画宽度（默认 60）")
    parser.add_argument("-s", "--scale", type=int, default=4,
                        help="device_scale_factor，相当于 MSAA 超采样倍数（默认 4）")
    parser.add_argument("--font-size", type=int, default=240,
                        help="HTML 中 emoji 的 font-size（默认 240px）")
    parser.add_argument("--bg", choices=["white", "black"], default="white",
                        help="背景色（默认 white）")

    # 互斥参数：选择字符梯度表
    setup_group = parser.add_mutually_exclusive_group()
    setup_group.add_argument("--setup1", action="store_true",
                             help="使用字符梯度 1: '@%%#*+=-:. ' (默认)")
    setup_group.add_argument("--setup2", action="store_true",
                             help="使用字符梯度 2: '█▇▆▅▄▃▂▁' (适合配合 --color)")

    parser.add_argument("--invert", action="store_true", help="反转明暗")
    parser.add_argument("--contrast", action="store_true",
                        help="对比度拉伸")
    parser.add_argument("--equalize", action="store_true",
                        help="自适应直方图均衡")
    parser.add_argument("-o", "--output", help="输出到 .txt 文件")
    parser.add_argument("--color", action="store_true",
                        help="输出 24-bit ANSI 真彩色版本")
    parser.add_argument("--no-print", action="store_true",
                        help="不在终端打印（仅写入文件）")
    parser.add_argument("--show-browser", action="store_true",
                        help="调试用：显示浏览器窗口")

    args = parser.parse_args(argv)

    # 根据 cli 参数确定使用的 ramp
    if args.setup2:
        args.ramp = RAMP_2
    else:
        args.ramp = RAMP_1

    outputs = []
    try:
        with EmojiRenderer(
                device_scale_factor=args.scale,
                font_size=args.font_size,
                headless=not args.show_browser,
        ) as renderer:
            for emoji in args.emojis:
                try:
                    lines, rgb = render_one(emoji, args, renderer)
                    if args.color:
                        outputs.append(to_ansi_color(rgb, args.ramp))
                    else:
                        outputs.append("\n".join(lines))
                except Exception as e:
                    print(f"[WARN] 处理 emoji '{emoji}' 失败: {e}",
                          file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] 浏览器或渲染失败: {e}", file=sys.stderr)
        sys.exit(1)

    text = "\n\n".join(outputs)

    if not args.no_print:
        print(text)

    if args.output:
        if args.color:
            ansi_color_to_file(text, args.output)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"[INFO] 已保存到 {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
