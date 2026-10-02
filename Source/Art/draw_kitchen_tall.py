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


def draw_tall(module, facing, cw, ccw, back=False):
    joined = joined_sides(facing, cw, ccw) | ({OPP[facing]} if back else set())
    open_sides = set(SIDES) - joined
    cv = Canvas()
    ow = lambda side: 0.0 if side in joined else 0.03
    if facing in ("south", "north"):
        x0, x1 = ow("west"), 1 - ow("east")
        cv.rect((x0, 0.0, x1, 1.0 if (back and facing == "north") else 0.97), WALL)   # carcass
        cv.rect((x0, 0.0, x1, 0.06), TOP_LIT)                      # top
        cv.rect((x0, 0.06, x1, 0.075), SEAM)
        cv.rect((x0, 0.92, x1, 0.97), WALL_DARK)                   # plinth
        if facing == "north":
            cv.rect((x0, 0.075, x1, 0.92), TOP)                    # plain back
            cv.rect((x0, 0.5, x1, 0.51), SEAM)
        elif module == "Hutch":
            # Open shelving over a counter: plates on the shelves, doors below.
            cv.rect((x0 + 0.04, 0.10, x1 - 0.04, 0.46), SHELF_BACK)
            for sy in (0.10, 0.28):
                cv.rect((x0 + 0.04, sy, x1 - 0.04, sy + 0.03), (140, 140, 140))   # under the shelf above
                cv.rect((x0 + 0.04, sy + 0.15, x1 - 0.04, sy + 0.18), WALL)       # shelf lip
                for k, cx in enumerate((0.3, 0.5, 0.7)):
                    r = 0.075
                    cy = sy + 0.09
                    cv.ellipse((cx - r, cy - r * 0.9, cx + r, cy + r * 0.9), PLATE_RIM, tint=False)
                    cv.ellipse((cx - r * 0.7, cy - r * 0.62, cx + r * 0.7, cy + r * 0.62), PLATE, tint=False)
            cv.rect((0, 0.47, 1, 0.55), STONE, tint=False)         # the worktop between
            cv.rect((0, 0.47, 1, 0.49), STONE_LIT, tint=False)
            cv.rect((0, 0.53, 1, 0.55), STONE_EDGE, tint=False)
            doors(cv, x0, x1, 0.56, 0.91)
        elif module == "Oven":
            doors(cv, x0, x1, 0.085, 0.27)                         # cupboard over
            # The oven: a steel fascia, a dark glass door, a bar handle.
            cv.rect((x0 + 0.04, 0.29, x1 - 0.04, 0.66), STEEL, tint=False)
            cv.rect((x0 + 0.04, 0.29, x1 - 0.04, 0.31), STEEL_LIT, tint=False)
            for kx in (0.32, 0.44, 0.56, 0.68):                     # control strip
                cv.ellipse((kx - 0.015, 0.325, kx + 0.015, 0.355), STEEL_DARK, tint=False)
            cv.rect((x0 + 0.1, 0.40, x1 - 0.1, 0.62), BURNER, tint=False)        # window
            cv.rect((x0 + 0.12, 0.42, x1 - 0.12, 0.45), (70, 70, 74), tint=False)
            cv.rect((x0 + 0.14, 0.375, x1 - 0.14, 0.39), STEEL_LIT, tint=False)  # handle
            doors(cv, x0, x1, 0.68, 0.91, n=1)                     # drawer under
            cv.rect((0.42, 0.72, 0.58, 0.735), STEEL_DARK, tint=False)
        elif module == "Fridge":
            # Panel-fronted, built in: a tall fridge door over a freezer drawer.
            doors(cv, x0, x1, 0.085, 0.62, n=1, handle=None)
            doors(cv, x0, x1, 0.64, 0.91, n=1, handle=None)
            cv.rect((x1 - 0.12, 0.30, x1 - 0.095, 0.56), STEEL_DARK, tint=False)  # long handles
            cv.rect((0.40, 0.68, 0.60, 0.695), STEEL_DARK, tint=False)
            cv.ellipse((x0 + 0.08, 0.12, x0 + 0.11, 0.15), COLD, tint=False)      # powered light
    else:
        right = facing == "east"
        y0, y1 = (0.0 if "north" in joined else 0.03), (1.0 if "south" in joined else 0.94)
        bx0 = 0.0 if (back and right) else 0.03
        bx1 = 1.0 if (back and not right) else 0.97
        cv.rect((bx0, y0, bx1, y1), TOP)                           # the top, looking down
        if "north" not in joined:
            cv.rect((0.03, y0, 0.97, y0 + 0.03), TOP_LIT)
        if "south" not in joined:
            cv.rect((0.03, y1 - 0.06, 0.97, y1), WALL)
        fx = (0.80, 0.97) if right else (0.03, 0.20)               # the front, edge-on
        cv.rect((fx[0], y0, fx[1], y1), WALL)
        face = {"Oven": STEEL, "Fridge": None, "Hutch": None}[module]
        if face:
            cv.rect((fx[0] + 0.01, 0.30, fx[1] - 0.01, 0.62), face, tint=False)
        if module == "Hutch":
            cv.rect((fx[0], y0, fx[1], y1), SHELF_BACK)
            for k in range(3):
                py = 0.2 + k * 0.27
                cv.ellipse((fx[0] + 0.02, py, fx[1] - 0.02, py + 0.12), PLATE, tint=False)
        if module == "Fridge":
            hx = fx[1] - 0.03 if right else fx[0] + 0.03
            cv.rect((hx - 0.01, 0.25, hx + 0.01, 0.6), STEEL_DARK, tint=False)
    cv.silhouette(open_sides)
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
    if facing == "south":
        band = (x0, 0.0, x1, 0.30)                                  # back of the cell is the top
        cv.rect(band, WALL)
        cv.rect((x0, 0.0, x1, 0.035), TOP_LIT)
        doors(cv, x0, x1, 0.04, 0.29)
    elif facing == "north":
        band = (x0, 0.72, x1, 1.0)                                  # seen from behind
        cv.rect(band, WALL)
        cv.rect((x0, 0.72, x1, 0.75), TOP_LIT)
        cv.rect((x0, 0.86, x1, 0.87), SEAM)
    else:
        right = facing == "east"
        band = (0.0, y0, 0.30, y1) if right else (0.70, y0, 1.0, y1)
        cv.rect(band, TOP)                                          # the cabinet tops
        if "north" not in joined:
            cv.rect((band[0], y0, band[2], y0 + 0.03), TOP_LIT)
        fx = (0.24, 0.30) if right else (0.70, 0.76)                # doors, edge-on
        cv.rect((fx[0], y0, fx[1], y1), WALL)
        cv.rect((fx[0], 0.495, fx[1], 0.505), SEAM)
    # Which screen sides of the overlay are the cabinet's own open ends: the
    # silhouette is the band's outline, not the cell's.
    cv.silhouette(open_sides)
    # Soft shadow onto the counter below the cabinets (translucent, so not outlined).
    sh = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    if facing == "south":
        sd.rectangle([px(band[0]), px(0.30), px(band[2]) - 1, px(0.37)], fill=(0, 0, 0, 70))
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
