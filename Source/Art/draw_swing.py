"""Free-standing seats drawn as views, like the rocking chairs: the papasan chair
and the three hanging swings.

Swings are 2x1, so they draw on a multi-cell canvas: `Big(w, h)` takes the same
drawing calls as Canvas (coordinates in cells, so (0..2, 0..1) for a 2x1 view)
and finishes against an all-open silhouette - these pieces never join anything.

Hanging: the ropes or chains rise from the swing's ends to the top of its
sprite. The C# only lets a swing be placed under a roof, so they always have
something to hang from.
"""
import math
import os
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from slopkea_draw import (BLACK, C, CELL, RING, SEAM, TOP, TOP_LIT, WALL, WALL_DARK, Canvas, px)

ROOT = "Textures/Things/Building/Furniture/Slopkea"
SWING_DIR = ROOT + "/Swing"
PAPASAN_DIR = ROOT + "/Papasan"
SWINGS = ("Daybed", "Rattan", "Platform")
FACINGS = ("north", "east", "south", "west")

# Fixed colours (untinted): rattan, rope, chain, the cream daybed cushion, white paint.
RATTAN_LIT, RATTAN, RATTAN_DARK = (214, 176, 116), (184, 144, 88), (132, 100, 58)
ROPE, ROPE_DARK = (222, 206, 170), (176, 158, 120)
CHAIN, CHAIN_DARK = (196, 200, 206), (120, 124, 130)
CREAM, CREAM_LIT, CREAM_DARK = (232, 226, 210), (246, 242, 230), (198, 190, 172)
PAINT, PAINT_LIT, PAINT_DARK = (240, 240, 236), (252, 252, 250), (200, 200, 196)


