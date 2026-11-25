#!/usr/bin/env python3
"""Draw the day's news infographic to /output/entry.png.

The stories of Wednesday 25 November 2026 are embedded below, each with a
region tag and colour; the program lays them out as a two-column front page
and writes the PNG, world-readable, under the 1 MiB cap.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

STORIES = [
    ("Nvidia reinstates Huang as CEO after board reversal", "US", (255, 170, 60)),
    ("AI stocks slide as AI trade falters", "US", (255, 170, 60)),
    ("Trump: Iran war funding lasts through January", "US", (255, 170, 60)),
    ("NASA ESCAPADE beams parting images of Earth", "US", (255, 170, 60)),
    ("Trump intervenes in Nvidia board fight", "US", (255, 170, 60)),
    ("NATO talks after missiles hit Poland", "EU", (120, 180, 255)),
    ("Brussels mulls extra Ukraine loan as US retreats", "EU", (120, 180, 255)),
    ("COP31 ends without climate pact", "GL", (140, 255, 170)),
    ("UN chief: no ambiguity in the science", "GL", (140, 255, 170)),
    ("Putin vows retaliation over oil-plant strikes", "RU", (255, 110, 110)),
    ("Russian strike injures 11 in Zaporizhzhia", "UA", (255, 210, 90)),
    ("Ukraine hits Russian ship in Gulf of Finland", "UA", (255, 210, 90)),
    ("Ukraine: Libya ship attack was self-defense", "UA", (255, 210, 90)),
    ("Houthis threaten Saudi ports over Hodeidah", "ME", (255, 120, 200)),
    ("Houthis take second swipe at Riyadh tower", "ME", (255, 120, 200)),
    ("Houthis close in on Aden as Yemen digs in", "ME", (255, 120, 200)),
    ("IDF warns strike on Iran could widen war", "ME", (255, 120, 200)),
    ("Israel: Iran developing chemical weapons", "ME", (255, 120, 200)),
    ("Oil falls as Hormuz traffic stays below prewar", "ME", (255, 120, 200)),
    ("Shenzhou-24 launches, first foreign astronaut", "CN", (255, 90, 90)),
    ("China probes politburo star in Xi's purge", "CN", (255, 90, 90)),
    ("Korea speaker meets Japan PM Takaichi", "AS", (170, 140, 255)),
    ("India pushes $1trn space-economy target", "IN", (120, 255, 230)),
    ("Nigeria unveils next-gen satellite models", "AF", (120, 255, 120)),
    ("Ebola Bundibugyo outbreak in DR Congo", "AF", (120, 255, 120)),
    ("Gunmen hold 24 hostage in Cartagena, Colombia", "LA", (255, 160, 120)),
    ("Gold drops; Asian stocks retreat", "AS", (170, 140, 255)),
    ("Tariff threats loom over global equities", "GL", (140, 255, 170)),
]

SIZE = (1024, 1024)
FONT_BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REG = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"


def fit(draw, text, font, max_width):
    line = text
    while draw.textlength(line + "…", font=font) > max_width and len(line) > 12:
        line = line[:-1].rstrip()
    return line + "…" if line != text else line


def draw_image():
    img = Image.new("RGB", SIZE, (12, 15, 20))
    d = ImageDraw.Draw(img)
    f_head = ImageFont.truetype(FONT_BOLD, 46)
    f_sub = ImageFont.truetype(FONT_BOLD, 22)
    f_story = ImageFont.truetype(FONT_REG, 20)
    f_tag = ImageFont.truetype(FONT_BOLD, 14)
    f_foot = ImageFont.truetype(FONT_REG, 15)

    d.rectangle([0, 0, SIZE[0], 128], fill=(20, 26, 34))
    d.text((40, 22), "THE WORLD IN ONE DAY", font=f_head, fill=(240, 240, 235))
    regions = len(set(s[1] for s in STORIES))
    d.text((40, 84), "Wednesday, 25 November 2026 · %d stories · %d regions" % (len(STORIES), regions), font=f_sub, fill=(255, 210, 90))

    body_top = 152
    rows = (len(STORIES) + 1) // 2
    row_h = (978 - body_top - 40) // rows
    col_w = (SIZE[0] - 40 * 2 - 30) // 2
    xs = [40, 40 + col_w + 30]
    for i, (txt, tag, color) in enumerate(STORIES):
        col = i // rows
        row = i % rows
        x = xs[col]
        yy = body_top + row * row_h
        d.rounded_rectangle([x, yy, x + col_w, yy + row_h - 6], radius=8, fill=(20, 26, 34))
        d.ellipse([x + 12, yy + 14, x + 22, yy + 24], fill=color)
        tw = d.textlength(tag, font=f_tag)
        chip = tuple(min(255, c // 3 + 20) for c in color)
        d.rounded_rectangle([x + 30, yy + 9, x + 30 + tw + 12, yy + 27], radius=6, fill=chip)
        d.text((x + 36, yy + 11), tag, font=f_tag, fill=color)
        d.text((x + 12, yy + 30), fit(d, txt, f_story, col_w - 44), font=f_story, fill=(228, 230, 232))

    d.rectangle([0, SIZE[1] - 44, SIZE[0], SIZE[1]], fill=(20, 26, 34))
    d.text((40, SIZE[1] - 32), "All events first reported 25 November 2026 · Reuters · Bloomberg · WSJ · Al Jazeera · NHK · NASA", font=f_foot, fill=(160, 170, 180))
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, mode=0o755, exist_ok=True)
    img = draw_image()
    dst = os.path.join(out_dir, "entry.png")
    img.save(dst)
    os.chmod(dst, 0o644)
    print("entry: wrote %s" % dst)


if __name__ == "__main__":
    sys.exit(main())
