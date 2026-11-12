"""Kitchen run modules (cabinet, sink, hob) and the bookcase.

Both join along their sides with neighbours facing the same way, like the cube
shelving: `<facing>_<cw><ccw>`, each side o (open) or j (joined). The kitchen
modules all join each other, so a run can mix them freely.
"""
import os
import shutil

from slopkea_draw import SEAM, TOP, TOP_LIT, WALL, WALL_DARK, Canvas

ROOT = "Textures/Things/Building/Furniture/Slopkea"
KITCHEN_DIR = ROOT + "/Kitchen"
BOOK_DIR = ROOT + "/Bookcase"
MODULES = ("Cabinet", "Sink", "Hob")
SIDES = ("north", "east", "south", "west")
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}

# Fixed colours: the worktop is pale stone, the fittings steel, and they never
# take the stuff colour (black in the mask). The stuff is the cabinet carcass.
STONE_LIT, STONE, STONE_EDGE = (236, 234, 228), (218, 215, 208), (176, 172, 164)
STEEL_LIT, STEEL, STEEL_DARK = (214, 220, 226), (172, 180, 188), (104, 110, 118)
BURNER, BURNER_RING = (40, 40, 42), (84, 84, 88)


def kitchen_path(module, facing, cw, ccw, mask=False, back=False):
    """`back`: the module's back is against a wall, so it runs flush to it ("b")."""
    return f"{KITCHEN_DIR}/Slopkea_{module}_{facing}_{cw}{ccw}{'b' if back else ''}{'_m' if mask else ''}.png"


OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def book_path(facing, cw, ccw, mask=False):
    """Named <cw><ccw>_<facing>, unlike the rest: the bookcase keeps the vanilla
    Building_Bookcase and swaps its Graphic for a Graphic_Multi per join state, and
    Graphic_Multi appends _<facing> (and "m", no underscore, for the mask)."""
    return f"{BOOK_DIR}/Slopkea_Bookcase_{cw}{ccw}_{facing}{'m' if mask else ''}.png"


BOOKEND_EAST = BOOK_DIR + "/Slopkea_BookendEast.png"
BOOKEND_NORTH = BOOK_DIR + "/Slopkea_BookendNorth.png"


def joined_sides(facing, cw, ccw):
    return {s for s, st in ((CW[facing], cw), (CCW[facing], ccw)) if st == "j"}


# Layout, in cells, measured off vanilla's electric stove (TableStoveElectric):
# the bench is seen from above in every facing, its top about 0.9 of a cell deep,
# and what shows of its height is one dark strip about 0.13 of a cell tall along
# the SCREEN-BOTTOM edge - the south face, whichever way the bench faces.
EDGE = 0.03          # margin at an open side, for the silhouette ring
STRIP = 0.135        # the carcass strip under the worktop, at an open south side
FRONT = 0.07         # the door edge that shows along the front in the side views
BURNER_RINGS = ((1.0, (58, 58, 62)), (0.80, (96, 92, 94)), (0.62, (62, 62, 66)),
                (0.44, (100, 96, 98)), (0.26, (62, 62, 66)), (0.10, (104, 100, 102)))
PLATE, PLATE_EDGE = (108, 110, 114), (86, 88, 92)


