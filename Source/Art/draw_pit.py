"""SÄNKA conversation pit: the sunken floor and the built-in pit seats.

The floor joins like the rug - `Slopkea_Pit_<sides>_<corners>` - and is drawn as
carpet a step below the room: round the outside of the shape run the pit's lip and
its step-down walls, with the shadow they cast onto the carpet. The far (north)
wall shows its whole face, the side walls a sliver, and the near (south) wall only
its lip, as you'd see them looking down into a pit. The lip and walls are plaster
(untinted); the carpet takes the stuff.

The seats are the sectional drawn built in (no plinth or feet), under their own
names, `Slopkea_PitSeat_<facing>_<cw><ccw>[b|p]`.
"""
import os
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from draw_modular import BITS, CORNERS, SIDES, rug_variants
from slopkea_draw import C, SEAM, SS, Canvas, px

ROOT = "Textures/Things/Building/Furniture/Slopkea"
PIT_DIR = ROOT + "/Pit"

CARPET = (184, 184, 184)
CARPET_PILE = (170, 170, 170)
NEAR_LIP = 0.12   # the near (south) rim: its top, seen from above and behind
LIP, LIP_EDGE = (232, 228, 220), (196, 192, 184)          # untinted plaster
WALL_TOP, WALL_BOTTOM = (176, 172, 166), (122, 118, 112)  # the step-down face
FACE = 0.20       # depth of the far wall's face, as seen
SIDE = 0.07       # the side walls, seen nearly edge-on
LIPW = 0.085


def pit_path(i, c, mask=False):
    return f"{PIT_DIR}/Slopkea_Pit_{i}_{c}{'_m' if mask else ''}.png"


def pitseat_path(facing, cw, ccw, mask=False, back=False):
    suffix = back if isinstance(back, str) else ("b" if back else "")
    return f"{PIT_DIR}/Slopkea_PitSeat_{facing}_{cw}{ccw}{suffix}{'_m' if mask else ''}.png"


DROP = (54, 50, 46)


def drop_edge(cv, sides, inset=None):
    """Where the room floor (the rim) falls away into the pit, on `sides`: a dark
    edge line at the rim's inner edge and a soft shadow just below it."""
    inset = LIPW if inset is None else inset
    sh = Image.new("L", (C, C), 0)
    sd = ImageDraw.Draw(sh)
    for side in sides:
        a = inset if not isinstance(inset, dict) else inset[side]
        box = {"north": (0, a, 1, a + 0.07), "south": (0, 1 - a - 0.07, 1, 1 - a),
               "west": (a, 0, a + 0.07, 1), "east": (1 - a - 0.07, 0, 1 - a, 1)}[side]
        sd.rectangle([px(box[0]), px(box[1]), px(box[2]), px(box[3])], fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(int(0.025 * C)))
    sh = ImageChops.multiply(sh, cv.img.getchannel("A"))
    layer = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    layer.paste(Image.new("RGBA", (C, C), (0, 0, 0, 255)), (0, 0), sh.point(lambda v: int(v * 0.55)))
    cv.img.alpha_composite(layer)
    cv.d = ImageDraw.Draw(cv.img)
    for side in sides:
        a = inset if not isinstance(inset, dict) else inset[side]
        line = {"north": (0, a, 1, a + 0.014), "south": (0, 1 - a - 0.014, 1, 1 - a),
                "west": (a, 0, a + 0.014, 1), "east": (1 - a - 0.014, 0, 1 - a, 1)}[side]
        cv.rect(line, DROP, tint=False)


def wall_face(cv, r, vertical):
    """A step-down wall face, lit at its top edge and darkening into the pit."""
    x0, y0, x1, y1 = r
    n = max(1, px(y1 - y0) if not vertical else px(x1 - x0))
    for k in range(n):
        f = k / n
        col = tuple(int(a + (b - a) * f) for a, b in zip(WALL_TOP, WALL_BOTTOM))
        if vertical:       # side walls: lit at the rim (outer edge), dark at the floor
            x = px(x0) + k if vertical == "west" else px(x1) - 1 - k
            cv.d.line([(x, px(y0)), (x, px(y1) - 1)], fill=col)
        else:
            cv.d.line([(px(x0), px(y0) + k), (px(x1) - 1, px(y0) + k)], fill=col)
    cv.md.rectangle([px(x0), px(y0), px(x1) - 1, px(y1) - 1], fill=(0, 0, 0))


