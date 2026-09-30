"""Draws every Slopkea texture. Run from the repo root: python3 Source/Art/draw_sprites.py

Both pieces join up with their neighbours, and a building's texture is baked
into the map mesh, so each one is drawn as a set of per-cell VARIANTS rather
than as overlays turned on the fly. The C# picks the variant from its
neighbours; verify_art.py checks the two agree.
"""
import os
import shutil

from slopkea_draw import (CCW, CW, OPP, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, FOOT,
                          OAK, OAK_DARK, OAK_LIT, OAK_WALL,
                          Canvas, local_rect)

ROOT = "Textures/Things/Building/Furniture/Slopkea"
TABLE_DIR = ROOT + "/Table"
SECT_DIR = ROOT + "/Sectional"
ROCKER_DIR = ROOT + "/RockingChair"
ROCKER_KINDS = ("Wood", "Cloth")

# Table variant index: bit set = a table segment is joined on that side.
# Same bit order as the TrashPower pipe atlas: N=1, E=2, S=4, W=8.
BITS = {"north": 1, "east": 2, "south": 4, "west": 8}

# Sectional side states, per side of the seat: arm, joined, corner backrest.
SIDE_STATES = "ajc"
FACINGS = ("north", "east", "south", "west")

# Sectional layout, in cells, in the seat's own frame.
ARM = 0.16
BACK = 0.28
GAP = 0.02
H_PLINTH, H_CUSHION, H_ARM, H_BACK = 0.06, 0.10, 0.22, 0.32

# Table layout, in screen fractions.
TABLE_TOP_END = 0.80     # where the top face stops when the front (south) is open
TABLE_APRON_END = 0.90   # apron (the table's wall) below it; legs below that


def table_path(i):
    return f"{TABLE_DIR}/Slopkea_Table_{i}.png"


def sect_path(facing, cw, ccw, mask=False):
    return f"{SECT_DIR}/Slopkea_Sectional_{facing}_{cw}{ccw}{'_m' if mask else ''}.png"


def draw_table(i):
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(BITS) - joined
    cv = Canvas()
    south_open = "south" in open_sides
    top_end = TABLE_TOP_END if south_open else 1.0

    cv.rect((0, 0, 1, top_end), TOP)
    # Planks run east-west on fixed world fractions, so seams line up across cells.
    for y in (1 / 3, 2 / 3):
        if y < top_end:
            cv.rect((0, y - 0.004, 1, y + 0.004), SEAM)
    # Butt joints: one identical mark per plank row, staggered.
    for y0, y1, x in ((0, 1 / 3, 0.25), (1 / 3, 2 / 3, 0.75), (2 / 3, top_end, 0.25)):
        if y1 > y0:
            cv.rect((x - 0.004, y0, x + 0.004, min(y1, top_end)), SEAM)
    if "north" in open_sides:
        cv.rect((0, 0, 1, 0.02), TOP_LIT)
    if south_open:
        cv.rect((0, top_end, 1, TABLE_APRON_END), WALL)
        cv.rect((0, top_end, 1, top_end + 0.008), WALL_DARK)
        # Legs only at outside corners: the apron runs on under a joined side.
        if "west" in open_sides:
            cv.rect((0.03, TABLE_APRON_END, 0.13, 1.0), WALL_DARK)
        if "east" in open_sides:
            cv.rect((0.87, TABLE_APRON_END, 0.97, 1.0), WALL_DARK)
    cv.silhouette(open_sides)
    cv.save(table_path(i))


def side_inset(state):
    return {"a": ARM + GAP, "c": BACK + GAP, "j": 0.0}[state]


def draw_sectional(facing, cw, ccw):
    cv = Canvas()
    # A corner seat's front runs straight into the perpendicular seat in front of
    # it (which sees us as a joined side), so there is no silhouette there either.
    front_joined = "c" in (cw, ccw)
    screen_state = {facing: "j" if front_joined else "open", OPP[facing]: "open", CW[facing]: cw, CCW[facing]: ccw}
    open_sides = {s for s, st in screen_state.items() if st != "j"}
    joined_sides = set(screen_state) - open_sides

    def runs_on(r):
        """Screen sides where this rect reaches a joined cell edge."""
        x0, y0, x1, y1 = r
        touch = {"north": y0 <= 1e-6, "south": y1 >= 1 - 1e-6,
                 "west": x0 <= 1e-6, "east": x1 >= 1 - 1e-6}
        return {s for s in joined_sides if touch[s]}

    # Plinth. It stops short of an open screen-bottom edge so the feet show.
    south_open = "south" in open_sides
    plinth = (0, 0, 1, 0.93 if south_open else 1.0)
    cv.slab(plinth, H_PLINTH, face=WALL, wall=WALL_DARK, joined=runs_on(plinth))
    if south_open:
        if "west" in open_sides:
            cv.rect((0.05, 0.90, 0.15, 1.0), FOOT, tint=False)
        if "east" in open_sides:
            cv.rect((0.85, 0.90, 0.95, 1.0), FOOT, tint=False)

    # Seat cushion, inset from whatever stands at each side.
    # A corner seat's cushion runs right up to the seat in front, so the seating
    # inside an L or U is one unbroken surface.
    lo, hi = side_inset(ccw), 1 - side_inset(cw)
    f0 = 0.0 if front_joined else 0.05
    cushion = local_rect(facing, lo, hi, f0, 1 - BACK)
    cv.slab(cushion, H_CUSHION, joined=runs_on(cushion))
    # A seam where this cushion meets the next seat's.
    if ccw == "j":
        cv.rect(local_rect(facing, 0, 0.012, f0, 1 - BACK), SEAM)
    if cw == "j":
        cv.rect(local_rect(facing, 0.988, 1, f0, 1 - BACK), SEAM)

    raised = [(local_rect(facing, 0, 1, 1 - BACK, 1), H_BACK, "back")]
    for state, (a0, a1) in ((ccw, (0, None)), (cw, (None, 1))):
        if state == "j":
            continue
        w = ARM if state == "a" else BACK
        span = (0, w) if a0 == 0 else (1 - w, 1)
        raised.append((local_rect(facing, span[0], span[1], 0, 1 - BACK),
                       H_ARM if state == "a" else H_BACK, state))
    # Painter's order: further up the screen first, then taller last.
    raised.sort(key=lambda p: (p[0][3], p[1]))
    for r, h, kind in raised:
        cv.slab(r, h, joined=runs_on(r))
        if kind == "back":
            # Tufting: a row of identical buttons along the backrest.
            for a in (1 / 6, 1 / 2, 5 / 6):
                bx0, by0, bx1, by1 = local_rect(facing, a - 0.02, a + 0.02,
                                                1 - BACK * 0.5 - 0.02, 1 - BACK * 0.5 + 0.02)
                cv.rect((bx0, by0 - 0.03, bx1, by1 - 0.03), SEAM)
    cv.silhouette(open_sides)
    cv.save(sect_path(facing, cw, ccw), sect_path(facing, cw, ccw, mask=True))


