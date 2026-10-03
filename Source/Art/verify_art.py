"""Checks the textures against the defs and the C#. Exits non-zero on a mismatch.
python3 Source/Art/verify_art.py   (from the repo root)"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image

from draw_sprites import BITS, FACINGS, ROCKER_KINDS, SIDE_STATES, rocker_path, sect_path, table_path
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
            # Joined: no outline running ALONG the edge - it continues into the
            # neighbour. An outline crossing it (the bottom of an apron) is fine, so
            # this looks for a long black run down the edge, not any black at all.
            # (It need not be solid: the gap between legs runs on under a join.)
            run = best = 0
            for p in edge_pixels(im, side, depth=1):
                run = run + 1 if p[3] > 200 and max(p[:3]) < 40 else 0
                best = max(best, run)
            check(best < 12, f"{path}: joined {side} edge has a black ring ({best}px run)")


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
            # Back to back (or against a wall): the back side is joined too.
            pb = sect_path(f, cw, ccw, back=True)
            check(os.path.exists(pb) and os.path.exists(sect_path(f, cw, ccw, True, True)), f"missing {pb}")
            if os.path.exists(pb):
                state[OPP[f]] = "j"
                check_edges(pb, {s for s, st in state.items() if st != "j"})
            mask = Image.open(m).convert("RGB")
            red = sum(1 for r, g, b in mask.get_flattened_data() if r > 127) / (CELL * CELL)
            check(red > 0.8, f"{m}: only {red:.0%} tinted")

# Rocking chairs: free-standing, so every side is silhouette; the cloth one's
# oak frame is untinted, so its mask must leave a real share black.
for kind in ROCKER_KINDS:
    for f in FACINGS:
        p = rocker_path(kind, f)
        check(os.path.exists(p), f"missing {p}")
        if os.path.exists(p):
            check_edges(p, {"north", "east", "south", "west"})
        if kind == "Cloth":
            m = rocker_path(kind, f, mask=True)
            check(os.path.exists(m), f"missing {m}")
            if os.path.exists(m):
                a = Image.open(p).getchannel("A")
                reds = [r > 127 for r, g, b in Image.open(m).convert("RGB").get_flattened_data()]
                solid = [v > 127 for v in a.get_flattened_data()]
                share = sum(r and s_ for r, s_ in zip(reds, solid)) / max(1, sum(solid))
                check(0.15 < share < 0.8, f"{m}: {share:.0%} of the chair tinted, want upholstery only")

# Desk, rug and shelf: the same open/joined edge contract.
import draw_modular as dm
for i in range(16):
    open_s = {s_ for s_, b in BITS.items() if not i & b}
    check_edges(dm.desk_path(i), open_s)
    check(os.path.exists(dm.desk_path(i, True)), f"missing {dm.desk_path(i, True)}")
n_rug = 0
for i, c in dm.rug_variants():
    p = dm.rug_path(i, c)
    check(os.path.exists(p), f"missing {p}")
    if os.path.exists(p):
        check_edges(p, {s_ for s_, b in BITS.items() if not i & b})
    n_rug += 1
check(n_rug == 47, f"{n_rug} rug variants, expected 47")
for f in FACINGS:
    for cw in "oj":
        for ccw in "oj":
            p = dm.shelf_path(f, cw, ccw)
            check(os.path.exists(dm.shelf_path(f, cw, ccw, True)), f"missing mask for {p}")
            joined = {s_ for s_, st in ((CW[f], cw), (CCW[f], ccw)) if st == "j"}
            check_edges(p, {"north", "east", "south", "west"} - joined)

# Kitchen modules and bookcase: side joins, masks, all four facings.
import draw_kitchen as dk
for f in FACINGS:
    for cw in "oj":
        for ccw in "oj":
            joined = {s_ for s_, st in ((CW[f], cw), (CCW[f], ccw)) if st == "j"}
            import draw_kitchen_tall as dkt
            for p, m in [(dk.book_path(f, cw, ccw), dk.book_path(f, cw, ccw, True))]:
                check(os.path.exists(m), f"missing {m}")
                check_edges(p, {"north", "east", "south", "west"} - joined)
            # Kitchen modules, counters and tall, and the wall cabinets: each also
            # has a "back flush to a wall" variant, where the back side is joined.
            for back in (False, True):
                j2 = joined | ({dk.OPP[f]} if back else set())
                for mod in dk.MODULES + dkt.TALL + ("WallCab",):
                    p, m = dk.kitchen_path(mod, f, cw, ccw, back=back), dk.kitchen_path(mod, f, cw, ccw, True, back)
                    check(os.path.exists(m), f"missing {m}")
                    if os.path.exists(p):
                        check_edges(p, {"north", "east", "south", "west"} - j2)
kr = open("Source/SlopkeaFurniture/KitchenRun.cs").read()
got = kr.split('Dir = "', 1)[1].split('"', 1)[0]
check(dk.kitchen_path("Cabinet", "north", "o", "o").startswith("Textures/" + got), f"KitchenRun.cs: bad Dir {got}")
bc = open("Source/SlopkeaFurniture/Building_SlopkeaBookcase.cs").read()
got = bc.split('TexPrefix = "', 1)[1].split('"', 1)[0]
# The bookcase builds <prefix><cw><ccw> and Graphic_Multi appends _<facing>.
check(dk.book_path("north", "o", "j") == f"Textures/{got}oj_north.png", f"bookcase prefix {got} vs {dk.book_path('north', 'o', 'j')}")
for p in (dk.BOOKEND_EAST, dk.BOOKEND_NORTH):
    check(os.path.exists(p), f"missing {p}")
import draw_kitchen_tall as dkt
for mod in dk.MODULES + dkt.TALL + ("WallCab",):
    check(f'KitchenPaths.Dir + "{mod}_"' in kr, f"KitchenRun.cs: no print path for {mod}")

# Bench, wardrobe (side joins) and divider, planter (bits).
import draw_more as dmo
for f in FACINGS:
    for cw in "oj":
        for ccw in "oj":
            joined = {s_ for s_, st in ((CW[f], cw), (CCW[f], ccw)) if st == "j"}
            for kind in ("Bench", "Wardrobe"):
                check(os.path.exists(dmo.side_path(kind, f, cw, ccw, True)), f"missing {kind} mask")
                check_edges(dmo.side_path(kind, f, cw, ccw), {"north", "east", "south", "west"} - joined)
for i in range(16):
    open_s = {s_ for s_, b in BITS.items() if not i & b}
    for fn in (dmo.divider_path, dmo.planter_path):
        check(os.path.exists(fn(i, True)), f"missing {fn(i, True)}")
        check_edges(fn(i), open_s)
mf = open("Source/SlopkeaFurniture/MoreFurniture.cs").read()
for name, sample in (("Bench", dmo.side_path("Bench", "north", "o", "o")),
                     ("Wardrobe", dmo.side_path("Wardrobe", "north", "o", "o")),
                     ("Divider", dmo.divider_path(0)), ("Planter", dmo.planter_path(0))):
    got = mf.split(f'{name} = "', 1)[1].split('"', 1)[0]
    check(sample.startswith("Textures/" + got), f"MoreFurniture.cs {name}: {got} vs {sample}")

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
                   ("Building_SlopkeaSectional.cs", sect_path("north", "a", "a")),
                   ("Building_SlopkeaDesk.cs", dm.desk_path(0)),
                   ("Building_SlopkeaRug.cs", dm.rug_path(0, 0)),
                   ("Building_SlopkeaShelf.cs", dm.shelf_path("north", "o", "o"))):
    src = open("Source/SlopkeaFurniture/" + cs).read()
    prefix = re.search(r'TexPrefix = "([^"]+)"', src).group(1)
    check(sample.startswith("Textures/" + prefix), f"{cs}: TexPrefix {prefix} does not match {sample}")
src = open("Source/SlopkeaFurniture/Building_SlopkeaSectional.cs").read()
check('"north", "east", "south", "west"' in src, "sectional facing names out of Rot4 order")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("art ok: table, sectional, rocking chairs, desk, rug, shelf, kitchen, bookcase, bench, wardrobe, divider and planter variants; defs and C# agree")