def _toward(side, box, depth):
    """The band `depth` deep along the `side` edge of box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    return {"north": (x0, y0, x1, y0 + depth), "south": (x0, y1 - depth, x1, y1),
            "west": (x0, y0, x0 + depth, y1), "east": (x1 - depth, y0, x1, y1)}[side]


def fitting(cv, module, top, facing):
    """What is let into the worktop `top` (x0, y0, x1, y1). It is seen from above
    in every facing, so it is never squashed: only its front and back swap ends."""
    tx0, ty0, tx1, ty1 = top
    cx, cy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
    if module == "Hob":
        # A steel plate with four burners, each about 0.36 of a cell across as on
        # the vanilla stove, and the controls in a band along the plate's front.
        hw, hh = 0.37, 0.37
        hh = min(hh, (ty1 - ty0) / 2 - 0.06)
        hw = min(hw, (tx1 - tx0) / 2 - 0.06)
        plate = (cx - hw, cy - hh, cx + hw, cy + hh)
        cv.rect(plate, PLATE_EDGE, tint=False)
        cv.rect((plate[0] + 0.012, plate[1] + 0.012, plate[2] - 0.012, plate[3] - 0.012), PLATE, tint=False)
        band = 0.085
        ctrl = _toward(facing, plate, band)
        cv.rect(ctrl, PLATE_EDGE, tint=False)
        horiz = facing in ("north", "south")
        for t in (0.14, 0.26, 0.74, 0.86):                       # two knobs each side of a slot
            kx = ctrl[0] + t * (ctrl[2] - ctrl[0]) if horiz else (ctrl[0] + ctrl[2]) / 2
            ky = (ctrl[1] + ctrl[3]) / 2 if horiz else ctrl[1] + t * (ctrl[3] - ctrl[1])
            cv.ellipse((kx - 0.022, ky - 0.022, kx + 0.022, ky + 0.022), BURNER, tint=False)
        if horiz:
            cv.rect((cx - 0.13, (ctrl[1] + ctrl[3]) / 2 - 0.012, cx + 0.13, (ctrl[1] + ctrl[3]) / 2 + 0.012),
                    STEEL, tint=False)
        else:
            cv.rect(((ctrl[0] + ctrl[2]) / 2 - 0.012, cy - 0.13, (ctrl[0] + ctrl[2]) / 2 + 0.012, cy + 0.13),
                    STEEL, tint=False)
        # The burners fill what is left of the plate.
        bx0, by0, bx1, by1 = plate
        if facing == "south": by1 -= band
        elif facing == "north": by0 += band
        elif facing == "east": bx1 -= band
        else: bx0 += band
        r = min((bx1 - bx0), (by1 - by0)) / 4 - 0.012
        for fx in (0.25, 0.75):
            for fy in (0.25, 0.75):
                x, y = bx0 + fx * (bx1 - bx0), by0 + fy * (by1 - by0)
                for k, col in BURNER_RINGS:
                    cv.ellipse((x - r * k, y - r * k, x + r * k, y + r * k), col, tint=False)
    elif module == "Sink":
        # A steel basin let into the top, the tap at the back.
        horiz = facing in ("north", "south")
        hw, hh = (0.33, 0.25) if horiz else (0.25, 0.33)
        back = OPP[facing]
        shift = {"north": (0, -0.03), "south": (0, 0.03), "east": (0.03, 0), "west": (-0.03, 0)}[facing]
        cx, cy = cx + shift[0], cy + shift[1]                     # basin sits towards the front
        rim = (cx - hw, cy - hh, cx + hw, cy + hh)
        cv.rect(rim, STEEL_LIT, tint=False)
        bowl = (rim[0] + 0.035, rim[1] + 0.035, rim[2] - 0.035, rim[3] - 0.035)
        cv.rect(bowl, STEEL, tint=False)
        cv.rect((bowl[0], bowl[1], bowl[2], bowl[1] + 0.045), STEEL_DARK, tint=False)   # shade under the far rim
        cv.rect((bowl[0], bowl[1], bowl[0] + 0.03, bowl[3]), STEEL_DARK, tint=False)
        cv.ellipse((cx - 0.035, cy - 0.035, cx + 0.035, cy + 0.035), STEEL_DARK, tint=False)   # drain
        # Tap: a base on the worktop behind the basin, the spout reaching over it.
        bx, by = {"north": (cx, rim[1] - 0.045), "south": (cx, rim[3] + 0.045),
                  "west": (rim[0] - 0.045, cy), "east": (rim[2] + 0.045, cy)}[back]
        cv.line([(bx, by), (cx + (bx - cx) * 0.45, cy + (by - cy) * 0.45)], 0.05, STEEL_DARK, tint=False)
        cv.line([(bx, by), (cx + (bx - cx) * 0.45, cy + (by - cy) * 0.45)], 0.03, STEEL_LIT, tint=False)
        cv.ellipse((bx - 0.04, by - 0.04, bx + 0.04, by + 0.04), STEEL_DARK, tint=False)
        cv.ellipse((bx - 0.027, by - 0.027, bx + 0.027, by + 0.027), STEEL_LIT, tint=False)


def draw_kitchen(module, facing, cw, ccw, back=False):
    """One counter module, seen from above like vanilla's benches: the worktop
    covers the cell in every facing, and the carcass - the stuff - shows as one
    strip under it along the screen-bottom edge, plus the doors' top edge along
    the front in the side views. Nothing is drawn on a cell boundary, so a run
    reads as one counter."""
    joined = joined_sides(facing, cw, ccw)
    if back:
        joined = joined | {OPP[facing]}     # flush to the wall behind: no lip, no outline
    open_sides = set(SIDES) - joined
    cv = Canvas()
    x0 = 0.0 if "west" in joined else EDGE
    x1 = 1.0 if "east" in joined else 1 - EDGE
    y0 = 0.0 if "north" in joined else EDGE
    y1 = 1.0 if "south" in joined else 1 - EDGE
    top_y1 = y1 if "south" in joined else y1 - STRIP
    # Carcass first: the strip under the worktop, and the door edge along the front.
    if "south" not in joined:
        cv.rect((x0, top_y1, x1, y1), WALL)
        cv.rect((x0, top_y1, x1, top_y1 + 0.02), WALL_DARK)      # in the worktop's shadow
        if facing == "south":
            # Door gaps every half cell, the same on a cell boundary as inside one.
            for gx, half in ((0.0, "west"), (0.5, None), (1.0, "east")):
                if half is None or half in joined:
                    cv.rect((gx - 0.008, top_y1 + 0.02, gx + 0.008, y1), WALL_DARK)
    tx0, tx1 = x0, x1
    if facing in ("east", "west") and facing not in joined:
        f = (x1 - FRONT, y0, x1, top_y1) if facing == "east" else (x0, y0, x0 + FRONT, top_y1)
        cv.rect(f, TOP)
        for gy, half in ((0.0, "north"), (0.5, None), (1.0, "south")):
            if half is None or half in joined:
                cv.rect((f[0], gy - 0.008, f[2], gy + 0.008), WALL)
        if facing == "east":
            tx1 = x1 - FRONT
        else:
            tx0 = x0 + FRONT
    # Worktop.
    top = (tx0, y0, tx1, top_y1)
    cv.rect(top, STONE, tint=False)
    if "north" not in joined:
        cv.rect((tx0, y0, tx1, y0 + 0.022), STONE_LIT, tint=False)
    if "south" not in joined:
        cv.rect((tx0, top_y1 - 0.022, tx1, top_y1), STONE_EDGE, tint=False)   # the front lip
    if facing in ("east", "west") and facing not in joined:
        lip = (tx1 - 0.022, y0, tx1, top_y1) if facing == "east" else (tx0, y0, tx0 + 0.022, top_y1)
        cv.rect(lip, STONE_EDGE, tint=False)
    fitting(cv, module, top, facing)
    cv.silhouette(open_sides, corner=0.012)
    cv.save(kitchen_path(module, facing, cw, ccw, back=back), kitchen_path(module, facing, cw, ccw, True, back))


BOOK_FRAME, BOOK_FLOOR, BOOK_RECESS, BOOK_LIP, BOOK_FACE = (204,) * 3, (250,) * 3, (112,) * 3, (228,) * 3, (128,) * 3


def draw_bookcase(facing, cw, ccw):
    """A bookcase, drawn EMPTY and laid out like vanilla's own one-cell bookcase
    (BookcaseSmall): seen from above and a little from the front, a frame round a
    pale shelf floor, the shadowed recess under the top at the back, and the
    case's face as a strip along the screen-bottom edge. Vanilla's bookcase code
    draws the stored books over it, so the floor sits where vanilla's does."""
    from slopkea_units import CORNER, EDGE
    joined = joined_sides(facing, cw, ccw)
    open_sides = set(SIDES) - joined
    cv = Canvas()
    x0 = 0.0 if "west" in joined else EDGE
    x1 = 1.0 if "east" in joined else 1 - EDGE
    y0 = 0.0 if "north" in joined else EDGE
    y1 = 1.0 if "south" in joined else 1 - EDGE
    w = lambda side: 0.035 if side in joined else 0.08       # a shared wall is half of each cell's
    cv.rect((x0, y0, x1, y1), BOOK_FRAME)
    if "north" not in joined:
        cv.rect((x0, y0, x1, y0 + 0.022), TOP_LIT)
    strip = 0.0
    if "south" not in joined:
        strip = 0.15 if facing == "south" else 0.20
        cv.rect((x0, y1 - strip, x1, y1), BOOK_FACE)
    ix0, ix1 = x0 + w("west"), x1 - w("east")
    if facing == "south":
        # Looking into the open front: recess at the back, floor, lit front lip.
        cv.rect((ix0, y0 + 0.08, ix1, 0.31), BOOK_RECESS)
        cv.rect((ix0, 0.31, ix1, y1 - strip - 0.07), BOOK_FLOOR)
        cv.rect((ix0, y1 - strip - 0.07, ix1, y1 - strip), BOOK_LIP)
    elif facing == "north":
        # From behind: the floor runs to the back edge, the frame closes the front.
        cv.rect((ix0, y0 + 0.03, ix1, y0 + 0.09), BOOK_LIP)
        cv.rect((ix0, y0 + 0.09, ix1, y1 - strip - 0.10), BOOK_FLOOR)
    else:
        right = facing == "east"
        iy0 = y0 + (0.0 if "north" in joined else 0.12)
        iy1 = y1 - strip - (0.0 if "south" in joined else 0.12)
        fx0, fx1 = (x0 + 0.12, x1) if right else (x0, x1 - 0.12)      # open on the front side
        if "north" not in joined:
            cv.rect((fx0, iy0, fx1, iy0 + 0.07), BOOK_RECESS)
            iy0 += 0.07
        cv.rect((fx0, iy0, fx1, iy1), BOOK_FLOOR)
        lip = (fx1 - 0.07, iy0, fx1, iy1) if right else (fx0, iy0, fx0 + 0.07, iy1)
        cv.rect(lip, BOOK_LIP)
    cv.silhouette(open_sides, corner=CORNER)
    cv.save(book_path(facing, cw, ccw), book_path(facing, cw, ccw, True))


