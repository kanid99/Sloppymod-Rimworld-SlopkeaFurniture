"""Scores furniture textures on the style metrics that matter for sitting beside
Vanilla Furniture Expanded, and prints ours against theirs.

python3 Source/Art/measure_furniture.py [path to VFE checkout]

Only stuff-tintable greyscale pixels are measured for tone (colour pixels are
fittings), and masks are skipped.
"""
import glob
import os
import statistics as st
import sys

from PIL import Image, ImageFilter

VFE = sys.argv[1] if len(sys.argv) > 1 else "/home/user/vanilla-expanded/vanillafurnitureexpanded"
VFE_GLOB = VFE + "/Textures/NewThings/Furniture/**/*.png"
OURS_GLOB = "Textures/Things/Building/Furniture/Slopkea/**/*.png"


def cell_px(path, im):
    """Pixels per cell: VFE authors 1x1 at 128 (couch 120); ours at 192."""
    return 192 if "Slopkea" in path else (120 if "ModularCouch" in path else 128)


def metrics(path):
    im = Image.open(path).convert("RGBA")
    px = list(im.get_flattened_data())
    solid = [p for p in px if p[3] > 200]
    if len(solid) < 50:
        return None
    grey = [p for p in solid if max(p[:3]) - min(p[:3]) < 12 and max(p[:3]) > 40]
    lum = [sum(p[:3]) / 3 for p in grey] or [0]
    black = sum(1 for p in solid if max(p[:3]) < 40)
    # Outline width: black pixels per unit of silhouette perimeter, scaled to a cell.
    a = im.getchannel("A").point(lambda v: 255 if v > 200 else 0)
    edge = sum(1 for v in a.filter(ImageFilter.FIND_EDGES).get_flattened_data() if v)
    outline = black / max(edge, 1) / cell_px(path, im) * 100          # % of a cell
    # Smoothness: distinct grey levels on the lit faces (flat fills score low).
    levels = len({int(v) // 2 for v in lum})
    return dict(lum=st.median(lum), p90=sorted(lum)[int(len(lum) * 0.9)],
                std=st.pstdev(lum), outline=outline, levels=levels)


def score(pattern):
    rows = []
    for f in glob.glob(pattern, recursive=True):
        if f.endswith("m.png") or "Bookend" in f:
            continue
        m = metrics(f)
        if m:
            rows.append(m)
    return rows


def summary(name, rows):
    out = {k: st.median(r[k] for r in rows) for k in rows[0]}
    lo = {k: min(r[k] for r in rows) for k in rows[0]}
    hi = {k: max(r[k] for r in rows) for k in rows[0]}
    return out, lo, hi


if __name__ == "__main__":
    vfe, ours = score(VFE_GLOB), score(OURS_GLOB)
    (vm, vlo, vhi), (om, olo, ohi) = summary("vfe", vfe), summary("ours", ours)
    print(f"{'metric':<34}{'ours (median)':>14}{'VFE (median)':>14}{'VFE range':>16}")
    names = {"lum": "grey face luminance (median)", "p90": "grey face highlight (p90)",
             "std": "tonal contrast (std)", "outline": "outline width (% of a cell)",
             "levels": "distinct grey levels (smoothness)"}
    for k, label in names.items():
        print(f"{label:<34}{om[k]:>14.1f}{vm[k]:>14.1f}{vlo[k]:>8.1f}-{vhi[k]:<7.1f}")
    print(f"\n{len(ours)} of ours, {len(vfe)} of VFE's")