class Big(Canvas):
    """A Canvas `w` x `h` cells. Free-standing: every side is open."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (px(w), px(h)), (0, 0, 0, 0))
        self.mask = Image.new("RGB", (px(w), px(h)), (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.md = ImageDraw.Draw(self.mask)

    def finish(self, ring=RING):
        """Rounded corners, edge light and the black ring - Canvas.silhouette's
        treatment, for an all-open, multi-cell sprite."""
        W, H = self.img.size
        a = self.img.getchannel("A").point(lambda v: 255 if v > 127 else 0)
        rounded = a.filter(ImageFilter.GaussianBlur(int(0.03 * C))).point(lambda v: 255 if v > 150 else 0)
        cut = ImageChops.subtract(a, rounded)
        if cut.getbbox():
            self.img.paste(Image.new("RGBA", (W, H), (0, 0, 0, 0)), (0, 0), cut)
            self.mask.paste((0, 0, 0), (0, 0), cut)
            a = ImageChops.multiply(a, rounded)
        dd = int(0.08 * C)
        blur = ImageFilter.GaussianBlur(int(0.04 * C))
        inv = lambda im: im.point(lambda v: 255 - v)
        ul = a.transform(a.size, Image.AFFINE, (1, 0, -dd, 0, 1, -dd))
        dr = a.transform(a.size, Image.AFFINE, (1, 0, dd, 0, 1, dd))
        light = ImageChops.multiply(ImageChops.multiply(a, inv(ul)).filter(blur), a).point(lambda v: int(v * 0.28))
        shade = ImageChops.multiply(ImageChops.multiply(a, inv(dr)).filter(blur), a).point(lambda v: int(v * 0.22))
        rgb = self.img.convert("RGB")
        rgb = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), rgb, light)
        rgb = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), rgb, shade)
        rgb.putalpha(self.img.getchannel("A"))
        self.img = rgb
        er = a
        for _ in range(ring):
            er = er.filter(ImageFilter.MinFilter(3))
        self.img.paste(Image.new("RGBA", (W, H), BLACK + (255,)), (0, 0), ImageChops.subtract(a, er))
        self.d = ImageDraw.Draw(self.img)

    def save(self, path, mask_path=None):
        size = (CELL * self.w, CELL * self.h)
        self.img.resize(size, Image.LANCZOS).save(path)
        if mask_path:
            self.mask.resize(size, Image.LANCZOS).save(mask_path)


def path(kind, facing, mask=False):
    d = PAPASAN_DIR if kind == "Papasan" else SWING_DIR
    name = "Slopkea_Papasan" if kind == "Papasan" else f"Slopkea_Swing{kind}"
    return f"{d}/{name}_{facing}{'m' if mask else ''}.png"


# --- Papasan -----------------------------------------------------------------------

def weave(cv, cx, cy, rx, ry, rings=4):
    """Rattan weave on a bowl: concentric rings and radial ribs, as tone steps."""
    for k in range(1, rings + 1):
        f = k / (rings + 1)
        cv.d.ellipse([px(cx - rx * f), px(cy - ry * f), px(cx + rx * f), px(cy + ry * f)], outline=RATTAN_DARK,
                     width=px(0.008))
    for k in range(16):
        t = k * math.pi / 8
        cv.d.line([(px(cx), px(cy)), (px(cx + rx * math.cos(t)), px(cy + ry * math.sin(t)))], fill=RATTAN_DARK,
                  width=px(0.006))


def draw_papasan(facing):
    if facing == "west":
        return  # mirrored from east in draw_all(): the chair is symmetric side to side
    """A papasan: a deep round rattan bowl on a drum base, filled with a big
    round cushion (the stuff). The bowl tilts back, so the front view shows the
    cushion as a tipped disc and the side view the bowl's profile."""
    cv = Big(1, 1)
    if facing in ("south", "north"):
        # Drum base.
        cv.ellipse((0.30, 0.72, 0.70, 0.86), RATTAN_DARK, tint=False)
        cv.rect((0.30, 0.66, 0.70, 0.79), RATTAN, tint=False)
        cv.ellipse((0.30, 0.60, 0.70, 0.72), RATTAN_LIT, tint=False)
        if facing == "south":
            # Bowl rim, then the cushion filling it, tipped back towards us.
            cv.ellipse((0.04, 0.06, 0.96, 0.74), RATTAN_DARK, tint=False)
            cv.ellipse((0.06, 0.07, 0.94, 0.72), RATTAN, tint=False)
            cv.ellipse((0.12, 0.12, 0.88, 0.68), WALL)                      # cushion edge
            cv.ellipse((0.14, 0.13, 0.86, 0.64), TOP)                       # cushion face
            cv.ellipse((0.22, 0.17, 0.78, 0.48), TOP_LIT)                   # the soft dome
            cv.ellipse((0.47, 0.37, 0.53, 0.42), SEAM)                      # centre button
        else:
            # From behind: the woven back of the bowl.
            cv.ellipse((0.04, 0.06, 0.96, 0.74), RATTAN_DARK, tint=False)
            cv.ellipse((0.07, 0.08, 0.93, 0.71), RATTAN, tint=False)
            weave(cv, 0.5, 0.395, 0.43, 0.315)
            cv.ellipse((0.10, 0.04, 0.90, 0.20), WALL)                      # cushion peeking over
            cv.ellipse((0.12, 0.05, 0.88, 0.18), TOP)
    else:
        # Side profile, facing east: the bowl tipped back on its base - a tilted
        # ellipse, the cushion a smaller one filling its upper face.
        def tilted(cx, cy, rx, ry, deg, n=48):
            t = math.radians(deg)
            return [(cx + rx * math.cos(a) * math.cos(t) - ry * math.sin(a) * math.sin(t),
                     cy + rx * math.cos(a) * math.sin(t) + ry * math.sin(a) * math.cos(t))
                    for a in (2 * math.pi * k / n for k in range(n))]
        cv.ellipse((0.32, 0.74, 0.68, 0.88), RATTAN_DARK, tint=False)
        cv.rect((0.33, 0.62, 0.67, 0.81), RATTAN, tint=False)
        cv.ellipse((0.32, 0.56, 0.68, 0.68), RATTAN_LIT, tint=False)
        bowl = tilted(0.48, 0.38, 0.44, 0.24, 38)
        cv.poly(bowl, RATTAN, tint=False)
        for k in range(1, 5):                                        # weave rings
            ring_ = tilted(0.48, 0.38, 0.44 * k / 5, 0.24 * k / 5, 38)
            cv.line(ring_ + [ring_[0]], 0.007, RATTAN_DARK, tint=False)
        cushion = tilted(0.44, 0.33, 0.36, 0.13, 38)
        cv.poly(cushion, TOP)
        lit = tilted(0.42, 0.30, 0.26, 0.07, 38)
        cv.poly(lit, TOP_LIT)
    cv.finish(ring=5 * 4)
    cv.save(path("Papasan", facing), path("Papasan", facing, True))


# --- Swings ------------------------------------------------------------------------

