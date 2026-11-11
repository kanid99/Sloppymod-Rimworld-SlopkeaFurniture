"""Storage and tall units, laid out the way vanilla draws its own.

Measured off vanilla's one-cell bookcase (BookcaseSmall) and its electric stove:
a unit is seen from above in EVERY facing. Its top covers the cell, and its height
shows as one strip along the screen-bottom edge - the face towards the camera,
whichever way the unit faces. So the front (doors, an oven, open shelves) is on
that strip only when the unit faces south; facing north the strip is its plain
back; facing east or west the front is seen edge-on, as a band down that side.
Corners are square, as vanilla's are.
"""
from slopkea_draw import TOP, TOP_LIT, WALL, WALL_DARK

EDGE = 0.03            # margin at an open side, for the silhouette ring
CORNER = 0.012         # outer corner radius, in cells: nearly square
GAP = 0.008            # half the width of a door gap


def unit_base(cv, facing, joined, strip_h, front_w=0.10, top=TOP, face=WALL):
    """Lay down the top and the camera-side strip. Returns the rects to detail:
    `top`, `strip` (None when the south side is joined) and `front` (the edge-on
    front band in an east/west view, None otherwise)."""
    x0 = 0.0 if "west" in joined else EDGE
    x1 = 1.0 if "east" in joined else 1 - EDGE
    y0 = 0.0 if "north" in joined else EDGE
    y1 = 1.0 if "south" in joined else 1 - EDGE
    has_strip = "south" not in joined
    ty1 = y1 - strip_h if has_strip else y1
    cv.rect((x0, y0, x1, ty1), top)
    if "north" not in joined:
        cv.rect((x0, y0, x1, y0 + 0.022), TOP_LIT)
    strip = None
    if has_strip:
        cv.rect((x0, ty1, x1, y1), face)
        cv.rect((x0, ty1, x1, ty1 + 0.018), WALL_DARK)        # in the top's shadow
        cv.rect((x0, y1 - 0.02, x1, y1), WALL_DARK)           # plinth
        strip = (x0, ty1 + 0.018, x1, y1 - 0.02)
    front = None
    if facing in ("east", "west") and facing not in joined:
        front = (x1 - front_w, y0, x1, ty1) if facing == "east" else (x0, y0, x0 + front_w, ty1)
        cv.rect(front, face)
    return {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ty1": ty1,
            "top": (x0, y0, x1, ty1), "strip": strip, "front": front}


def gaps_x(cv, r, joined, colour=WALL_DARK, tint=True):
    """Door gaps across a strip: every half cell, the same on a cell boundary
    (half a gap from each cell) as inside one."""
    for gx, side in ((0.0, "west"), (0.5, None), (1.0, "east")):
        if side is None or side in joined:
            cv.rect((max(r[0], gx - GAP), r[1], min(r[2], gx + GAP), r[3]), colour, tint)


def gaps_y(cv, r, joined, colour=WALL_DARK, tint=True):
    for gy, side in ((0.0, "north"), (0.5, None), (1.0, "south")):
        if side is None or side in joined:
            cv.rect((r[0], max(r[1], gy - GAP), r[2], min(r[3], gy + GAP)), colour, tint)
