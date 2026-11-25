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
    """Return a single line that never exceeds max_width (ellipsis fallback)."""
    line = text
    while draw.textlength(line + "…", font=font) > max_width and len(line) > 12:
        line = line[:-1].rstrip()
    return line + "…" if line != text else line


def wrap(draw, text, font, max_width):
    """Split text into up to 3 lines that each fit max_width.

    Greedy word wrap; falls back to hard character trim for a single
    over-long word so no line can ever overflow its box.
    """
    lines = []
    for word in text.split():
        candidate = (lines[-1] + " " + word) if lines else word
        if draw.textlength(candidate, font=font) <= max_width:
            if not lines:
                lines.append(candidate)
            else:
                lines[-1] = candidate
            continue
        if not lines or len(lines) == 3:
            # Hard trim: only reached for a very long single word.
            line = word
            while draw.textlength(line + "…", font=font) > max_width and len(line) > 4:
                line = line[:-1].rstrip()
            lines.append(line + "…")
        else:
            lines.append(word)
    return lines


def draw_image():
    """Compose the whole front page and return the finished image."""
    img = Image.new("RGB", SIZE, (12, 15, 20))
    d = ImageDraw.Draw(img)

    # -- Fonts ------------------------------------------------------------
    f_head = ImageFont.truetype(FONT_BOLD, 44)
    f_sub = ImageFont.truetype(FONT_BOLD, 21)
    f_story = ImageFont.truetype(FONT_REG, 20)
    f_tag = ImageFont.truetype(FONT_BOLD, 14)
    f_foot = ImageFont.truetype(FONT_REG, 14)

    # -- Header: banner, title, subtitle ----------------------------------
    header_h = 124
    d.rectangle([0, 0, SIZE[0], header_h], fill=(20, 26, 34))
    title = "THE WORLD IN ONE DAY"
    regions = len(set(s[1] for s in STORIES))
    sub = "Wednesday, 25 November 2026 · %d stories · %d regions" % (
        len(STORIES), regions)

    # Shrink the title until it fits the padded width, so it is never cut.
    title_pad = 80
    size = 44
    while d.textlength(title, font=ImageFont.truetype(FONT_BOLD, size)) > SIZE[0] - title_pad and size > 18:
        size -= 2
    f_title = ImageFont.truetype(FONT_BOLD, size)
    # Center the title block vertically: title on top, subtitle under it.
    title_w = d.textlength(title, font=f_title)
    d.text(((SIZE[0] - title_w) // 2, 26), title, font=f_title, fill=(240, 240, 235))
    sub_w = d.textlength(sub, font=f_sub)
    d.text(((SIZE[0] - sub_w) // 2, 84), sub, font=f_sub, fill=(255, 210, 90))
    # Thin separator line between header and body.
    d.line([0, header_h + 6, SIZE[0], header_h + 6], fill=(60, 70, 84), width=2)

    # -- Body: two columns of story cards ---------------------------------
    body_top = 148
    footer_h = 44
    body_bottom = SIZE[1] - footer_h - 16
    margin = 36
    gap = 16            # tighter gap between cards
    card_gap = 10       # vertical breathing room between stacked cards
    col_w = (SIZE[0] - margin * 2 - gap) // 2
    xs = [margin, margin + col_w + gap]

    # Fill columns top-to-bottom, balanced: left column gets the extra row.
    rows = (len(STORIES) + 1) // 2
    # Reserve one card_gap per gap between cards (rows - 1 gaps).
    row_h = (body_bottom - body_top - (rows - 1) * card_gap) // rows
    text_x = 14           # text indent inside a card
    tag_chip_y = 9        # tag chip offset from card top
    text_top = 30         # story text offset from card top
    line_h = 24           # story text line height (fits wrapped lines)

    for i, (txt, tag, color) in enumerate(STORIES):
        col = 0 if i < rows else 1
        row = i if i < rows else i - rows
        x = xs[col]
        yy = body_top + row * (row_h + card_gap)
        # Card background: lighter surface + subtle region-tinted border
        # for higher contrast against the dark page background.
        card_fill = (30, 36, 46)
        card_h = row_h - 6
        # Soft drop shadow: dark rect offset a few px down/right, drawn
        # before the card so it peeks out only at the bottom-right edge.
        d.rounded_rectangle(
            [x + 4, yy + 4, x + col_w + 4, yy + card_h + 4], radius=8,
            fill=(5, 7, 10))
        d.rounded_rectangle(
            [x, yy, x + col_w, yy + card_h], radius=8, fill=card_fill,
            outline=tuple(c // 3 for c in color), width=1)
        # Region colour dot.
        d.ellipse([x + text_x, yy + 13, x + text_x + 10, yy + 23], fill=color)
        # Region tag chip (tinted background + coloured text).
        tw = d.textlength(tag, font=f_tag)
        chip = tuple(min(255, c // 3 + 20) for c in color)
        d.rounded_rectangle(
            [x + text_x + 18, yy + tag_chip_y, x + text_x + 24 + tw, yy + tag_chip_y + 18],
            radius=6, fill=chip)
        d.text((x + text_x + 24, yy + tag_chip_y + 2), tag, font=f_tag, fill=color)
        # Story headline: wrap to fit the card instead of truncating.
        max_w = col_w - text_x - 18
        lines = wrap(d, txt, f_story, max_w)
        for j, line in enumerate(lines):
            ly = yy + text_top + j * line_h
            if ly > yy + row_h - 6:  # safety: never draw outside card
                break
            d.text((x + text_x, ly), line, font=f_story, fill=(228, 230, 232))

    # -- Footer ------------------------------------------------------------
    d.rectangle([0, SIZE[1] - footer_h, SIZE[0], SIZE[1]], fill=(20, 26, 34))
    foot = "All events first reported 25 November 2026 · Reuters · Bloomberg · WSJ · Al Jazeera · NHK · NASA"
    # Truncate the footer only if it would overflow the padded width.
    d.text((margin, SIZE[1] - 30),
           fit(d, foot, f_foot, SIZE[0] - margin * 2),
           font=f_foot, fill=(160, 170, 180))
    return img


def main():
    # Resolve the output directory (default /output, override via env).
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, mode=0o755, exist_ok=True)
    img = draw_image()
    dst = os.path.join(out_dir, "entry.png")
    img.save(dst)
    os.chmod(dst, 0o644)
    print("entry: wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