def hang(cv, xs, y_top, y_bottom, kind):
    """Ropes (twisted, with a knot) or chains (links) from each end up out of view."""
    for x in xs:
        if kind == "chain":
            y = y_top
            k = 0
            while y < y_bottom:
                w, h = (0.035, 0.05) if k % 2 == 0 else (0.012, 0.05)
                cv.d.ellipse([px(x - w - 0.01), px(y - 0.01), px(x + w + 0.01), px(y + h + 0.01)], outline=BLACK,
                             width=px(0.03))
                cv.d.ellipse([px(x - w), px(y), px(x + w), px(y + h)], outline=CHAIN, width=px(0.014))
                y += 0.04
                k += 1
            cv.md.rectangle([px(x - 0.04), px(y_top), px(x + 0.04), px(y_bottom)], fill=(0, 0, 0))
        else:
            cv.line([(x, y_top), (x, y_bottom)], 0.075, BLACK, tint=False)      # its own outline
            cv.line([(x, y_top), (x, y_bottom)], 0.05, ROPE, tint=False)
            for y in [y_top + k * 0.05 for k in range(int((y_bottom - y_top) / 0.05))]:
                cv.line([(x - 0.017, y), (x + 0.017, y + 0.03)], 0.008, ROPE_DARK, tint=False)
            cv.ellipse((x - 0.05, y_bottom - 0.03, x + 0.05, y_bottom + 0.06), BLACK, tint=False)
            cv.ellipse((x - 0.04, y_bottom - 0.02, x + 0.04, y_bottom + 0.05), ROPE_DARK, tint=False)