def draw_pit(i, c):
    joined = {s for s, b in BITS.items() if i & b}
    open_sides = set(SIDES) - joined
    cv = Canvas()
    cv.rect((0, 0, 1, 1), CARPET)
    for k in range(6):                                   # carpet pile: faint rows
        y = (k + 0.5) / 6
        cv.rect((0, y - 0.003, 1, y + 0.003), CARPET_PILE)

    # Where the walls stand, in this cell.
    n, s_, w, e = ("north" in open_sides, "south" in open_sides, "west" in open_sides, "east" in open_sides)
    top = LIPW + FACE if n else 0.0
    # Shadow cast down onto the carpet by the far wall and the side walls.
    sh = Image.new("L", (C, C), 0)
    sd = ImageDraw.Draw(sh)
    if n:
        sd.rectangle([0, px(top), C, px(top + 0.10)], fill=150)
    if w:
        sd.rectangle([px(SIDE + LIPW), 0, px(SIDE + LIPW + 0.07), C], fill=110)
    if e:
        sd.rectangle([px(1 - SIDE - LIPW - 0.05), 0, px(1 - SIDE - LIPW), C], fill=70)
    if s_:
        # Looking down past the near rim, the floor just behind it is in its lee.
        sd.rectangle([0, px(1 - NEAR_LIP - 0.09), C, px(1 - NEAR_LIP)], fill=120)
    # A hollow: the carpet darkens a little towards every wall. (Combined with
    # the wall shadows, not painted over them.)
    hollow = Image.new("L", (C, C), 0)
    hd = ImageDraw.Draw(hollow)
    for side, box in (("north", [0, 0, C, px(0.35)]), ("south", [0, px(0.65), C, C]),
                      ("west", [0, 0, px(0.3), C]), ("east", [px(0.7), 0, C, C])):
        if side in open_sides:
            hd.rectangle(box, fill=45)
    sh = ImageChops.lighter(sh, hollow)
    sh = sh.filter(ImageFilter.GaussianBlur(int(0.04 * C)))
    sh = Image.composite(sh, Image.new("L", (C, C), 0), cv.img.getchannel("A"))
    dark = Image.new("RGBA", (C, C), (0, 0, 0, 255))
    layer = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    layer.paste(dark, (0, 0), sh.point(lambda v: int(v * 0.6)))
    cv.img.alpha_composite(layer)

    if w:
        wall_face(cv, (LIPW, 0, LIPW + SIDE, 1), "west")
    if e:
        wall_face(cv, (1 - LIPW - SIDE, 0, 1 - LIPW, 1), "east")
    if n:
        wall_face(cv, (0, LIPW, 1, LIPW + FACE), None)
    # Inside corners: the room floor pokes into the pit, so its walls turn there.
    for name, (s1, s2, bit) in CORNERS.items():
        if not c & bit:
            continue
        right = "east" in (s1, s2)
        if "north" in (s1, s2):          # the far wall's face runs on round the corner
            x0 = 1 - LIPW - SIDE if right else 0
            wall_face(cv, (x0, 0, x0 + LIPW + SIDE, LIPW + FACE), None)
            cv.rect((x0, 0, x0 + LIPW + SIDE, LIPW), LIP, tint=False)
        else:                            # near corner: just the lip turns
            x0 = 1 - LIPW - SIDE if right else 0
            cv.rect((x0, 1 - LIPW, x0 + LIPW + SIDE, 1), LIP, tint=False)
            wall_face(cv, (x0, 0.8, x0 + LIPW + SIDE, 1 - LIPW), "east" if right else "west")
    # The lip: the room floor's edge, all round the outside of the shape.
    for side, r in (("north", (0, 0, 1, LIPW)), ("south", (0, 1 - LIPW, 1, 1)),
                    ("west", (0, 0, LIPW, 1)), ("east", (1 - LIPW, 0, 1, 1))):
        if side in open_sides:
            cv.rect(r, LIP, tint=False)
    if s_:
        cv.rect((0, 1 - NEAR_LIP, 1, 1), LIP, tint=False)                      # the near rim's top
    # The drop-off line where the rim falls away, on each open side. The rim is
    # the room floor, so there is no outline round the outside of the pit.
    drop_edge(cv, open_sides, {"north": LIPW, "west": LIPW, "east": LIPW, "south": NEAR_LIP})
    cv.silhouette(set(), ring=4 * SS)
    cv.save(pit_path(i, c), pit_path(i, c, True))


def draw_all():
    import draw_sprites as ds
    shutil.rmtree(PIT_DIR, ignore_errors=True)
    os.makedirs(PIT_DIR)
    n = 0
    for i, c in rug_variants():
        draw_pit(i, c)
        n += 1
    for f in ds.FACINGS:
        for cw in ds.SIDE_STATES:
            for ccw in ds.SIDE_STATES:
                for back in ("", "b", "p"):
                    ds.draw_sectional(f, cw, ccw, back, pit=True)
        shutil.copy(pitseat_path(f, "a", "a"), f"{PIT_DIR}/Slopkea_PitSeat_{f}.png")
        shutil.copy(pitseat_path(f, "a", "a", True), f"{PIT_DIR}/Slopkea_PitSeat_{f}m.png")
    return n
