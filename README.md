# Emoji2ASCII

将输入的 Emoji 字符（如 🍥、🔥）渲染为高质量的 ASCII 字符画。项目通过无头浏览器进行超采样渲染，实现类似 MSAA 的抗锯齿效果，支持灰度映射及 24-bit ANSI 真彩色输出。
<img width="1077" height="538" alt="image" src="https://github.com/user-attachments/assets/295b7bbe-64a3-4417-b58e-5db40f45e225" />

## 说明与声明
> [!WARNING]
> **LLM 被用于开发**：本项目初始代码由LLM进行编写，后续经过大量调试、修改与逻辑重构。当前分发版本并非完全由 LLM 编写，但是如果你要Fork，请考虑LLM编码的可读性。
> **开源协议**：本项目基于 GNU General Public License v3.0 (GPLv3) 协议开源。任何分发、修改或衍生项目必须同样遵守 GPLv3 协议并开源。
> **第三方组件声明**：本项目运行时依赖 Google Chromium 浏览器内核（通过 Playwright 自动驱动）。Chromium 本身基于 BSD 等开源协议发布。本项目的 GPLv3 协议仅适用于项目自身源代码，不适用于 Chromium 二进制文件。

## 依赖与配置
> [!WARNING]
>**警告**：由于修改频率高，该README不是最新，请以源代码实现为准，请不要频繁为更新README提交Issue，感谢配合。

### 环境要求

- Python 3.8 或更高版本
- 操作系统：能运行这几个支持库的系统

### 安装步骤

建议使用虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

安装 Python 依赖：

```bash
pip install playwright pillow
```

下载并配置 Chromium 内核（Playwright 自动下载适配版本）：

```bash
playwright install chromium
```

## 使用方法

### 命令行参数

```text
usage: cli.py [-h] [-w WIDTH] [-s SCALE] [--font-size FONT_SIZE]
              [--bg {white,black}] [--ramp RAMP] [--invert] [--contrast]
              [--equalize] [-o OUTPUT] [--color] [--no-print] [--show-browser]
              emojis [emojis ...]

将 emoji 渲染为 ASCII 字符画 (Playwright + MSAA 超采样)

positional arguments:
  emojis                一个或多个 emoji 字符

options:
  -h, --help            显示帮助信息并退出
  -w, --width           字符画宽度（默认 60）
  -s, --scale           device_scale_factor，即 MSAA 超采样倍数（默认 4）
  --font-size           HTML 中 emoji 的 font-size（默认 240px）
  --bg {white,black}    背景色（默认 white）
  --ramp RAMP           灰度到 ASCII 的字符梯度（默认 '@%#*+=-:. '）
  --invert              反转明暗
  --contrast            对比度拉伸
  --equalize            自适应直方图均衡
  -o, --output          输出到 .txt 文件
  --color               输出 24-bit ANSI 真彩色版本
  --no-print            不在终端打印，仅写入文件
  --show-browser        调试用：显示浏览器窗口
```

### 使用示例

渲染单个 Emoji 并打印到终端：

```bash
python cli.py "🤔"
```

批量渲染多个 Emoji（自动复用浏览器实例）：

```bash
python cli.py "🤔" "🔥" "❤️" "🐍" -w 80
```

保存到文件且不打印到终端：

```bash
python cli.py "🤔" -o thinking.txt --no-print
```

输出 24-bit 真彩色版本（需在支持真彩色的终端中查看）：

```bash
python cli.py "🔥" --color
```

启用图像增强（对比度拉伸 + 8x 超采样）：

```bash
python cli.py "🐍" --contrast -s 8
```

## 项目结构

```text
emoji2ascii/
├── renderer.py    # Playwright 无头浏览器渲染模块
├── processor.py   # 图像处理模块（压平、灰度、缩放）
├── mapper.py      # 灰度到 ASCII 字符的映射模块
├── output.py      # 终端打印与文件输出模块
├── cli.py         # 命令行入口程序
└── README.md
```

## 开源协议

本项目采用 GNU General Public License v3.0 (GPLv3) 协议开源，详见 LICENSE 文件。

> 本项目运行时调用由 Playwright 下载的 Google Chromium 二进制文件。Chromium 受其自身的开源许可协议约束，本项目不对 Chromium 二进制文件主张任何许可。
