"""The second wave of joining furniture: desk, rug and cube shelving.

Same scheme as the table and sectional: every per-cell variant is drawn, and the
C# prints the one its neighbours call for. verify_art.py checks the two agree.
"""
from PIL import Image

from slopkea_draw import (SS, FOOT, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, Canvas)

ROOT = "Textures/Things/Building/Furniture/Slopkea"
DESK_DIR = ROOT + "/Desk"
RUG_DIR = ROOT + "/Rug"
SHELF_DIR = ROOT + "/Shelf"

SIDES = ("north", "east", "south", "west")
BITS = {"north": 1, "east": 2, "south": 4, "west": 8}
# Rug inside corners: bit set = both sides are joined but the diagonal cell is not,
# so the border has to turn the corner inside this cell.
CORNERS = {"ne": ("north", "east", 1), "se": ("south", "east", 2),
           "sw": ("south", "west", 4), "nw": ("north", "west", 8)}


def desk_path(i, mask=False):
    return f"{DESK_DIR}/Slopkea_Desk_{i}{'_m' if mask else ''}.png"


def rug_path(i, c):
    return f"{RUG_DIR}/Slopkea_Rug_{i}_{c}.png"


def shelf_path(facing, cw, ccw, mask=False):
    return f"{SHELF_DIR}/Slopkea_Shelf_{facing}_{cw}{ccw}{'_m' if mask else ''}.png"


def rug_variants():
    """Every (sides, corners) pair that can occur: a corner needs both its sides joined."""
    for i in range(16):
        for c in range(16):
            if all(not c & b or (i & BITS[s1] and i & BITS[s2]) for s1, s2, b in CORNERS.values()):
                yield i, c


# --- Desk ---------------------------------------------------------------------------

DESK_TOP_END = 0.78   # a slimmer top than the table's: it's a laminate slab, not planks
DESK_EDGE_END = 0.84


def draw_desk(i):
    """A LINNMON-style desk: a smooth slab, a light edge band all round the outside
    of the shape, and slim steel legs at outside corners only (untinted)."""
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    south_open = "south" in open_sides
    top_end = DESK_TOP_END if south_open else 1.0
    cv.rect((0, 0, 1, top_end), TOP)
    # Edge banding: a lit strip along every open edge of the top.
    band = 0.025
    if "north" in open_sides:
        cv.rect((0, 0, 1, band), TOP_LIT)
    if "west" in open_sides:
        cv.rect((0, 0, band, top_end), TOP_LIT)
    if "east" in open_sides:
        cv.rect((1 - band, 0, 1, top_end), SEAM)
    if south_open:
        cv.rect((0, top_end, 1, DESK_EDGE_END), WALL)
        for side, x0 in (("west", 0.05), ("east", 0.86)):
            if side in open_sides:
                cv.rect((x0, DESK_EDGE_END, x0 + 0.09, 1.0), FOOT, tint=False)
    cv.silhouette(open_sides)
    cv.save(desk_path(i), desk_path(i, mask=True))


# --- Rug ----------------------------------------------------------------------------

RUG_BORDER = 0.13
FIELD = (200, 200, 200)
MOTIF = (248, 248, 248)
BORDER = (150, 150, 150)
BORDER_LINE = (240, 240, 240)


def draw_rug(i, c):
    """A flat rug. The field and its diamond motif fill the cell; the border runs
    along open sides and turns every inside corner, so any dragged shape gets one
    continuous border. Flat, so no wall - just a thin silhouette."""
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    cv.rect((0, 0, 1, 1), FIELD)
    cv.poly([(0.5, 0.27), (0.73, 0.5), (0.5, 0.73), (0.27, 0.5)], MOTIF)
    cv.poly([(0.5, 0.39), (0.61, 0.5), (0.5, 0.61), (0.39, 0.5)], FIELD)
    b, ln = RUG_BORDER, 0.012
    edge = {"north": (0, 0, 1, b), "south": (0, 1 - b, 1, 1),
            "west": (0, 0, b, 1), "east": (1 - b, 0, 1, 1)}
    inner = {"north": (0, b - ln, 1, b), "south": (0, 1 - b, 1, 1 - b + ln),
             "west": (b - ln, 0, b, 1), "east": (1 - b, 0, 1 - b + ln, 1)}
    for s in open_sides:
        cv.rect(edge[s], BORDER)
    for name, (s1, s2, bit) in CORNERS.items():
        if c & bit:
            x0 = 1 - b if "east" in (s1, s2) else 0
            y0 = 1 - b if "south" in (s1, s2) else 0
            cv.rect((x0, y0, x0 + b, y0 + b), BORDER)
    # The inner line: along open sides, clipped where a perpendicular border meets it.
    for s in open_sides:
        x0, y0, x1, y1 = inner[s]
        if s in ("north", "south"):
            x0 = b - ln if "west" in open_sides else 0
            x1 = 1 - b + ln if "east" in open_sides else 1
        else:
            y0 = b - ln if "north" in open_sides else 0
            y1 = 1 - b + ln if "south" in open_sides else 1
        cv.rect((x0, y0, x1, y1), BORDER_LINE)
    for name, (s1, s2, bit) in CORNERS.items():
        if c & bit:
            cx = 1 - b if "east" in (s1, s2) else b - ln
            cy = 1 - b if "south" in (s1, s2) else b - ln
            ex = 1 if "east" in (s1, s2) else 0
            ey = 1 if "south" in (s1, s2) else 0
            cv.rect((min(cx, ex), cy, max(cx + ln, ex), cy + ln), BORDER_LINE)
            cv.rect((cx, min(cy, ey), cx + ln, max(cy + ln, ey)), BORDER_LINE)
    cv.silhouette(open_sides, ring=4 * SS)
    cv.save(rug_path(i, c))


