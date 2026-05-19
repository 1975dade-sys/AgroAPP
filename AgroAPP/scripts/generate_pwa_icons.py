"""Genera le icone PNG per PWA e app native (eseguire una volta)."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Installa Pillow: pip install pillow") from None

STATIC = Path(__file__).resolve().parent.parent / "static"
COLOR_BG = (45, 106, 79)
COLOR_FG = (255, 255, 255)


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), COLOR_BG)
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 10,
        fill=(58, 130, 95),
    )
    font_size = max(size // 3, 24)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    text = "🌾"
    # Emoji non sempre renderizzata: usa lettera A stilizzata
    letter = "A"
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - tw) / 2, (size - th) / 2 - size // 20),
        letter,
        fill=COLOR_FG,
        font=font,
    )
    return img


def main() -> None:
    STATIC.mkdir(exist_ok=True)
    for size in (192, 512):
        path = STATIC / f"icon-{size}.png"
        draw_icon(size).save(path, "PNG")
        print(f"Creato {path}")
    # Apple touch icon
    draw_icon(180).save(STATIC / "apple-touch-icon.png", "PNG")
    print(f"Creato {STATIC / 'apple-touch-icon.png'}")


if __name__ == "__main__":
    main()
