from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SIZE = (1280, 720)
FRONT = ROOT / "source" / "robot-front.jpg"
ANGLE = ROOT / "source" / "robot-angle.jpg"
OUT = ROOT / "robot-ai-thumbnail.png"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


IMPACT = "C:/Windows/Fonts/impact.ttf"
ARIAL_BOLD = "C:/Windows/Fonts/arialbd.ttf"


def glow_text(layer: Image.Image, xy: tuple[int, int], text: str, *, fill: str, size: int) -> None:
    face = font(IMPACT, size)
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text(xy, text, font=face, fill=(0, 0, 0, 230), stroke_width=16, stroke_fill=(0, 0, 0, 230))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    layer.alpha_composite(shadow)
    ImageDraw.Draw(layer).text(
        xy,
        text,
        font=face,
        fill=fill,
        stroke_width=7,
        stroke_fill="#071018",
    )


def rounded_photo(source: Image.Image, size: tuple[int, int], radius: int) -> Image.Image:
    fitted = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS, centering=(0.48, 0.48))
    fitted = ImageEnhance.Contrast(fitted).enhance(1.15)
    fitted = ImageEnhance.Color(fitted).enhance(0.86).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    fitted.putalpha(mask)
    return fitted


def main() -> None:
    angle = Image.open(ANGLE).convert("RGB")
    front = Image.open(FRONT).convert("RGB")

    background = ImageOps.fit(angle, SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(18))
    background = ImageEnhance.Brightness(background).enhance(0.30).convert("RGBA")

    canvas = Image.new("RGBA", SIZE, "#071018")
    canvas.alpha_composite(background)
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Quiet technical grid keeps the background legible without inventing imagery.
    for x in range(0, SIZE[0], 64):
        draw.line((x, 0, x, SIZE[1]), fill=(58, 226, 255, 18), width=1)
    for y in range(0, SIZE[1], 64):
        draw.line((0, y, SIZE[0], y), fill=(58, 226, 255, 18), width=1)

    draw.polygon([(0, 0), (710, 0), (600, 720), (0, 720)], fill=(3, 10, 18, 232))
    draw.polygon([(615, 0), (710, 0), (600, 720), (540, 720)], fill=(58, 226, 255, 46))

    # The supplied rover remains the dominant factual subject.
    card_xy = (672, 62)
    card_size = (548, 596)
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((660, 54, 1232, 676), radius=30, fill=(0, 0, 0, 220))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow)
    photo = rounded_photo(front, card_size, 26)
    canvas.alpha_composite(photo, card_xy)
    draw.rounded_rectangle((665, 55, 1227, 665), radius=32, outline=(61, 233, 255, 255), width=7)

    # Reticle highlights the robot camera, the point where autonomy becomes tangible.
    cx, cy = 952, 220
    for radius, alpha in ((62, 70), (46, 130), (32, 240)):
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(255, 62, 72, alpha), width=4)
    for dx, dy in ((-82, 0), (82, 0), (0, -82), (0, 82)):
        draw.line((cx + dx * 0.62, cy + dy * 0.62, cx + dx, cy + dy), fill=(255, 62, 72, 230), width=6)
    draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(255, 62, 72, 255))

    # Compact copy communicates the conflict before the full video title is read.
    draw.rounded_rectangle((52, 48, 458, 105), radius=10, fill=(36, 213, 242, 255))
    draw.text((72, 61), "CHATGPT + REAL ROBOT", font=font(ARIAL_BOLD, 25), fill="#071018")
    glow_text(canvas, (48, 132), "IT TOOK", fill="#FFFFFF", size=116)
    glow_text(canvas, (48, 253), "CONTROL", fill="#FFD93D", size=116)

    draw.rounded_rectangle((50, 434, 550, 525), radius=16, fill=(255, 62, 72, 242))
    draw.text((77, 451), "NO DRIVER. JUST CODE.", font=font(ARIAL_BOLD, 41), fill="white")

    draw.line((551, 477, 733, 322), fill=(255, 211, 49, 255), width=18)
    draw.polygon([(735, 320), (697, 325), (723, 355)], fill=(255, 211, 49, 255))

    draw.rounded_rectangle((52, 610, 515, 671), radius=12, fill=(4, 13, 22, 220), outline=(58, 226, 255, 160), width=2)
    draw.text((74, 625), "ROBOTICS  /  AI  /  EXPERIMENT", font=font(ARIAL_BOLD, 25), fill="#D9F9FF")

    # A restrained vignette anchors the high-contrast center.
    vignette = Image.new("L", SIZE, 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse((-180, -120, 1460, 900), fill=210)
    vignette = ImageOps.invert(vignette).filter(ImageFilter.GaussianBlur(85))
    shade = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shade.putalpha(vignette.point(lambda p: int(p * 0.55)))
    canvas.alpha_composite(shade)

    canvas.convert("RGB").save(OUT, quality=94, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