def rocker_path(kind, facing, mask=False):
    return f"{ROCKER_DIR}/Slopkea_RockingChair{kind}_{facing}{'m' if mask else ''}.png"


def draw_rocking_chair(kind, facing):
    """A rocking chair, laid out in its own frame (a across, f front to back).

    Wood: the stuff is the whole chair. Cloth: the stuff is the upholstery only,
    on a fixed oak frame, so the frame is black in the mask.
    """
    cloth = kind == "Cloth"
    frame = dict(face=OAK, wall=OAK_WALL, lit=OAK_LIT, wall_dark=OAK_DARK, tint=False) if cloth else {}
    cv = Canvas()
    L = lambda a0, a1, f0, f1: local_rect(facing, a0, a1, f0, f1)

    parts = []
    # Rockers: two long runners, past the seat both ways - the thing that says "rocking".
    # Each runner tapers to half width over its last tenth at both tips, so it
    # reads as a curve lifting off the floor rather than a plank.
    for a0, a1 in ((0.2, 0.27), (0.73, 0.8)):
        mid = (a0 + a1) / 2
        parts.append((L(a0, a1, 0.12, 0.88), 0.03, "rocker"))
        for f0, f1 in ((0.03, 0.12), (0.88, 0.97)):
            parts.append((L(mid - 0.018, mid + 0.018, f0, f1), 0.02, "rocker"))
    parts.append((L(0.27, 0.73, 0.22, 0.74), 0.12, "seat"))
    for a0, a1 in ((0.24, 0.31), (0.69, 0.76)):
        parts.append((L(a0, a1, 0.26, 0.74), 0.24, "arm"))
    parts.append((L(0.25, 0.75, 0.74, 0.88), 0.4, "back"))
    parts.sort(key=lambda p: (p[2] != "rocker", p[0][3], p[1]))

    for r, h, name in parts:
        if name == "rocker":
            cv.slab(r, h, **(frame or dict(face=WALL, wall=WALL_DARK)))
            continue
        if name == "seat":
            cv.slab(r, h, **frame)
            if cloth:
                cv.slab(L(0.32, 0.68, 0.25, 0.72), 0.05)          # seat cushion
            else:
                for f in (0.33, 0.46, 0.59):                       # slats
                    cv.rect(L(0.27, 0.73, f - 0.005, f + 0.005), SEAM)
        elif name == "arm":
            cv.slab(r, h, **frame)
        elif name == "back":
            cv.slab(r, h, **frame)
            if cloth:
                cv.slab(L(0.3, 0.7, 0.755, 0.865), 0.08)        # padded back
            else:
                for a in (0.35, 0.45, 0.55, 0.65):                 # spindles
                    x0, y0, x1, y1 = L(a - 0.012, a + 0.012, 0.755, 0.865)
                    cv.rect((x0, y0, x1, y1), SEAM)
    cv.silhouette({"north", "east", "south", "west"})
    cv.save(rocker_path(kind, facing), rocker_path(kind, facing, mask=True) if cloth else None)


def main():
    for d in (TABLE_DIR, SECT_DIR, ROCKER_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for i in range(16):
        draw_table(i)
    for facing in FACINGS:
        for cw in SIDE_STATES:
            for ccw in SIDE_STATES:
                draw_sectional(facing, cw, ccw)
        # The def's own Graphic_Multi (blueprint, minified, placing ghost) is the
        # free-standing seat. Graphic_Multi masks append "m" with NO underscore.
        shutil.copy(sect_path(facing, "a", "a"), f"{SECT_DIR}/Slopkea_Sectional_{facing}.png")
        shutil.copy(sect_path(facing, "a", "a", True), f"{SECT_DIR}/Slopkea_Sectional_{facing}m.png")
    for kind in ROCKER_KINDS:
        for facing in FACINGS:
            draw_rocking_chair(kind, facing)
    print("drew 16 table and 36 sectional variants, 2 rocking chairs")


if __name__ == "__main__":
    main()
