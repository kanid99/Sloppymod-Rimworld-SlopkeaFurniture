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


# --- Inside corners of drag-to-shape pieces ------------------------------------------
# A cell whose two sides are joined but whose diagonal is empty sits at the inside
# corner of an L. The side bits alone cannot say so, so such cells get a second
# number: NE=1, SE=2, SW=4, NW=8 - the rug's scheme (Neighbors.InsideCornerBits).
SIDE_BITS = {"north": 1, "east": 2, "south": 4, "west": 8}
CORNER_BITS = {("north", "east"): 1, ("south", "east"): 2, ("south", "west"): 4, ("north", "west"): 8}


def corner_variants():
    """Every (sides, corners) pair with at least one inside corner: a corner needs
    both of its sides joined."""
    for i in range(16):
        for c in range(1, 16):
            if all(not c & b or (i & SIDE_BITS[ns] and i & SIDE_BITS[ew]) for (ns, ew), b in CORNER_BITS.items()):
                yield i, c


def corners_of(c):
    return [pair for pair, b in CORNER_BITS.items() if c & b]


def variant_name(i, c=0):
    """<sides>, or <sides>_<corners> when the cell has an inside corner. The plain
    names are the ones the pieces always had, so nothing is renamed."""
    return f"{i}_{c}" if c else f"{i}"


def inside_corner_outline(cv, corners, alpha_of):
    """Prepare cv's silhouette pass for inside corners. `alpha_of(i)` gives the
    finished silhouette of the plain variant with side bits i. Returns the
    `context` and `empty_diagonals` to hand to Canvas.silhouette: the ring is
    then measured against the two real neighbours, so it turns the corner inside
    this cell and runs straight into theirs. Where both neighbours stop short of
    their cell edges, this cell is cut back to where their edges cross."""
    from slopkea_draw import C, OPP
    corners = list(corners)
    context = {}
    for side in {s for pair in corners for s in pair}:
        # The neighbour beyond `side`: joined back to us, open towards any empty
        # diagonal it shares with us, and taken as joined everywhere else.
        joined = {side, OPP[side]}
        for perp in (("north", "south") if side in ("east", "west") else ("east", "west")):
            pair = (perp, side) if perp in ("north", "south") else (side, perp)
            if pair not in corners:
                joined.add(perp)
        context[side] = alpha_of(sum(SIDE_BITS[s] for s in joined))
    pad = int(0.2 * C)

    def gap(alpha, beyond, towards):
        """How far short of its `towards` edge the neighbour beyond `beyond`
        stops, measured in the strip of it that touches this cell."""
        strip = {"east": (0, 0, pad, C), "west": (C - pad, 0, C, C),
                 "south": (0, 0, C, pad), "north": (0, C - pad, C, C)}[beyond]
        box = alpha.crop(strip).getbbox()
        if box is None:
            return C
        x0, y0, x1, y1 = box
        size = {"north": y0, "west": x0, "south": (strip[3] - strip[1]) - y1, "east": (strip[2] - strip[0]) - x1}
        return size[towards]

    for ns, ew in corners:
        dy, dx = gap(context[ew], ew, ns), gap(context[ns], ns, ew)
        if dx > 0 and dy > 0:
            x = (C - dx, C - 1) if ew == "east" else (0, dx - 1)
            y = (C - dy, C - 1) if ns == "south" else (0, dy - 1)
            cv.d.rectangle([x[0], y[0], x[1], y[1]], fill=(0, 0, 0, 0))
            cv.md.rectangle([x[0], y[0], x[1], y[1]], fill=(0, 0, 0))
    return context, set(corners)
