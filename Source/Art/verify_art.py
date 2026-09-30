"""Checks the textures against the defs and the C#. Exits non-zero on a mismatch.
python3 Source/Art/verify_art.py   (from the repo root)"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image

from draw_sprites import BITS, FACINGS, SIDE_STATES, sect_path, table_path
from slopkea_draw import CELL, CW, CCW, OPP

errors = []


def check(ok, msg):
    if not ok:
        errors.append(msg)


def edge_pixels(im, side, depth=2, margin=8):
    """One edge, less `margin` px at each end: the corners belong to the sides either way."""
    w, h = im.size
    m = margin
    box = {"north": (m, 0, w - m, depth), "south": (m, h - depth, w - m, h),
           "west": (0, m, depth, h - m), "east": (w - depth, m, w, h - m)}[side]
    return list(im.crop(box).get_flattened_data())


def black_share(px):
    solid = [p for p in px if p[3] > 200]
    if not solid:
        return None
    return sum(1 for p in solid if max(p[:3]) < 40) / len(solid)


def solid_share(px):
    return sum(1 for p in px if p[3] > 200) / len(px)


def check_edges(path, open_sides):
    im = Image.open(path).convert("RGBA")
    check(im.size == (CELL, CELL), f"{path}: {im.size}, want {CELL}x{CELL}")
    for side in ("north", "east", "south", "west"):
        px = edge_pixels(im, side)
        if side in open_sides:
            # Open: whatever is drawn at the edge is silhouette ring (it may be empty).
            b = black_share(px)
            check(b is None or b > 0.9, f"{path}: open {side} edge has no silhouette ring")
        else:
            # Joined: no black - it continues into the neighbour. (It need not be
            # solid: the gap between a table's legs runs on under a joined side.)
            check((black_share(px) or 0) < 0.02, f"{path}: joined {side} edge has a black ring")


# Textures vs the variant rules.
for i in range(16):
    p = table_path(i)
    check(os.path.exists(p), f"missing {p}")
    if os.path.exists(p):
        check_edges(p, {s for s, b in BITS.items() if not i & b})

for f in FACINGS:
    for cw in SIDE_STATES:
        for ccw in SIDE_STATES:
            p, m = sect_path(f, cw, ccw), sect_path(f, cw, ccw, mask=True)
            for q in (p, m):
                check(os.path.exists(q), f"missing {q}")
            if not os.path.exists(p):
                continue
            front_joined = "c" in (cw, ccw)
            state = {f: "j" if front_joined else "o", OPP[f]: "o", CW[f]: cw, CCW[f]: ccw}
            check_edges(p, {s for s, st in state.items() if st != "j"})
            mask = Image.open(m).convert("RGB")
            red = sum(1 for r, g, b in mask.get_flattened_data() if r > 127) / (CELL * CELL)
            check(red > 0.8, f"{m}: only {red:.0%} tinted")

# Joined edges carry on into the neighbour: the two edges that meet must match.
def edge_mean(path, side):
    px = edge_pixels(Image.open(path).convert("RGBA"), side, 1)
    return sum(sum(p[:3]) for p in px) / (3 * len(px))

for a, b, side in ((2, 8, "east"), (4, 1, "south")):
    d = abs(edge_mean(table_path(a), side) - edge_mean(table_path(b), OPP[side]))
    check(d < 12, f"table {a} {side} edge and table {b} {OPP[side]} edge differ by {d:.0f}")

# Textures vs the defs.
root = ET.parse("Defs/ThingDefs_Buildings/Slopkea_Furniture.xml").getroot()
for td in root.iter("ThingDef"):
    gd = td.find("graphicData")
    if gd is None:
        continue
    path = "Textures/" + gd.findtext("texPath")
    if gd.findtext("graphicClass") == "Graphic_Multi":
        for f in FACINGS:
            check(os.path.exists(f"{path}_{f}.png"), f"def {td.findtext('defName')}: missing {path}_{f}.png")
            if gd.findtext("shaderType") == "CutoutComplex":
                # Graphic_Multi appends "m" with no underscore; "_north_m" silently finds nothing.
                check(os.path.exists(f"{path}_{f}m.png"), f"missing mask {path}_{f}m.png")
    else:
        check(os.path.exists(path + ".png"), f"def {td.findtext('defName')}: missing {path}.png")

# Textures vs the C#: the path prefixes the code builds must be the art's.
for cs, sample in (("Building_SlopkeaTable.cs", table_path(0)),
                   ("Building_SlopkeaSectional.cs", sect_path("north", "a", "a"))):
    src = open("Source/SlopkeaFurniture/" + cs).read()
    prefix = re.search(r'TexPrefix = "([^"]+)"', src).group(1)
    check(sample.startswith("Textures/" + prefix), f"{cs}: TexPrefix {prefix} does not match {sample}")
src = open("Source/SlopkeaFurniture/Building_SlopkeaSectional.cs").read()
check('"north", "east", "south", "west"' in src, "sectional facing names out of Rot4 order")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("art ok: 16 table variants, 36 sectional variants + masks, defs and C# agree")
