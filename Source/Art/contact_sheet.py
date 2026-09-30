"""Every variant plus a few assembled layouts on one sheet, for review.
python3 Source/Art/contact_sheet.py /tmp/sheet.png"""
import sys
from PIL import Image, ImageDraw

from compose import render, tinted
from draw_sprites import FACINGS, SIDE_STATES, sect_path, table_path
from slopkea_draw import CELL

WOOD = (133, 94, 62)
FABRIC = (70, 110, 150)
T = 96  # thumbnail cell


def scenes():
    # U-shaped sectional around a coffee spot, and an L table.
    s = {}
    for x in range(1, 5):
        s[(x, 5)] = ("sect", "south")
    for z in range(2, 5):
        s[(0, z)] = ("sect", "east")
        s[(5, z)] = ("sect", "west")
    s[(0, 5)] = ("sect", "south")
    s[(5, 5)] = ("sect", "south")
    t = {}
    for x in range(1, 5):
        for z in range(1, 3):
            t[(x, z)] = ("table",)
    for z in range(3, 5):
        t[(1, z)] = ("table",)
    t[(0, 1)] = ("sect", "east")
    t[(5, 2)] = ("sect", "west")
    t[(2, 0)] = ("sect", "north")
    t[(3, 3)] = ("sect", "south")
    return s, t


def main(out):
    tables = [tinted(table_path(i), WOOD) for i in range(16)]
    sects = [tinted(sect_path(f, a, b), FABRIC, sect_path(f, a, b, True))
             for f in FACINGS for a in SIDE_STATES for b in SIDE_STATES]
    s, t = scenes()
    u = render(s, {"table": WOOD, "sect": FABRIC}, (6, 6), T)
    lt = render(t, {"table": WOOD, "sect": FABRIC}, (6, 6), T)
    sheet = Image.new("RGBA", (12 * T + 40, 4 * T + 2 * T + 6 * T + 80), (40, 40, 44, 255))
    d = ImageDraw.Draw(sheet)
    d.text((10, 4), "table variants 0-15 (bits N1 E2 S4 W8 = joined)", fill="white")
    for i, im in enumerate(tables):
        sheet.alpha_composite(im.resize((T // 2 * 2, T // 2 * 2)), (10 + (i % 8) * (T + 4), 20 + (i // 8) * (T + 4)))
    y0 = 20 + 2 * (T + 4) + 10
    d.text((10, y0 - 14), "sectional: rows north/east/south/west, cols cw,ccw in a/j/c", fill="white")
    small = T // 2
    for i, im in enumerate(sects):
        r, c = divmod(i, 9)
        sheet.alpha_composite(im.resize((small, small)), (10 + c * (small + 4), y0 + r * (small + 4)))
    y1 = y0 + 4 * (small + 4) + 20
    d.text((10, y1 - 14), "assembled: U sectional; L table with seats", fill="white")
    sheet = sheet.crop((0, 0, max(sheet.width, 2 * u.width + 30), y1 + u.height + 10))
    sheet.alpha_composite(u, (10, y1))
    sheet.alpha_composite(lt, (20 + u.width, y1))
    sheet.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sheet.png")
