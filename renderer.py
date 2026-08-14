# renderer.py
from playwright.sync_api import sync_playwright


class EmojiRenderer:
    """使用 Playwright 无头 Chromium 渲染 emoji 并截图。

    支持 context-manager 用法，浏览器实例可复用以批量处理。
    """

    DEFAULT_HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ background: transparent; }}
        #emoji {{
            font-size: {font_size}px;
            line-height: 1;
            display: inline-block;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: geometricPrecision;
            font-family: 'Apple Color Emoji', 'Segoe UI Emoji',
                         'Noto Color Emoji', 'Twemoji Mozilla',
                         'EmojiOne Color', sans-serif;
        }}
    </style>
    </head>
    <body>
        <span id="emoji"></span>
    </body>
    </html>
    """

    def __init__(self, device_scale_factor: int = 4,
                 font_size: int = 240, headless: bool = True,
                 font_load_timeout_ms: int = 5000):
        self.device_scale_factor = device_scale_factor
        self.font_size = font_size
        self.headless = headless
        self.font_load_timeout_ms = font_load_timeout_ms

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    # ----- context manager -----
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ----- lifecycle -----
    def start(self):
        if self._page is not None:
            return self
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)

        # 修正：移除了 transparent=True
        self._context = self._browser.new_context(
            device_scale_factor=self.device_scale_factor,
            viewport={"width": 1024, "height": 1024},
        )

        self._page = self._context.new_page()
        html = self.DEFAULT_HTML_TEMPLATE.format(font_size=self.font_size)
        self._page.set_content(html)

        # 等待一次字体 ready，保证后续渲染时 emoji 字体已加载
        try:
            self._page.wait_for_function(
                "document.fonts && document.fonts.status === 'loaded'",
                timeout=self.font_load_timeout_ms,
            )
        except Exception as e:
            raise RuntimeError(f"Emoji 字体加载超时: {e}") from e
        return self

    def close(self):
        for attr in ("_page", "_context", "_browser"):
            obj = getattr(self, attr)
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass
                setattr(self, attr, None)
        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    # ----- render -----
    def render(self, emoji: str) -> bytes:
        """渲染单个 emoji，返回 PNG 字节流（RGBA，透明背景）。"""
        if self._page is None:
            raise RuntimeError("Renderer 未启动，请先调用 start() 或使用 with 语法。")
        try:
            self._page.evaluate(
                "(e) => document.getElementById('emoji').textContent = e", emoji
            )
            # 再次确保字体就绪
            self._page.wait_for_function(
                "document.fonts && document.fonts.status === 'loaded'",
                timeout=self.font_load_timeout_ms,
            )
            # 给渲染一帧的时间
            self._page.wait_for_timeout(80)

            element = self._page.query_selector("#emoji")
            if element is None:
                raise RuntimeError("找不到 #emoji 节点")

            # omit_background=True 会自动将未渲染的区域变为透明，无需在 context 设置 transparent
            png_bytes = element.screenshot(type="png", omit_background=True)

            if not png_bytes:
                raise RuntimeError("截图为空")
            return png_bytes
        except Exception as e:
            raise RuntimeError(f"渲染 emoji '{emoji}' 失败: {e}") from e