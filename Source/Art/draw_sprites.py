"""Draws every Slopkea texture. Run from the repo root: python3 Source/Art/draw_sprites.py

Both pieces join up with their neighbours, and a building's texture is baked
into the map mesh, so each one is drawn as a set of per-cell VARIANTS rather
than as overlays turned on the fly. The C# picks the variant from its
neighbours; verify_art.py checks the two agree.
"""
import os
import shutil

from PIL import Image

from slopkea_draw import (SS, CCW, CW, OPP, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, FOOT,
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
    """A rocking chair, drawn as a VIEW per facing - like vanilla furniture, in
    three-quarter elevation rather than as a floor plan. From straight above a
    rocking chair is just a box; what says "rocking chair" is the curved runner
    under it and the tall back, so every view is built to show those.

    Wood: the stuff is the whole chair. Cloth: the stuff is the upholstery only,
    on a fixed oak frame, so the frame is black in the mask.
    """
    if facing == "west":
        return  # mirrored from east in main(): the chair is symmetric side to side
    cloth = kind == "Cloth"
    t = not cloth
    if cloth:
        F_LIT, F, F_MID, F_WALL = OAK_LIT, OAK, (148, 108, 70), OAK_WALL
    else:
        F_LIT, F, F_MID, F_WALL = TOP_LIT, TOP, (204, 204, 204), WALL
    cv = Canvas()
    ln = lambda pts, w, c: cv.line(pts, w, c, t)
    poly = lambda pts, c: cv.poly(pts, c, t)
    knob = lambda x, y, r, c: cv.ellipse((x - r, y - r, x + r, y + r), c, t)
    # A soft floor shadow under the whole chair (alpha below the silhouette threshold).
    cv.soft_shadow((0.14, 0.84, 0.86, 0.93), off=(0.0, 0.0))

    if facing == "east":
        # Side profile, facing right. The runner is a smile: low in the middle, both
        # ends lifting off the floor. Everything else stands on it.
        ry = lambda x: 0.86 - 0.45 * (x - 0.5) ** 2
        xs = [0.06 + k * 0.02 for k in range(45)]
        ln([(x, ry(x)) for x in xs], 0.07, F_WALL)
        ln([(x, ry(x) - 0.018) for x in xs[2:-2]], 0.022, F)             # lit top of the runner
        for x in (0.36, 0.70):                                              # legs
            ln([(x, ry(x)), (x, 0.56)], 0.065, F_MID)
        ln([(0.34, 0.54), (0.19, 0.07)], 0.075, F)                          # back post, leaning back
        knob(0.19, 0.07, 0.045, F_LIT)                                      # crest
        poly([(0.28, 0.50), (0.78, 0.50), (0.78, 0.53), (0.28, 0.53)], F_LIT)  # seat top
        poly([(0.28, 0.53), (0.78, 0.53), (0.78, 0.59), (0.28, 0.59)], F_MID)  # seat edge
        if cloth:
            cv.line([(0.41, 0.46), (0.28, 0.13)], 0.09, TOP)                # back pad
            cv.line([(0.40, 0.44), (0.29, 0.15)], 0.03, TOP_LIT)
            cv.poly([(0.36, 0.43), (0.76, 0.44), (0.77, 0.50), (0.35, 0.50)], TOP)   # seat cushion
            cv.poly([(0.36, 0.43), (0.76, 0.44), (0.76, 0.455), (0.36, 0.445)], TOP_LIT)
        ln([(0.71, 0.52), (0.73, 0.37)], 0.055, F_MID)                      # arm support
        ln([(0.29, 0.33), (0.75, 0.36)], 0.06, F)                           # arm rail
        knob(0.76, 0.36, 0.04, F_LIT)                                       # arm scroll

    elif facing == "south":
        # Front view, facing the viewer: the tall back rises above the seat, and the
        # runners come towards us under it and curl up at the tips.
        for x in (0.27, 0.73):
            ln([(x, 0.50), (x, 0.90)], 0.06, F_WALL)                        # runner, end-on
            knob(x, 0.91, 0.042, F)                                         # curled tip
        for x in (0.25, 0.75):
            ln([(x, 0.52), (x, 0.07)], 0.07, F)                             # back posts
            knob(x, 0.06, 0.042, F_LIT)                                     # finials
        ln([(0.25, 0.13), (0.5, 0.085), (0.75, 0.13)], 0.075, F)            # curved crest rail
        ln([(0.25, 0.45), (0.75, 0.45)], 0.05, F_MID)                       # lower back rail
        if cloth:
            cv.poly([(0.30, 0.15), (0.70, 0.15), (0.70, 0.44), (0.30, 0.44)], TOP)
            cv.poly([(0.30, 0.15), (0.70, 0.15), (0.70, 0.18), (0.30, 0.18)], TOP_LIT)
            for x in (0.40, 0.5, 0.60):                                      # tufting
                cv.rect((x - 0.012, 0.29, x + 0.012, 0.31), SEAM)
        else:
            for x in (0.34, 0.42, 0.5, 0.58, 0.66):                           # spindles
                ln([(x, 0.16), (x, 0.43)], 0.032, F_MID)
        poly([(0.23, 0.47), (0.77, 0.47), (0.80, 0.67), (0.20, 0.67)], F)    # seat top
        poly([(0.23, 0.47), (0.77, 0.47), (0.775, 0.49), (0.225, 0.49)], F_LIT)
        poly([(0.20, 0.67), (0.80, 0.67), (0.80, 0.72), (0.20, 0.72)], F_WALL)  # seat front edge
        if cloth:
            cv.poly([(0.29, 0.50), (0.71, 0.50), (0.73, 0.65), (0.27, 0.65)], TOP)
            cv.poly([(0.29, 0.50), (0.71, 0.50), (0.713, 0.52), (0.287, 0.52)], TOP_LIT)
        for x in (0.25, 0.75):
            ln([(x, 0.72), (x, 0.84)], 0.06, F_MID)                         # front legs
        for x in (0.17, 0.83):
            ln([(x, 0.60), (x, 0.73)], 0.05, F_MID)                         # arm supports
            ln([(x, 0.30), (x, 0.61)], 0.06, F)                             # arm rails
            knob(x, 0.62, 0.042, F_LIT)                                     # arm scrolls

    elif facing == "north":
        # Rear view, facing away: the back of the backrest is nearest us and rises up
        # the screen; the runners run out past it at both ends.
        for x in (0.27, 0.73):
            ln([(x, 0.08), (x, 0.92)], 0.06, F_WALL)                        # runners
            knob(x, 0.07, 0.036, F)                                          # front tips
            knob(x, 0.93, 0.042, F)                                          # rear tips
        poly([(0.23, 0.22), (0.77, 0.22), (0.79, 0.40), (0.21, 0.40)], F)     # seat, beyond the back
        for x in (0.17, 0.83):
            ln([(x, 0.16), (x, 0.48)], 0.06, F)                             # arm rails
            knob(x, 0.15, 0.04, F_LIT)
        for x in (0.25, 0.75):
            ln([(x, 0.86), (x, 0.30)], 0.07, F)                             # back posts
            knob(x, 0.29, 0.042, F_LIT)
        ln([(0.25, 0.36), (0.5, 0.315), (0.75, 0.36)], 0.075, F)            # crest rail
        ln([(0.25, 0.72), (0.75, 0.72)], 0.05, F_MID)                       # lower back rail
        if cloth:
            cv.poly([(0.30, 0.38), (0.70, 0.38), (0.70, 0.71), (0.30, 0.71)], WALL)  # back of the pad
        else:
            for x in (0.34, 0.42, 0.5, 0.58, 0.66):
                ln([(x, 0.39), (x, 0.70)], 0.032, F_MID)
        for x in (0.25, 0.75):
            ln([(x, 0.74), (x, 0.88)], 0.06, F_MID)                         # back legs

    cv.silhouette({"north", "east", "south", "west"}, ring=3 * SS)
    cv.save(rocker_path(kind, facing), rocker_path(kind, facing, mask=True) if cloth else None)


def mirror_east_to_west(kind):
    """Graphic_Multi would mirror east for west anyway; write it so every view exists."""
    for mask in ((False, True) if kind == "Cloth" else (False,)):
        Image.open(rocker_path(kind, "east", mask)).transpose(Image.FLIP_LEFT_RIGHT).save(
            rocker_path(kind, "west", mask))


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
        mirror_east_to_west(kind)
    print("drew 16 table and 36 sectional variants, 2 rocking chairs")


if __name__ == "__main__":
    main()
