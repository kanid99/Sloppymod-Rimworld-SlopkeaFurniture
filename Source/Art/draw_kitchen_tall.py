"""SKÅPKÖK tall modules (hutch, wall oven, fridge) and the wall-cabinet overlay.

Tall modules join the kitchen run like the counters: `Slopkea_<Module>_<facing>_<cw><ccw>`.
The wall cabinets are not a building: they are an overlay a counter module prints
above pawns when "fit wall cabinets" is on, `Slopkea_WallCab_<facing>_<cw><ccw>`,
hanging over the back of the counter.
"""
from PIL import Image, ImageDraw

from draw_kitchen import (OPP, BURNER, CCW, CW, SIDES, STEEL, STEEL_DARK, STEEL_LIT, STONE, STONE_EDGE,
                          STONE_LIT, joined_sides, kitchen_path)
from slopkea_draw import C, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, Canvas, px

TALL = ("Hutch", "Oven", "Fridge")
COLD = (120, 190, 230)        # the fridge's one accent: its powered indicator
SHELF_BACK = (176, 176, 176)
PLATE, PLATE_RIM = (246, 246, 242), (196, 196, 190)


def doors(cv, x0, x1, y0, y1, n=2, handle="bar"):
    """`n` recessed doors across (x0..x1), with steel handles at the meeting edges."""
    cv.rect((x0, y0, x1, y1), WALL)
    w = (x1 - x0) / n
    for k in range(n):
        d0, d1 = x0 + k * w + 0.012, x0 + (k + 1) * w - 0.012
        cv.rect((d0, y0 + 0.012, d1, y1 - 0.012), TOP)
        cv.rect((d0, y0 + 0.012, d1, y0 + 0.026), TOP_LIT)
        if y1 - y0 > 0.2:
            cv.rect((d0 + 0.03, y0 + 0.06, d1 - 0.03, y1 - 0.05), SEAM)
            cv.rect((d0 + 0.04, y0 + 0.07, d1 - 0.04, y1 - 0.06), TOP)
    if handle == "bar":
        for k in range(n):
            hx = x0 + (k + 1) * w - 0.06 if k % 2 == 0 else x0 + k * w + 0.06
            cv.rect((hx - 0.01, y0 + 0.04, hx + 0.01, y0 + min(0.16, (y1 - y0) * 0.6)), STEEL_DARK, tint=False)


UPPER = 0.36        # depth of the hutch's upper shelving, at its back


