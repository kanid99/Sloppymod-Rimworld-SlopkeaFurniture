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


def kitchen_path(module, facing, cw, ccw, mask=False):
    return f"{KITCHEN_DIR}/Slopkea_{module}_{facing}_{cw}{ccw}{'_m' if mask else ''}.png"


def book_path(facing, cw, ccw, mask=False):
    """Named <cw><ccw>_<facing>, unlike the rest: the bookcase keeps the vanilla
    Building_Bookcase and swaps its Graphic for a Graphic_Multi per join state, and
    Graphic_Multi appends _<facing> (and "m", no underscore, for the mask)."""
    return f"{BOOK_DIR}/Slopkea_Bookcase_{cw}{ccw}_{facing}{'m' if mask else ''}.png"


BOOKEND_EAST = BOOK_DIR + "/Slopkea_BookendEast.png"
BOOKEND_NORTH = BOOK_DIR + "/Slopkea_BookendNorth.png"


def joined_sides(facing, cw, ccw):
    return {s for s, st in ((CW[facing], cw), (CCW[facing], ccw)) if st == "j"}


def fitting(cv, module, cx, cy, sx, sy):
    """What sits on the worktop, centred at (cx, cy), sx/sy its half-extent in
    screen fractions (the side views squash it)."""
    if module == "Sink":
        cv.rect((cx - sx, cy - sy, cx + sx, cy + sy), STEEL_DARK, tint=False)
        cv.rect((cx - sx * 0.82, cy - sy * 0.75, cx + sx * 0.82, cy + sy * 0.8), STEEL, tint=False)
        cv.rect((cx - sx * 0.82, cy - sy * 0.75, cx + sx * 0.82, cy - sy * 0.55), STEEL_DARK, tint=False)
        cv.ellipse((cx - 0.02, cy - 0.02, cx + 0.02, cy + 0.02), STEEL_DARK, tint=False)  # drain
    elif module == "Hob":
        cv.rect((cx - sx, cy - sy, cx + sx, cy + sy), BURNER, tint=False)
        for dx in (-0.5, 0.5):
            for dy in (-0.5, 0.5):
                x, y = cx + dx * sx, cy + dy * sy
                r = min(sx, sy) * 0.36
                cv.ellipse((x - r * sx / min(sx, sy), y - r * sy / min(sx, sy),
                            x + r * sx / min(sx, sy), y + r * sy / min(sx, sy)), BURNER_RING, tint=False)


def draw_kitchen(module, facing, cw, ccw):
    joined = joined_sides(facing, cw, ccw)
    open_sides = set(SIDES) - joined
    cv = Canvas()
    ow = lambda side: 0.0 if side in joined else 0.03   # carcass inset on open ends

    if facing in ("south", "north"):
        x0, x1 = ow("west"), 1 - ow("east")
        top0, top1 = 0.04, (0.46 if facing == "south" else 0.62)
        # Worktop, with a lit front lip. It overhangs, so it runs edge to edge.
        cv.rect((0, top0, 1, top1), STONE, tint=False)
        cv.rect((0, top0, 1, top0 + 0.025), STONE_LIT, tint=False)
        cv.rect((0, top1 - 0.03, 1, top1), STONE_EDGE, tint=False)
        if facing == "south":
            # Cabinet front: two doors per cell with bar handles.
            cv.rect((x0, top1, x1, 0.96), WALL)                # carcass shows between doors
            cv.rect((x0, 0.90, x1, 0.96), WALL_DARK)           # recessed plinth
            for d0, d1 in ((max(x0, 0.02) + 0.015, 0.495), (0.505, min(x1, 0.98) - 0.015)):
                cv.rect((d0, top1 + 0.02, d1, 0.885), TOP)       # door
                cv.rect((d0, top1 + 0.02, d1, top1 + 0.035), TOP_LIT)
                cv.rect((d0 + 0.035, top1 + 0.08, d1 - 0.035, 0.84), SEAM)   # recessed panel
                cv.rect((d0 + 0.045, top1 + 0.09, d1 - 0.045, 0.83), TOP)
            for hx in (0.42, 0.58):
                cv.rect((hx - 0.012, top1 + 0.07, hx + 0.012, top1 + 0.2), STEEL_DARK, tint=False)
            if module == "Hob":
                for kx in (0.3, 0.42, 0.58, 0.7):                  # control knobs on the fascia
                    cv.ellipse((kx - 0.02, top1 + 0.012, kx + 0.02, top1 + 0.052), STEEL_DARK, tint=False)
            fitting(cv, module, 0.5, (top0 + top1) / 2 + 0.01, 0.30, 0.15)
        else:
            cv.rect((x0, top1, x1, 0.96), WALL)                  # the plain back
            cv.rect((x0, top1, x1, top1 + 0.02), WALL_DARK)
            fitting(cv, module, 0.5, (top0 + top1) / 2, 0.30, 0.2)
            if module == "Sink":                                  # the tap, at the back
                cv.rect((0.47, top1 - 0.09, 0.53, top1 - 0.02), STEEL_LIT, tint=False)
    else:
        right = facing == "east"
        y0, y1 = (0.0 if "north" in joined else 0.04), (1.0 if "south" in joined else 0.93)
        wt0, wt1 = (0.04, 0.80) if right else (0.20, 0.96)      # worktop across the depth
        cv.rect((wt0, y0, wt1, y1), STONE, tint=False)
        if "north" not in joined:
            cv.rect((wt0, y0, wt1, y0 + 0.025), STONE_LIT, tint=False)
        fx = (wt1, 0.97) if right else (0.03, wt0)              # cabinet front, edge-on
        cv.rect((fx[0], y0, fx[1], y1), WALL)
        for d0, d1 in ((y0 + 0.02, 0.495), (0.505, y1 - 0.02)):     # doors, edge-on
            cv.rect((fx[0] + 0.01, d0, fx[1] - 0.01, d1), TOP)
        lip = (wt1 - 0.03, wt1) if right else (wt0, wt0 + 0.03)
        cv.rect((lip[0], y0, lip[1], y1), STONE_EDGE, tint=False)
        if "south" not in joined:
            cv.rect((0, y1 - 0.05, 1, y1), WALL)                 # end panel's wall
        fitting(cv, module, (wt0 + wt1) / 2, 0.47, 0.17, 0.28)
        if module == "Hob":
            kx = (fx[0] + fx[1]) / 2
            for ky in (0.28, 0.4, 0.56, 0.68):
                cv.ellipse((kx - 0.018, ky - 0.018, kx + 0.018, ky + 0.018), STEEL_DARK, tint=False)
    cv.silhouette(open_sides)
    cv.save(kitchen_path(module, facing, cw, ccw), kitchen_path(module, facing, cw, ccw, True))


