"""Third wave: bench, wardrobe (side-joining, per facing) and room divider,
planter box (drag-to-shape, bit variants). Same join contracts as the rest."""
import os
import shutil

from slopkea_draw import SEAM, TOP, TOP_LIT, WALL, WALL_DARK, FOOT, Canvas

ROOT = "Textures/Things/Building/Furniture/Slopkea"
BENCH_DIR, WARDROBE_DIR = ROOT + "/Bench", ROOT + "/Wardrobe"
DIVIDER_DIR, PLANTER_DIR = ROOT + "/Divider", ROOT + "/Planter"
SIDES = ("north", "east", "south", "west")
BITS = {"north": 1, "east": 2, "south": 4, "west": 8}
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}

SOIL, SOIL_DARK, SOIL_LIT = (92, 66, 44), (70, 50, 34), (112, 84, 58)
PAPER, PAPER_LIT = (238, 230, 206), (250, 245, 228)
STEEL = (150, 156, 164)


def side_path(kind, facing, cw, ccw, mask=False):
    d = BENCH_DIR if kind == "Bench" else WARDROBE_DIR
    return f"{d}/Slopkea_{kind}_{facing}_{cw}{ccw}{'_m' if mask else ''}.png"


def divider_path(i, mask=False):
    return f"{DIVIDER_DIR}/Slopkea_Divider_{i}{'_m' if mask else ''}.png"


def planter_path(i, mask=False):
    return f"{PLANTER_DIR}/Slopkea_Planter_{i}{'_m' if mask else ''}.png"


def joined_of(facing, cw, ccw):
    return {s for s, st in ((CW[facing], cw), (CCW[facing], ccw)) if st == "j"}


# --- Bench -------------------------------------------------------------------------

def draw_bench(facing, cw, ccw):
    """A plank bench with no back. Joined ends run the seat straight on, so a row
    reads as one long pew; legs stand only at the open ends. It has no front or
    back, so north draws as south and west as east."""
    joined = joined_of(facing, cw, ccw)
    open_sides = set(SIDES) - joined
    cv = Canvas()
    if facing in ("north", "south"):
        x0 = 0.0 if "west" in joined else 0.04
        x1 = 1.0 if "east" in joined else 0.96
        for side, lx in (("west", 0.08), ("east", 0.84)):
            if side not in joined:
                cv.rect((lx, 0.60, lx + 0.08, 0.84), WALL_DARK)          # legs
        cv.rect((x0, 0.30, x1, 0.56), TOP)                               # seat top
        cv.rect((x0, 0.30, x1, 0.33), TOP_LIT)
        cv.rect((x0, 0.43, x1, 0.435), SEAM)                             # two planks
        cv.rect((x0, 0.56, x1, 0.63), WALL)                              # seat edge
    else:
        y0 = 0.0 if "north" in joined else 0.04
        y1 = 1.0 if "south" in joined else 0.90
        cv.rect((0.33, y0, 0.67, y1), TOP)
        if "north" not in joined:
            cv.rect((0.33, y0, 0.67, y0 + 0.03), TOP_LIT)
        cv.rect((0.497, y0, 0.503, y1), SEAM)
        if "south" not in joined:
            cv.rect((0.33, y1 - 0.06, 0.67, y1), WALL)                   # end grain
            for lx in (0.36, 0.58):
                cv.rect((lx, y1, lx + 0.06, min(1.0, y1 + 0.08)), WALL_DARK)
    cv.silhouette(open_sides)
    cv.save(side_path("Bench", facing, cw, ccw), side_path("Bench", facing, cw, ccw, True))


# --- Wardrobe ----------------------------------------------------------------------

def draw_wardrobe(facing, cw, ccw):
    """A tall two-door wardrobe. Joined sides share a carcass wall, so a run reads
    as one fitted wall of wardrobes. Door knobs are steel (untinted)."""
    joined = joined_of(facing, cw, ccw)
    open_sides = set(SIDES) - joined
    cv = Canvas()
    w = lambda s: 0.015 if s in joined else 0.04
    if facing in ("south", "north"):
        cv.rect((0, 0.01, 1, 0.99), WALL)
        cv.rect((0, 0.01, 1, 0.09), TOP_LIT)                             # top
        cv.rect((0, 0.09, 1, 0.105), SEAM)
        if facing == "south":
            x0, x1 = w("west"), 1 - w("east")
            for d0, d1 in ((x0, 0.495), (0.505, x1)):
                cv.rect((d0, 0.12, d1, 0.94), TOP)                       # doors
                cv.rect((d0, 0.12, d1, 0.14), TOP_LIT)
            for kx in (0.46, 0.54):
                cv.ellipse((kx - 0.018, 0.50, kx + 0.018, 0.536), STEEL, tint=False)
            cv.rect((0, 0.94, 1, 0.99), WALL_DARK)                       # plinth
        else:
            cv.rect((0, 0.105, 1, 0.99), TOP)                            # plain back
            cv.rect((0, 0.94, 1, 0.99), WALL_DARK)
    else:
        right = facing == "east"
        y0, y1 = (0.0 if "north" in joined else 0.04), (1.0 if "south" in joined else 0.94)
        cv.rect((0.04, y0, 0.96, y1), TOP)
        if "north" not in joined:
            cv.rect((0.04, y0, 0.96, y0 + 0.03), TOP_LIT)
        if "south" not in joined:
            cv.rect((0.04, y1 - 0.06, 0.96, y1), WALL)
        fx0, fx1 = (0.82, 0.96) if right else (0.04, 0.18)               # doors, edge-on
        cv.rect((fx0, y0 + w("north"), fx1, y1 - w("south")), WALL)
        cv.rect((fx0, 0.495, fx1, 0.505), SEAM)
    cv.silhouette(open_sides)
    cv.save(side_path("Wardrobe", facing, cw, ccw), side_path("Wardrobe", facing, cw, ccw, True))