def draw_tall(module, facing, cw, ccw, back=False):
    """Hutch, wall oven and fridge, seen from above like the counters they join:
    the top covers the cell, and the unit's face is the strip along the
    screen-bottom edge - taller than a counter's, because the unit is. The front
    is on that strip only when the unit faces south; in the side views it is a
    band down the front."""
    from slopkea_units import CORNER, gaps_x, gaps_y, unit_base
    joined = joined_sides(facing, cw, ccw) | ({OPP[facing]} if back else set())
    open_sides = set(SIDES) - joined
    cv = Canvas()
    u = unit_base(cv, facing, joined, strip_h=0.22)
    x0, x1, y0, ty1 = u["x0"], u["x1"], u["y0"], u["ty1"]
    r, f = u["strip"], u["front"]
    horiz = facing in ("north", "south")

    if module == "Hutch":
        # Upper shelving at the back, a worktop in front of it with plates on.
        tx0, tx1 = (x0, x1) if horiz else ((x0, f[0]) if facing == "east" and f else
                                           ((f[2], x1) if f else (x0, x1)))
        if facing == "south":
            work, edge, shade = (tx0, y0 + UPPER, tx1, ty1), (tx0, y0 + UPPER - 0.02, tx1, y0 + UPPER), (tx0, y0 + UPPER, tx1, y0 + UPPER + 0.045)
        elif facing == "north":
            work, edge, shade = (tx0, y0, tx1, ty1 - UPPER), (tx0, ty1 - UPPER, tx1, ty1 - UPPER + 0.02), None
        elif facing == "east":
            work, edge, shade = (x0 + UPPER, y0, tx1, ty1), (x0 + UPPER - 0.02, y0, x0 + UPPER, ty1), (x0 + UPPER, y0, x0 + UPPER + 0.045, ty1)
        else:
            work, edge, shade = (tx0, y0, x1 - UPPER, ty1), (x1 - UPPER, y0, x1 - UPPER + 0.02, ty1), None
        cv.rect(work, STONE, tint=False)
        if shade:
            cv.rect(shade, STONE_EDGE, tint=False)                 # the shelving's shadow
        cv.rect(edge, WALL_DARK)
        if facing in ("south", "north") and "south" not in joined:
            cv.rect((work[0], ty1 - 0.022, work[2], ty1), STONE_EDGE, tint=False) if facing == "south" else None
        cxw, cyw = (work[0] + work[2]) / 2, (work[1] + work[3]) / 2
        for t in (0.2, 0.5, 0.8):                                   # the same spots in every cell of a run
            px_, py_ = (t, cyw) if horiz else (cxw, t)
            if not (work[0] + 0.05 <= px_ <= work[2] - 0.05 and work[1] + 0.05 <= py_ <= work[3] - 0.05):
                px_, py_ = ((px_, cyw) if horiz else (cxw, work[3] - 0.11))
                if not horiz and py_ - 0.5 < 0.2:
                    continue
            rad = 0.085
            cv.ellipse((px_ - rad, py_ - rad, px_ + rad, py_ + rad), PLATE_RIM, tint=False)
            cv.ellipse((px_ - rad * 0.68, py_ - rad * 0.68, px_ + rad * 0.68, py_ + rad * 0.68), PLATE, tint=False)
    elif module == "Fridge":
        # A vent grille at the back of the top.
        if horiz:
            gy = y0 + 0.07 if facing == "south" else ty1 - 0.13
            for k in range(3):
                cv.rect((0.28, gy + k * 0.025, 0.72, gy + k * 0.025 + 0.012), STEEL_DARK, tint=False)
        else:
            gx = x0 + 0.07 if facing == "east" else x1 - 0.13
            for k in range(3):
                cv.rect((gx + k * 0.025, 0.28, gx + k * 0.025 + 0.012, 0.72), STEEL_DARK, tint=False)

    if r and facing == "south":
        cv.rect((r[0], r[1] + 0.02, r[2], r[3] - 0.015), TOP)      # door fronts
        if module == "Hutch":
            gaps_x(cv, r, joined)
            for hx in (0.42, 0.58):
                cv.rect((hx - 0.012, r[1] + 0.04, hx + 0.012, r[3] - 0.04), STEEL_DARK, tint=False)
        elif module == "Oven":
            # A steel fascia with a dark glass door and a bar handle.
            cv.rect((0.14, r[1] + 0.012, 0.86, r[3] - 0.008), STEEL, tint=False)
            cv.rect((0.14, r[1] + 0.012, 0.86, r[1] + 0.03), STEEL_LIT, tint=False)
            cv.rect((0.22, r[1] + 0.075, 0.78, r[3] - 0.025), BURNER, tint=False)
            cv.rect((0.26, r[1] + 0.045, 0.74, r[1] + 0.06), STEEL_DARK, tint=False)
        elif module == "Fridge":
            for gx, side in ((0.0, "west"), (1.0, "east")):         # one door: gaps only between units
                if side in joined:
                    cv.rect((max(r[0], gx - 0.008), r[1], min(r[2], gx + 0.008), r[3]), WALL_DARK)
            cv.rect((0.58, r[1] + 0.05, 0.60 + 0.005, r[3] - 0.05), STEEL_DARK, tint=False)   # handle by the door edge
            cv.ellipse((0.12, r[1] + 0.04, 0.16, r[1] + 0.08), COLD, tint=False)              # powered light
    if f:
        cv.rect((f[0] + 0.015, f[1], f[2] - 0.015, f[3]), TOP)
        gaps_y(cv, f, joined, WALL)
        if module == "Oven":
            cv.rect((f[0] + 0.01, 0.22, f[2] - 0.01, 0.78), STEEL, tint=False)
            cv.rect((f[0] + 0.03, 0.30, f[2] - 0.03, 0.70), BURNER, tint=False)
        elif module == "Fridge":
            hx = f[2] - 0.03 if facing == "east" else f[0] + 0.03
            cv.rect((hx - 0.012, 0.56, hx + 0.012, 0.80), STEEL_DARK, tint=False)
        else:
            hx = f[2] - 0.03 if facing == "east" else f[0] + 0.03
            for hy in (0.42, 0.58):
                cv.rect((hx - 0.012, hy - 0.05, hx + 0.012, hy + 0.05), STEEL_DARK, tint=False)
    cv.silhouette(open_sides, corner=CORNER)
    cv.save(kitchen_path(module, facing, cw, ccw, back=back), kitchen_path(module, facing, cw, ccw, True, back))


