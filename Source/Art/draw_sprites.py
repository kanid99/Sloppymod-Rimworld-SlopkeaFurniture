"""Draws every Slopkea texture. Run from the repo root: python3 Source/Art/draw_sprites.py

The joining pieces join up with their neighbours, and a building's texture is baked
into the map mesh, so each one is drawn as a set of per-cell VARIANTS rather
than as overlays turned on the fly. The C# picks the variant from its
neighbours; verify_art.py checks the two agree.
"""
import os
import shutil

from PIL import Image

from slopkea_draw import (SS, CCW, CW, OPP, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, FOOT,
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
TABLE_TOP_END = 0.76     # where the top face stops when the front (south) is open
TABLE_APRON_END = 0.85   # apron (the table's wall) below it; legs below that


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
        # Chunky, like VFE's: a leg reads at play zoom or it is not there.
        if "west" in open_sides:
            cv.rect((0.04, TABLE_APRON_END, 0.19, 1.0), WALL)
            cv.rect((0.04, TABLE_APRON_END, 0.07, 1.0), TOP)
        if "east" in open_sides:
            cv.rect((0.81, TABLE_APRON_END, 0.96, 1.0), WALL)
            cv.rect((0.81, TABLE_APRON_END, 0.84, 1.0), TOP)
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
    """A view per facing, in three-quarter elevation like vanilla furniture rather
    than as a floor plan: from straight above a rocking chair is just a box.

    Wood: a classic spindle-back rocker on curved runners, all stuff.
    Cloth: a nursery glider (see draw_glider).
    """
    if facing == "west":
        return  # mirrored from east in main(): both chairs are symmetric side to side
    if kind == "Cloth":
        return draw_glider(facing)
    F_LIT, F, F_MID, F_WALL = TOP_LIT, TOP, (204, 204, 204), WALL
    cv = Canvas()
    ln = lambda pts, w, c: cv.line(pts, w, c)
    poly = lambda pts, c: cv.poly(pts, c)
    knob = lambda x, y, r, c: cv.ellipse((x - r, y - r, x + r, y + r), c)
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
        ln([(0.71, 0.52), (0.73, 0.37)], 0.055, F_MID)                      # arm support
        ln([(0.29, 0.33), (0.75, 0.36)], 0.06, F)                           # arm rail
        knob(0.76, 0.36, 0.04, F_LIT)                                       # arm scroll
    else:
        # Front (south) and back (north). The tell is the runners: two long skids
        # running past the chair at BOTH ends, widening towards the viewer, each end
        # rolled up off the floor. The chair stands on them: legs down to the
        # runners, arms tied into the back posts, a back tall enough to rise over
        # the seat.
        front = facing == "south"

        def runner(x, y_far, y_near):
            w_far, w_near = 0.04, 0.066                                     # perspective
            cv.soft_shadow((x - w_near / 2, y_far, x + w_near / 2, y_near), off=(0.012, 0.012))
            poly([(x - w_far / 2, y_far), (x + w_far / 2, y_far),
                  (x + w_near / 2, y_near), (x - w_near / 2, y_near)], F_WALL)
            poly([(x - w_far / 2, y_far), (x - w_far / 2 + 0.012, y_far),
                  (x - w_near / 2 + 0.016, y_near), (x - w_near / 2, y_near)], F)  # lit edge
            knob(x, y_near + 0.012, w_near * 0.62, F_WALL)                 # near end rolls up
            knob(x, y_near - 0.004, w_near * 0.55, F_LIT)
            knob(x, y_far - 0.006, w_far * 0.6, F)                         # far end lifts away

        RX = (0.29, 0.71)
        if front:
            for x in RX:
                runner(x, 0.24, 0.90)
            for x0, x1 in ((0.27, 0.25), (0.73, 0.75)):
                ln([(x0, 0.50), (x1, 0.06)], 0.07, F)                        # back posts
                knob(x1, 0.05, 0.043, F_LIT)                                  # finials
            # The shade behind the spindles runs up under the crest rail, so there
            # is no enclosed gap for the silhouette to fill black.
            poly([(0.29, 0.10), (0.71, 0.10), (0.71, 0.46), (0.29, 0.46)], F_WALL)
            for x in (0.35, 0.425, 0.5, 0.575, 0.65):                          # spindles
                ln([(x, 0.15), (x, 0.45)], 0.034, F_MID)
            ln([(0.25, 0.14), (0.5, 0.085), (0.75, 0.14)], 0.08, F)            # arched crest rail
            ln([(0.26, 0.135), (0.5, 0.08), (0.74, 0.135)], 0.022, F_LIT)
            poly([(0.26, 0.45), (0.74, 0.45), (0.79, 0.69), (0.21, 0.69)], F)  # seat top
            poly([(0.26, 0.45), (0.74, 0.45), (0.745, 0.475), (0.255, 0.475)], F_MID)
            poly([(0.21, 0.69), (0.79, 0.69), (0.79, 0.745), (0.21, 0.745)], F_WALL)  # apron
            for y in (0.53, 0.59, 0.65):                                       # slats
                f = (y - 0.45) / 0.24
                cv.rect((0.26 - 0.05 * f, y - 0.003, 0.74 + 0.05 * f, y + 0.003), SEAM)
            for x in RX:
                ln([(x - 0.04 if x < 0.5 else x + 0.04, 0.74), (x, 0.83)], 0.058, F_MID)  # front legs
            for (xb, xf) in ((0.26, 0.19), (0.74, 0.81)):
                ln([(xf, 0.66), (xf, 0.73)], 0.05, F_MID)                     # arm support
                ln([(xb, 0.30), (xf, 0.64)], 0.065, F)                        # arm rail
                knob(xf, 0.655, 0.045, F_LIT)                                  # scroll
        else:
            # The far ends only just clear the seat: long enough to read as runners
            # running on past the chair, short enough not to read as posts.
            for x in RX:
                runner(x, 0.22, 0.93)
            poly([(0.27, 0.27), (0.73, 0.27), (0.76, 0.50), (0.24, 0.50)], F)  # seat beyond the back
            poly([(0.27, 0.27), (0.73, 0.27), (0.73, 0.295), (0.27, 0.295)], F_LIT)
            for (xf, xb) in ((0.20, 0.26), (0.80, 0.74)):
                ln([(xf, 0.20), (xf, 0.28)], 0.045, F_MID)                    # arm support
                ln([(xf, 0.18), (xb, 0.56)], 0.065, F)                        # arm rail
                knob(xf, 0.18, 0.042, F_LIT)
            for x0, x1 in ((0.27, 0.25), (0.73, 0.75)):
                ln([(x0, 0.86), (x1, 0.30)], 0.072, F)                        # back posts
                knob(x1, 0.29, 0.043, F_LIT)
            poly([(0.29, 0.34), (0.71, 0.34), (0.71, 0.72), (0.29, 0.72)], F_WALL)
            for x in (0.35, 0.425, 0.5, 0.575, 0.65):
                ln([(x, 0.38), (x, 0.71)], 0.034, F_MID)
            ln([(0.25, 0.37), (0.5, 0.315), (0.75, 0.37)], 0.08, F)            # crest rail
            ln([(0.26, 0.365), (0.5, 0.31), (0.74, 0.365)], 0.022, F_LIT)
            ln([(0.27, 0.73), (0.73, 0.73)], 0.05, F_MID)                     # lower back rail
            for x in RX:
                ln([(x - 0.02 if x < 0.5 else x + 0.02, 0.76), (x, 0.86)], 0.058, F_MID)  # rear legs

    cv.silhouette({"north", "east", "south", "west"}, ring=5 * SS)
    cv.save(rocker_path(kind, facing))


# The glider's frame is painted white and never takes the stuff colour.
PAINT_LIT, PAINT, PAINT_MID, PAINT_WALL = (252, 251, 248), (238, 237, 233), (216, 215, 210), (182, 181, 176)


def draw_glider(facing):
    """The cloth chair: a nursery glider rocker.

    Overstuffed and upholstered in the stuff: a tall back cushion in three
    channel-tufted pillows, pillow arm pads and a thick seat cushion. The frame is
    white paint (black in the mask) and stands on a FLAT base: a glider swings
    on links rather than rocking on curved runners, so there are no runners here.
    """
    cv = Canvas()
    fr = lambda pts, c: cv.poly(pts, c, False)                              # frame (untinted)
    fl = lambda pts, w, c: cv.line(pts, w, c, False)
    cu = lambda pts, c: cv.poly(pts, c)                                     # cushion (stuff)
    blob = lambda r, c: cv.ellipse(r, c)
    cv.soft_shadow((0.12, 0.84, 0.88, 0.95), off=(0.0, 0.0))

    def pillow(x0, y0, x1, y1):
        """One overstuffed channel: a rounded pad, lit on top, shaded underneath."""
        rad = min(x1 - x0, y1 - y0) * 0.45
        blob((x0, y0, x0 + 2 * rad, y1), WALL)
        blob((x1 - 2 * rad, y0, x1, y1), WALL)
        cu([(x0 + rad, y0), (x1 - rad, y0), (x1 - rad, y1), (x0 + rad, y1)], WALL)
        blob((x0, y0, x0 + 2 * rad, y1 - 0.02), TOP)
        blob((x1 - 2 * rad, y0, x1, y1 - 0.02), TOP)
        cu([(x0 + rad, y0), (x1 - rad, y0), (x1 - rad, y1 - 0.02), (x0 + rad, y1 - 0.02)], TOP)
        cu([(x0 + rad, y0 + 0.012), (x1 - rad, y0 + 0.012), (x1 - rad, y0 + 0.03), (x0 + rad, y0 + 0.03)], TOP_LIT)

    if facing == "south":
        # Glider base: two flat skids on the floor and a front stretcher.
        for x0, x1 in ((0.17, 0.29), (0.71, 0.83)):
            fr([(x0 + 0.02, 0.74), (x1 - 0.02, 0.74), (x1, 0.93), (x0, 0.93)], PAINT_WALL)
            fr([(x0 + 0.02, 0.74), (x1 - 0.02, 0.74), (x1 - 0.015, 0.78), (x0 + 0.015, 0.78)], PAINT)
        fr([(0.24, 0.86), (0.76, 0.86), (0.76, 0.90), (0.24, 0.90)], PAINT_MID)
        # Glide links: short angled arms between base and chair, the mechanism's tell.
        for x in (0.23, 0.77):
            fl([(x, 0.84), (x + (0.03 if x < 0.5 else -0.03), 0.74)], 0.04, PAINT_MID)
        # Back frame behind the cushion: solid, so no gap between cushion and arm
        # is left enclosed for the silhouette to fill black.
        fr([(0.17, 0.05), (0.83, 0.05), (0.83, 0.66), (0.17, 0.66)], PAINT)
        fl([(0.19, 0.05), (0.5, 0.025), (0.81, 0.05)], 0.06, PAINT)
        # Back cushion: three stacked channels, biggest at the top where it rolls over.
        pillow(0.22, 0.03, 0.78, 0.20)
        pillow(0.23, 0.18, 0.77, 0.33)
        pillow(0.24, 0.31, 0.76, 0.46)
        # Seat box and a thick seat cushion.
        fr([(0.19, 0.64), (0.81, 0.64), (0.81, 0.75), (0.19, 0.75)], PAINT_MID)
        fr([(0.19, 0.64), (0.81, 0.64), (0.81, 0.66), (0.19, 0.66)], PAINT_LIT)
        cu([(0.26, 0.45), (0.74, 0.45), (0.77, 0.60), (0.23, 0.60)], TOP)
        cu([(0.26, 0.45), (0.74, 0.45), (0.745, 0.47), (0.255, 0.47)], TOP_LIT)
        cu([(0.23, 0.60), (0.77, 0.60), (0.77, 0.665), (0.23, 0.665)], WALL)  # cushion front
        # Arms: wide flat white side panels with a pillow pad on top.
        for x0, x1 in ((0.12, 0.24), (0.76, 0.88)):
            fr([(x0, 0.40), (x1, 0.40), (x1, 0.76), (x0, 0.76)], PAINT)
            fr([(x0, 0.70), (x1, 0.70), (x1, 0.76), (x0, 0.76)], PAINT_WALL)
            fr([(x0, 0.40), (x0 + 0.02, 0.40), (x0 + 0.02, 0.76), (x0, 0.76)], PAINT_LIT)
            pillow(x0 - 0.005, 0.30, x1 + 0.005, 0.45)

    elif facing == "north":
        # From behind: the back of the frame is nearest us; arms and base run away.
        for x0, x1 in ((0.17, 0.29), (0.71, 0.83)):
            fr([(x0 + 0.03, 0.18), (x1 - 0.03, 0.18), (x1, 0.94), (x0, 0.94)], PAINT_WALL)
            fr([(x0 + 0.03, 0.18), (x1 - 0.03, 0.18), (x1 - 0.028, 0.22), (x0 + 0.028, 0.22)], PAINT)
        fr([(0.14, 0.24), (0.86, 0.24), (0.86, 0.60), (0.14, 0.60)], PAINT_MID)  # seat box, beyond
        # Arm panels and pads, beyond the back so higher up the screen.
        for x0, x1 in ((0.12, 0.24), (0.76, 0.88)):
            fr([(x0, 0.22), (x1, 0.22), (x1, 0.60), (x0, 0.60)], PAINT)
            pillow(x0 - 0.005, 0.15, x1 + 0.005, 0.28)
        cu([(0.24, 0.26), (0.76, 0.26), (0.76, 0.40), (0.24, 0.40)], TOP)      # seat, glimpsed
        # The back: white frame round the back of the cushion.
        fr([(0.20, 0.30), (0.80, 0.30), (0.80, 0.86), (0.20, 0.86)], PAINT)
        fr([(0.20, 0.30), (0.80, 0.30), (0.80, 0.33), (0.20, 0.33)], PAINT_LIT)
        fr([(0.20, 0.80), (0.80, 0.80), (0.80, 0.86), (0.20, 0.86)], PAINT_WALL)
        pillow(0.20, 0.22, 0.80, 0.36)                                          # cushion rolling over the top
        cu([(0.26, 0.38), (0.74, 0.38), (0.74, 0.78), (0.26, 0.78)], WALL)     # back of the cushion
        for y in (0.51, 0.64):                                                  # channel seams through
            cv.rect((0.26, y - 0.004, 0.74, y + 0.004), SEAM)
        fr([(0.24, 0.87), (0.76, 0.87), (0.76, 0.91), (0.24, 0.91)], PAINT_MID)  # rear stretcher

    elif facing == "east":
        # Side profile, facing right: flat base, glide links, reclined overstuffed back.
        fr([(0.10, 0.87), (0.90, 0.87), (0.88, 0.93), (0.12, 0.93)], PAINT_WALL)  # base skid
        fr([(0.10, 0.87), (0.90, 0.87), (0.90, 0.885), (0.10, 0.885)], PAINT)
        for xb, xt in ((0.26, 0.31), (0.70, 0.65)):                               # glide links
            fl([(xb, 0.87), (xt, 0.73)], 0.045, PAINT_MID)
        fr([(0.18, 0.66), (0.84, 0.66), (0.84, 0.74), (0.18, 0.74)], PAINT_MID)   # seat rail
        fl([(0.22, 0.68), (0.10, 0.05)], 0.07, PAINT)                            # reclined back post
        # Back cushion: one thick pad up the reclined back, a darker underside, the
        # rolled top, and the channel seams across it as tone steps.
        cv.line([(0.285, 0.62), (0.19, 0.11)], 0.17, WALL)
        cv.line([(0.27, 0.60), (0.18, 0.10)], 0.15, TOP)
        cv.line([(0.24, 0.58), (0.15, 0.10)], 0.035, TOP_LIT)
        for (ax, ay), (bx, by) in (((0.17, 0.27), (0.30, 0.245)), ((0.20, 0.43), (0.33, 0.405))):
            cv.line([(ax, ay), (bx, by)], 0.012, SEAM)
        # Thick seat cushion.
        cu([(0.26, 0.54), (0.80, 0.54), (0.80, 0.66), (0.26, 0.66)], TOP)
        cu([(0.26, 0.54), (0.80, 0.54), (0.80, 0.56), (0.26, 0.56)], TOP_LIT)
        cu([(0.26, 0.62), (0.80, 0.62), (0.80, 0.66), (0.26, 0.66)], WALL)
        # Arm: a flat white panel from the back to a curved front, pad on top.
        fr([(0.28, 0.44), (0.80, 0.44), (0.84, 0.50), (0.84, 0.74), (0.28, 0.74)], PAINT)
        fr([(0.28, 0.60), (0.76, 0.60), (0.76, 0.74), (0.28, 0.74)], PAINT_MID)
        fr([(0.28, 0.44), (0.80, 0.44), (0.81, 0.455), (0.28, 0.455)], PAINT_LIT)
        pillow(0.28, 0.36, 0.72, 0.47)

    cv.silhouette({"north", "east", "south", "west"}, ring=5 * SS)
    cv.save(rocker_path("Cloth", facing), rocker_path("Cloth", facing, mask=True))


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
    import draw_modular
    rugs = draw_modular.draw_all()
    import draw_kitchen
    draw_kitchen.draw_all()
    import draw_kitchen_tall
    draw_kitchen_tall.draw_all()
    import draw_more
    draw_more.draw_all()
    print(f"drew 16 table and 36 sectional variants, 2 rocking chairs, "
          f"16 desk, {rugs} rug and 16 shelf variants, 48 kitchen and 16 bookcase variants, "
          f"16 each of bench, wardrobe, divider and planter")


if __name__ == "__main__":
    main()
