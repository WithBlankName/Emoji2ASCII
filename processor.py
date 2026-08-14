# processor.py
import io
from PIL import Image, ImageOps


class ImageProcessor:
    """RGBA -> 灰度图 / RGB 图像处理。

    1) 透明背景压平（白 / 黑底）
    2) 灰度化
    3) 可选对比度拉伸 / 直方图均衡
    4) 缩放到目标字符宽度（按字符 2:1 长宽比补偿）
    """

    # 终端字符通常高:宽 ≈ 2:1
    CHAR_ASPECT = 0.5

    def __init__(self, background: str = "white"):
        self.background = background

    def process(self, png_bytes: bytes, target_width: int = 60,
                contrast_stretch: bool = False,
                equalize: bool = False):
        img = Image.open(io.BytesIO(png_bytes))
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        rgb_img = self._flatten_alpha(img)
        gray = rgb_img.convert("L")

        if contrast_stretch:
            gray = ImageOps.autocontrast(gray)
        if equalize:
            gray = ImageOps.equalize(gray)

        gray_resized, rgb_resized = self._resize_pair(
            gray, rgb_img, target_width
        )
        return gray_resized, rgb_resized

    # ----- helpers -----
    def _flatten_alpha(self, img: Image.Image) -> Image.Image:
        bg_color = (255, 255, 255) if self.background == "white" else (0, 0, 0)
        background = Image.new("RGBA", img.size, bg_color + (255,))
        background.paste(img, mask=img.split()[3])
        return background.convert("RGB")

    def _resize_pair(self, gray: Image.Image, rgb: Image.Image,
                     target_width: int):
        w, h = gray.size
        if w == 0 or h == 0:
            raise ValueError("图像尺寸为 0，无法处理")
        aspect = h / w
        target_height = max(1, int(target_width * aspect * self.CHAR_ASPECT))
        size = (target_width, target_height)
        return (
            gray.resize(size, Image.LANCZOS),
            rgb.resize(size, Image.LANCZOS),
        )