def draw_wallcab(facing, cw, ccw, back=False):
    """Wall cabinets hanging over the back of a counter, as an overlay. Only the
    cabinets are drawn; the rest is transparent so the counter shows through, with
    a soft shadow cast down onto the worktop."""
    joined = joined_sides(facing, cw, ccw) | ({OPP[facing]} if back else set())
    open_sides = set(SIDES) - joined
    cv = Canvas()
    x0 = 0.0 if "west" in joined else 0.02
    x1 = 1.0 if "east" in joined else 0.98
    y0 = 0.0 if "north" in joined else 0.02
    y1 = 1.0 if "south" in joined else 0.98
    # Seen from above in every facing: the cabinets' tops, a band over the back of
    # the cell, with the doors' top edge along its front.
    if facing in ("south", "north"):
        band = (x0, 0.0, x1, 0.30) if facing == "south" else (x0, 0.70, x1, 1.0)
        cv.rect(band, TOP)
        cv.rect((band[0], band[1], band[2], band[1] + 0.03), TOP_LIT)
        fy = (0.24, 0.30) if facing == "south" else (0.70, 0.76)   # doors, edge-on
        cv.rect((x0, fy[0], x1, fy[1]), WALL)
        for gx, side in ((0.0, "west"), (0.5, None), (1.0, "east")):
            if side is None or side in joined:
                cv.rect((max(x0, gx - 0.008), fy[0], min(x1, gx + 0.008), fy[1]), SEAM)
    else:
        right = facing == "east"
        band = (0.0, y0, 0.30, y1) if right else (0.70, y0, 1.0, y1)
        cv.rect(band, TOP)                                          # the cabinet tops
        if "north" not in joined:
            cv.rect((band[0], y0, band[2], y0 + 0.03), TOP_LIT)
        fx = (0.24, 0.30) if right else (0.70, 0.76)                # doors, edge-on
        cv.rect((fx[0], y0, fx[1], y1), WALL)
        for gy, side in ((0.0, "north"), (0.5, None), (1.0, "south")):
            if side is None or side in joined:
                cv.rect((fx[0], max(y0, gy - 0.008), fx[1], min(y1, gy + 0.008)), SEAM)
    # Which screen sides of the overlay are the cabinet's own open ends: the
    # silhouette is the band's outline, not the cell's.
    cv.silhouette(open_sides, corner=0.012)
    # Soft shadow onto the counter below the cabinets (translucent, so not outlined).
    sh = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    if facing == "south":
        sd.rectangle([px(band[0]), px(0.30), px(band[2]) - 1, px(0.37)], fill=(0, 0, 0, 70))
    elif facing == "north":
        sd.rectangle([px(band[0]), px(0.63), px(band[2]) - 1, px(0.70)], fill=(0, 0, 0, 70))
    elif facing in ("east", "west"):
        sx0, sx1 = (0.30, 0.36) if facing == "east" else (0.64, 0.70)
        sd.rectangle([px(sx0), px(y0), px(sx1) - 1, px(y1) - 1], fill=(0, 0, 0, 70))
    under = cv.img.copy()
    cv.img = Image.alpha_composite(sh, under)
    cv.save(kitchen_path("WallCab", facing, cw, ccw, back=back), kitchen_path("WallCab", facing, cw, ccw, True, back))


def draw_all():
    import shutil
    from draw_kitchen import KITCHEN_DIR
    for f in SIDES:
        for cw in "oj":
            for ccw in "oj":
                for back in (False, True):
                    for m in TALL:
                        draw_tall(m, f, cw, ccw, back)
                    draw_wallcab(f, cw, ccw, back)
        for m in TALL:
            shutil.copy(kitchen_path(m, f, "o", "o"), f"{KITCHEN_DIR}/Slopkea_{m}_{f}.png")
            shutil.copy(kitchen_path(m, f, "o", "o", True), f"{KITCHEN_DIR}/Slopkea_{m}_{f}m.png")