# --- Cube shelving ------------------------------------------------------------------

CUBBY = (124, 124, 124)        # the inside of a cube: dark, but still stuff-tinted
CUBBY_TOP = (100, 100, 100)    # the shadow under the shelf above


def draw_shelf(facing, cw, ccw):
    """KALLAX-style cube unit, one column of two cubes per cell, drawn as a view.

    Joins only to a neighbour facing the same way, on its cw/ccw sides; a joined
    side has no outer wall, so a run reads as one unit with shared walls.
    """
    cw_s = {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]
    ccw_s = {"north": "west", "east": "north", "south": "east", "west": "south"}[facing]
    screen = {cw_s: cw, ccw_s: ccw}
    joined = {s for s, st in screen.items() if st == "j"}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    wall_open, wall_joined = 0.07, 0.035   # a shared wall is half of each cell's

    def w(side):
        return wall_joined if side in joined else wall_open

    if facing in ("south", "north"):
        top = 0.12
        cv.rect((0, 0.02, 1, 0.98), TOP)                       # carcass
        cv.rect((0, 0.02, 1, top), TOP_LIT)                    # top face
        cv.rect((0, top - 0.008, 1, top), SEAM)
        if facing == "south":
            x0, x1 = w("west"), 1 - w("east")
            for y0, y1 in ((top + 0.06, 0.53), (0.59, 0.94)):
                cv.rect((x0, y0, x1, y1), CUBBY)
                cv.rect((x0, y0, x1, y0 + 0.06), CUBBY_TOP)
        else:
            cv.rect((0, 0.555, 1, 0.565), SEAM)                # back panel: the shelf line shows through
            cv.rect((0, 0.94, 1, 0.98), WALL)
    else:
        # Side views: we look down on the top and see the open front edge-on.
        right = facing == "east"
        # A joined end runs to the cell edge, so a column of units is one top.
        ty0 = 0.0 if "north" in joined else 0.10
        ty1 = 1.0 if "south" in joined else 0.90
        cv.rect((0, ty0, 1, ty1), TOP)                         # top face
        if "north" not in joined:
            cv.rect((0, ty0, 1, ty0 + 0.03), TOP_LIT)
        if "south" not in joined:
            cv.rect((0, ty1 - 0.06, 1, ty1), WALL)             # end panel's wall
        # The open front, edge-on: two cube openings per cell, split by the shelf.
        fx0, fx1 = (0.80, 0.97) if right else (0.03, 0.20)
        ya, yb = ty0 + w("north"), ty1 - w("south") - (0.06 if "south" not in joined else 0)
        mid = (ya + yb) / 2
        cv.rect((fx0, ya, fx1, mid - 0.02), CUBBY)
        cv.rect((fx0, mid + 0.02, fx1, yb), CUBBY)
    cv.silhouette(open_sides)
    cv.save(shelf_path(facing, cw, ccw), shelf_path(facing, cw, ccw, mask=True))


def draw_all():
    import os
    import shutil
    for d in (DESK_DIR, RUG_DIR, SHELF_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for i in range(16):
        draw_desk(i)
    n = 0
    for i, c in rug_variants():
        draw_rug(i, c)
        n += 1
    for f in SIDES:
        for cw in "oj":
            for ccw in "oj":
                draw_shelf(f, cw, ccw)
        # Def graphic (blueprint, minified, ghost): the free-standing unit.
        shutil.copy(shelf_path(f, "o", "o"), f"{SHELF_DIR}/Slopkea_Shelf_{f}.png")
        shutil.copy(shelf_path(f, "o", "o", True), f"{SHELF_DIR}/Slopkea_Shelf_{f}m.png")
    return n