# --- Room divider ------------------------------------------------------------------

def draw_divider(i):
    """A folding paper screen. It follows its joins: a run east-west shows the
    panels face-on; a run north-south is seen edge-on, as the frame's top rail.
    Posts stand where panels hinge. Paper is fixed (untinted); the frame is stuff."""
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    ew = joined & {"east", "west"} or not (joined & {"north", "south"})
    if joined & {"north", "south"}:
        # Edge-on: a rail from the centre to each joined north/south edge.
        y0 = 0.0 if "north" in joined else 0.42
        y1 = 1.0 if "south" in joined else 0.58
        cv.rect((0.44, y0, 0.56, y1), TOP)
        cv.rect((0.44, y0, 0.47, y1), TOP_LIT)
    if ew:
        x0 = 0.0 if "west" in joined else 0.08
        x1 = 1.0 if "east" in joined else 0.92
        cv.rect((x0, 0.12, x1, 0.80), TOP)                               # frame
        cv.rect((x0, 0.12, x1, 0.15), TOP_LIT)
        for p0, p1 in ((max(x0, 0.0) + 0.05, 0.47), (0.53, min(x1, 1.0) - 0.05)):
            cv.rect((p0, 0.19, p1, 0.74), PAPER, tint=False)             # paper panels
            cv.rect((p0, 0.19, p1, 0.21), PAPER_LIT, tint=False)
            for k in (1, 2, 3):
                y = 0.19 + k * (0.74 - 0.19) / 4
                cv.rect((p0, y - 0.005, p1, y + 0.005), WALL, tint=True)  # lattice
        cv.rect((0.47, 0.12, 0.53, 0.86), WALL)                           # hinge post
        for side, fx in (("west", x0), ("east", x1 - 0.06)):
            if side not in joined:
                cv.rect((fx, 0.12, fx + 0.06, 0.86), WALL)               # end posts
    cv.silhouette(open_sides)
    cv.save(divider_path(i), divider_path(i, True))


# --- Planter box -------------------------------------------------------------------

def draw_planter(i):
    """A raised timber bed. The rim runs only round the outside of the dragged
    shape, so the soil is one continuous bed; the front rim shows its wall.
    Soil is untinted; the timber takes the stuff."""
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    rim = 0.09
    bottom = 0.88 if "south" in open_sides else 1.0
    cv.rect((0, 0, 1, bottom), SOIL, tint=False)
    for k in range(5):                                                   # furrows
        y = 0.12 + k * 0.17
        if y < bottom - 0.04:
            cv.rect((0, y, 1, y + 0.02), SOIL_DARK, tint=False)
            cv.rect((0, y + 0.02, 1, y + 0.03), SOIL_LIT, tint=False)
    if "north" in open_sides:
        cv.rect((0, 0, 1, rim), TOP)
        cv.rect((0, 0, 1, 0.02), TOP_LIT)
    if "west" in open_sides:
        cv.rect((0, 0, rim, bottom), TOP)
    if "east" in open_sides:
        cv.rect((1 - rim, 0, 1, bottom), TOP)
    if "south" in open_sides:
        cv.rect((0, bottom - rim, 1, bottom), TOP)
        cv.rect((0, bottom, 1, 1.0), WALL)                               # front board
        cv.rect((0, bottom, 1, bottom + 0.01), WALL_DARK)
    cv.silhouette(open_sides)
    cv.save(planter_path(i), planter_path(i, True))


def draw_all():
    for d in (BENCH_DIR, WARDROBE_DIR, DIVIDER_DIR, PLANTER_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for f in SIDES:
        for cw in "oj":
            for ccw in "oj":
                draw_bench(f, cw, ccw)
                draw_wardrobe(f, cw, ccw)
        for kind, d in (("Bench", BENCH_DIR), ("Wardrobe", WARDROBE_DIR)):
            shutil.copy(side_path(kind, f, "o", "o"), f"{d}/Slopkea_{kind}_{f}.png")
            shutil.copy(side_path(kind, f, "o", "o", True), f"{d}/Slopkea_{kind}_{f}m.png")
    for i in range(16):
        draw_divider(i)
        draw_planter(i)
