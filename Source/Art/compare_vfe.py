"""Side by side with Vanilla Furniture Expanded, same scale (128px a cell) and
same stuff colours, for the art review. Needs a VFE checkout.
python3 Source/Art/compare_vfe.py OUT.png [VFE path]"""
import sys

from PIL import Image, ImageChops, ImageDraw

from compose import render

VFE = (sys.argv[2] if len(sys.argv) > 2 else "/home/user/vanilla-expanded/vanillafurnitureexpanded") \
    + "/Textures/NewThings/Furniture/"
CELL = 128
WOOD, FABRIC, BG = (150, 108, 70), (96, 128, 168), (92, 84, 72)


def tint(im, color, mask=None):
    t = ImageChops.multiply(im, Image.new("RGBA", im.size, color + (255,)))
    if mask is not None:
        t = Image.composite(t, im, mask.convert("RGB").getchannel("R"))
    t.putalpha(im.getchannel("A"))
    return t


def vfe(name, color, cells):
    im = Image.open(VFE + name).convert("RGBA")
    mpath = VFE + name.replace(".png", "m.png")
    try:
        m = Image.open(mpath)
    except FileNotFoundError:
        m = None
    return tint(im.resize((cells[0] * CELL, cells[1] * CELL), Image.LANCZOS), color,
                m.resize((cells[0] * CELL, cells[1] * CELL)) if m else None)


def panel(w, h):
    return Image.new("RGBA", (w * CELL, h * CELL), BG + (255,))


def main(out):
    rows = []
    # Couch: VFE's modular L vs ours.
    a = panel(3, 2)
    for x, n in enumerate(("UpLeft_Outer", "UpMiddle_Straight", "UpRight_Outer")):
        a.alpha_composite(vfe(f"ModularCouch/ModularCouch_{n}.png", FABRIC, (1, 1)), (x * CELL, 0))
    b = render({(0, 1): ("sect", "south"), (1, 1): ("sect", "south"), (2, 1): ("sect", "south")},
               {"sect": FABRIC, "table": WOOD}, (3, 2), CELL)
    rows.append(("modular couch", a, b))
    # Table: VFE 1x1 vs ours 1x1 and a 2x1.
    a = panel(3, 2)
    a.alpha_composite(vfe("Tables/Table1x1.png", WOOD, (1, 1)), (0, 0))
    b = render({(0, 1): ("table",), (1, 1): ("table",), (2, 1): ("table",)}, {"table": WOOD, "sect": FABRIC}, (3, 2), CELL)
    rows.append(("table", a, b))
    # Wardrobe: VFE 3x? drawn at 3 cells vs our run of 3.
    a = panel(3, 2)
    a.alpha_composite(vfe("Wardrobe/Wardrobe_south.png", WOOD, (2, 2)), (0, 0))
    b = render({(x, 1): ("Wardrobe", "south") for x in range(3)}, {"Wardrobe": WOOD}, (3, 2), CELL)
    rows.append(("wardrobe", a, b))
    # Chairs: VFE armchair vs our glider / rocker.
    a = panel(3, 2)
    a.alpha_composite(vfe("RoyalArmchair/RoyalArmchair_south.png", FABRIC, (1, 1)), (0, 0))
    a.alpha_composite(vfe("SchoolChair/SchoolChair_south.png", WOOD, (1, 1)), (CELL, 0))
    b = panel(3, 2)
    from draw_sprites import rocker_path
    for k, (kind, col) in enumerate((("Cloth", FABRIC), ("Wood", WOOD))):
        p = rocker_path(kind, "south")
        m = Image.open(rocker_path(kind, "south", True)) if kind == "Cloth" else None
        b.alpha_composite(tint(Image.open(p).convert("RGBA").resize((CELL, CELL), Image.LANCZOS), col,
                               m.resize((CELL, CELL)) if m else None), (k * CELL, 0))
    rows.append(("chairs", a, b))
    # Shelving: VFE weapon shelf vs our cube shelf and bookcase.
    a = panel(3, 2)
    a.alpha_composite(vfe("WeaponRack/WeaponShelf_south.png", WOOD, (2, 1)), (0, 0))
    b = render({(0, 1): ("shelf", "south"), (1, 1): ("shelf", "south"), (2, 0): ("book", "south")},
               {"shelf": WOOD, "book": WOOD}, (3, 2), CELL)
    rows.append(("shelving", a, b))

    W = 2 * 3 * CELL + 60
    H = len(rows) * (2 * CELL + 30) + 30
    sheet = Image.new("RGBA", (W, H), (40, 40, 44, 255))
    d = ImageDraw.Draw(sheet)
    d.text((20, 6), "VFE", fill="white")
    d.text((40 + 3 * CELL, 6), "Slopkea", fill="white")
    for k, (name, a, b) in enumerate(rows):
        y = 24 + k * (2 * CELL + 30)
        d.text((20, y), name, fill=(200, 200, 200))
        sheet.alpha_composite(a, (20, y + 14))
        sheet.alpha_composite(b, (40 + 3 * CELL, y + 14))
    sheet.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1])