def draw_bookcase(facing, cw, ccw):
    """A BILLY-style bookcase, drawn EMPTY: the vanilla bookcase code fills the
    shelves with the books actually stored in it. Tall, three shelves, a view per
    facing."""
    joined = joined_sides(facing, cw, ccw)
    open_sides = set(SIDES) - joined
    cv = Canvas()
    w = lambda side: 0.03 if side in joined else 0.06
    if facing == "south":
        cv.rect((0, 0.02, 1, 0.98), TOP)
        cv.rect((0, 0.02, 1, 0.08), TOP_LIT)
        x0, x1 = w("west"), 1 - w("east")
        for y0, y1 in ((0.11, 0.37), (0.40, 0.66), (0.69, 0.94)):
            cv.rect((x0, y0, x1, y1), (150, 150, 150))           # the back panel, in shade
            cv.rect((x0, y0, x1, y0 + 0.035), (120, 120, 120))  # under the shelf above
            cv.rect((x0, y1 - 0.02, x1, y1), WALL)              # the shelf's lit front lip
    elif facing == "north":
        cv.rect((0, 0.02, 1, 0.98), TOP)
        cv.rect((0, 0.02, 1, 0.08), TOP_LIT)
        for y in (0.385, 0.675):
            cv.rect((0, y - 0.005, 1, y + 0.005), SEAM)
        cv.rect((0, 0.94, 1, 0.98), WALL)
    else:
        right = facing == "east"
        y0, y1 = (0.0 if "north" in joined else 0.06), (1.0 if "south" in joined else 0.94)
        cv.rect((0.06, y0, 0.94, y1), TOP)                        # the top, looking down
        if "north" not in joined:
            cv.rect((0.06, y0, 0.94, y0 + 0.03), TOP_LIT)
        if "south" not in joined:
            cv.rect((0.06, y1 - 0.06, 0.94, y1), WALL)
        fx0, fx1 = (0.72, 0.94) if right else (0.06, 0.28)       # the open front, empty
        ya, yb = y0 + w("north"), y1 - w("south") - (0.06 if "south" not in joined else 0)
        cv.rect((fx0, ya, fx1, yb), (150, 150, 150))
    cv.silhouette(open_sides)
    cv.save(book_path(facing, cw, ccw), book_path(facing, cw, ccw, True))


def draw_bookends():
    """The small steel bookends vanilla's bookcase stands at the end of a row."""
    for path, (w, h) in ((BOOKEND_EAST, (0.5, 0.9)), (BOOKEND_NORTH, (0.9, 0.5))):
        cv = Canvas()
        x0, y0 = (1 - w) / 2, (1 - h) / 2
        cv.rect((x0, y0, x0 + w, y0 + h), STEEL, tint=False)
        cv.rect((x0, y0, x0 + w, y0 + min(w, h) * 0.2), STEEL_LIT, tint=False)
        cv.silhouette(set(SIDES))
        cv.save(path)


def draw_all():
    for d in (KITCHEN_DIR, BOOK_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for f in SIDES:
        for cw in "oj":
            for ccw in "oj":
                for m in MODULES:
                    draw_kitchen(m, f, cw, ccw)
                draw_bookcase(f, cw, ccw)
        # Def graphics (blueprint, minified, ghost): the free-standing unit.
        for m in MODULES:
            shutil.copy(kitchen_path(m, f, "o", "o"), f"{KITCHEN_DIR}/Slopkea_{m}_{f}.png")
            shutil.copy(kitchen_path(m, f, "o", "o", True), f"{KITCHEN_DIR}/Slopkea_{m}_{f}m.png")
        shutil.copy(book_path(f, "o", "o"), f"{BOOK_DIR}/Slopkea_Bookcase_{f}.png")
        shutil.copy(book_path(f, "o", "o", True), f"{BOOK_DIR}/Slopkea_Bookcase_{f}m.png")
    draw_bookends()