def draw_bookends():
    """The small steel bookends vanilla's bookcase stands at the end of a row."""
    for path, (w, h) in ((BOOKEND_EAST, (0.5, 0.9)), (BOOKEND_NORTH, (0.9, 0.5))):
        cv = Canvas()
        x0, y0 = (1 - w) / 2, (1 - h) / 2
        cv.rect((x0, y0, x0 + w, y0 + h), STEEL, tint=False)
        cv.rect((x0, y0, x0 + w, y0 + min(w, h) * 0.2), STEEL_LIT, tint=False)
        cv.silhouette(set(SIDES), corner=0.012)
        cv.save(path)


def draw_all():
    for d in (KITCHEN_DIR, BOOK_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for f in SIDES:
        for cw in "oj":
            for ccw in "oj":
                for m in MODULES:
                    for back in (False, True):
                        draw_kitchen(m, f, cw, ccw, back)
                draw_bookcase(f, cw, ccw)
        # Def graphics (blueprint, minified, ghost): the free-standing unit.
        for m in MODULES:
            shutil.copy(kitchen_path(m, f, "o", "o"), f"{KITCHEN_DIR}/Slopkea_{m}_{f}.png")
            shutil.copy(kitchen_path(m, f, "o", "o", True), f"{KITCHEN_DIR}/Slopkea_{m}_{f}m.png")
        shutil.copy(book_path(f, "o", "o"), f"{BOOK_DIR}/Slopkea_Bookcase_{f}.png")
        shutil.copy(book_path(f, "o", "o", True), f"{BOOK_DIR}/Slopkea_Bookcase_{f}m.png")
    draw_bookends()