def draw_swing(kind, facing):
    """A two-seat hanging swing, 2x1. North/south views are 2 cells wide, east and
    west 2 cells tall. Each style:
      Daybed   - slatted wooden back and scroll arms (stuff) on ropes, cream cushion.
      Rattan   - a curved woven shell (fixed) on chains, tufted cushion (stuff).
      Platform - a flat white-painted platform on ropes, long cushion (stuff).
    """
    wide = facing in ("north", "south")
    cv = Big(2, 1) if wide else Big(1, 2)
    L = 2.0                                           # the swing's length, in cells
    # Frame colours: stuff-tinted for the daybed, fixed otherwise.
    if kind == "Daybed":
        F, F_LIT, F_DARK, ft = TOP, TOP_LIT, WALL_DARK, True
        CU, CU_LIT, CU_DARK, ct = CREAM, CREAM_LIT, CREAM_DARK, False
        rope = "rope"
    elif kind == "Rattan":
        F, F_LIT, F_DARK, ft = RATTAN, RATTAN_LIT, RATTAN_DARK, False
        CU, CU_LIT, CU_DARK, ct = TOP, TOP_LIT, WALL, True
        rope = "chain"
    else:
        F, F_LIT, F_DARK, ft = PAINT, PAINT_LIT, PAINT_DARK, False
        CU, CU_LIT, CU_DARK, ct = TOP, TOP_LIT, WALL, True
        rope = "rope"

    if wide:
        front = facing == "south"
        # Seat platform and cushion, a back along the far side, arms at the ends.
        if kind == "Rattan":
            shell = [(0.08, 0.30), (0.30, 0.18), (1.70, 0.18), (1.92, 0.30), (1.86, 0.74), (1.50, 0.86),
                     (0.50, 0.86), (0.14, 0.74)]
            cv.poly(shell, F, ft)
            cv.line(shell + [shell[0]], 0.03, F_DARK, ft)
            for k in range(1, 9):                                     # the woven bands
                x = 0.1 + k * 0.2
                cv.line([(x, 0.22), (x, 0.82)], 0.012, F_DARK, ft)
        else:
            cv.rect((0.06, 0.62, 1.94, 0.80), F_DARK, ft)            # platform edge
            cv.rect((0.06, 0.58, 1.94, 0.64), F, ft)
        if front:
            if kind == "Daybed":
                cv.rect((0.10, 0.08, 1.90, 0.40), F, ft)              # slatted back
                for k in range(1, 12):
                    x = 0.10 + k * 0.15
                    cv.rect((x - 0.012, 0.12, x + 0.012, 0.38), F_DARK, ft)
                cv.line([(0.10, 0.09), (1.90, 0.09)], 0.035, F_LIT, ft)
            elif kind == "Rattan":
                cv.ellipse((0.20, 0.12, 1.80, 0.46), CU_DARK, ct)     # tufted back cushion
                cv.ellipse((0.22, 0.13, 1.78, 0.42), CU, ct)
                for x in (0.6, 1.0, 1.4):
                    cv.ellipse((x - 0.02, 0.26, x + 0.02, 0.30), SEAM, ct)
            # Fill behind the cushion and pillows, so no gap is left for the
            # outline to fence off.
            cv.rect((0.10, 0.28, 1.90, 0.62), F_DARK if kind == "Daybed" else CU_DARK,
                    ft if kind == "Daybed" else ct)
            # The seat cushion, and pillows leaning on the back.
            cv.rect((0.16, 0.42, 1.84, 0.62), CU, ct)
            cv.rect((0.16, 0.42, 1.84, 0.46), CU_LIT, ct)
            cv.rect((0.16, 0.58, 1.84, 0.62), CU_DARK, ct)
            for x0 in (0.26, 1.42):
                cv.rect((x0, 0.30, x0 + 0.32, 0.48), CU_LIT if kind != "Platform" else WALL, ct)
                cv.rect((x0, 0.44, x0 + 0.32, 0.48), CU_DARK, ct)
            if kind == "Daybed":
                for x in (0.10, 1.90):                                 # scroll arms
                    cv.line([(x, 0.22), (x, 0.60)], 0.06, F, ft)
                    cv.ellipse((x - 0.045, 0.18, x + 0.045, 0.27), F_LIT, ft)
        else:
            # From behind: the back of the back, the cushion just showing over it.
            cv.rect((0.16, 0.24, 1.84, 0.40), CU, ct)
            if kind == "Daybed":
                cv.rect((0.10, 0.36, 1.90, 0.62), F, ft)
                for k in range(1, 12):
                    x = 0.10 + k * 0.15
                    cv.rect((x - 0.012, 0.38, x + 0.012, 0.60), F_DARK, ft)
            elif kind == "Platform":
                cv.rect((0.10, 0.40, 1.90, 0.58), F, ft)
        hangs = [((0.12, 1.88), 0.0, 0.62)]
    else:
        # Side views: the swing seen end-on along its length, front to the right
        # for east. Back on the far (left) side, seat in the middle.
        right = facing == "east"
        bx = (0.08, 0.30) if right else (0.70, 0.92)                  # the back, edge-on
        sx = (0.26, 0.86) if right else (0.14, 0.74)                  # the seat
        if kind == "Rattan":
            cv.ellipse((0.06, 0.06, 0.94, 1.94), F, ft)
            cv.d.ellipse([px(0.06), px(0.06), px(0.94), px(1.94)], outline=F_DARK, width=px(0.03))
            for k in range(1, 9):
                y = 0.1 + k * 0.2
                cv.line([(0.12, y), (0.88, y)], 0.012, F_DARK, ft)
        cv.rect((sx[0], 0.10, sx[1], 1.90), CU, ct)                    # the seat cushion
        cv.rect((sx[0], 0.10, sx[1], 0.16), CU_LIT, ct)
        if kind != "Platform":
            cv.rect((bx[0], 0.10, bx[1], 1.90), F if kind == "Daybed" else CU_DARK, ft if kind == "Daybed" else ct)
        if kind == "Daybed":
            for y0 in (0.06, 1.80):                                    # arms
                cv.rect((0.08, y0, 0.92, y0 + 0.14), F, ft)
                cv.rect((0.08, y0, 0.92, y0 + 0.03), F_LIT, ft)
        if kind == "Platform":
            cv.rect((0.10, 0.06, 0.90, 0.14), F_DARK, ft)
            cv.rect((0.10, 1.86, 0.90, 1.94), F_DARK, ft)
        # Ropes at each end rise straight up: from above, the far end's rope runs
        # a short way up-screen; the near end shows its knot.
        mid = (sx[0] + sx[1]) / 2
        hangs = [((mid,), 0.0, 0.16), ((mid,), 1.80, 1.84)]
    cv.finish(ring=6 * 4)
    # Hung after the outline, so the ropes sit in front with their own edge.
    for xs, y0, y1 in hangs:
        hang(cv, xs, y0, y1, rope)
    cv.save(path(kind, facing), path(kind, facing, True))


def draw_all():
    for d in (SWING_DIR, PAPASAN_DIR):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    for f in FACINGS:
        draw_papasan(f)
        for k in SWINGS:
            draw_swing(k, f)
    for mask in (False, True):
        Image.open(path("Papasan", "east", mask)).transpose(Image.FLIP_LEFT_RIGHT).save(path("Papasan", "west", mask))
