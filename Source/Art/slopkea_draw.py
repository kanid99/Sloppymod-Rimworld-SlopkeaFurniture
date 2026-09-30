"""Shared primitives for the Slopkea sprites.

The rules are the SloppyMods ones (see the mending, Riimba and TrashPower
Source/Art/README.md): drawn from primitives, black only on the silhouette,
height as a lit top face over a darker wall, views rather than rotated pixels,
supersampled 4x and reduced with LANCZOS.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

CELL = 192          # final pixels per cell, as the other SloppyMods furniture
SS = 4              # supersample factor
C = CELL * SS       # working canvas per cell
RING = 4 * SS       # silhouette ring width (4px final)
LIFT = 0.55         # how far one cell of height rises up the screen

# Stuff-tinted tones. RimWorld multiplies these by the stuff colour, so they are
# light neutral greys; depth is the step between them, never an outline.
TOP_LIT = (246, 246, 246)
TOP = (228, 228, 228)
SEAM = (196, 196, 196)
WALL = (162, 162, 162)
WALL_DARK = (128, 128, 128)
SHADOW = (0, 0, 0, 70)
BLACK = (0, 0, 0)

# Untinted parts keep their own colour (black in the mask).
FOOT = (46, 42, 40)

# Screen directions, x right and y DOWN: map z runs up, so north is the TOP.
DIRS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def px(v):
    return int(round(v * C))


class Canvas:
    """One cell, supersampled, with a parallel stuff mask."""

    def __init__(self):
        self.img = Image.new("RGBA", (C, C), (0, 0, 0, 0))
        self.mask = Image.new("RGB", (C, C), (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.md = ImageDraw.Draw(self.mask)

    def rect(self, r, fill, tint=True):
        x0, y0, x1, y1 = r
        box = [px(x0), px(y0), px(x1) - 1, px(y1) - 1]
        if box[2] < box[0] or box[3] < box[1]:
            return
        self.d.rectangle(box, fill=fill)
        self.md.rectangle(box, fill=(255, 0, 0) if tint else (0, 0, 0))

    def soft_shadow(self, r, off=(0.02, 0.03)):
        """Cast shadow down and right, soft, drawn before the part that casts it."""
        layer = Image.new("RGBA", (C, C), (0, 0, 0, 0))
        x0, y0, x1, y1 = r
        ImageDraw.Draw(layer).rectangle(
            [px(x0 + off[0]), px(y0 + off[1]), px(x1 + off[0]), px(y1 + off[1])], fill=SHADOW)
        layer = layer.filter(ImageFilter.GaussianBlur(3 * SS))
        # Only onto what is already there: a shadow never makes new silhouette.
        a = ImageChops.multiply(layer.getchannel("A"), self.img.getchannel("A"))
        layer.putalpha(a)
        self.img.alpha_composite(layer)

    def slab(self, r, h, face=TOP, wall=WALL, joined=()):
        """A raised part: lit top face over a darker wall LIFT*h deep, lit lip on top.

        `joined` lists the screen sides where this part runs on into the same part
        of the next piece. There is no wall or lip on those: the face carries
        straight across the seam, so a backrest or a seat reads as one run.
        """
        x0, y0, x1, y1 = r
        wall_h = 0 if "south" in joined else min(LIFT * h, (y1 - y0) * 0.6)
        self.soft_shadow(r)
        if wall_h:
            self.rect((x0, y1 - wall_h, x1, y1), wall)
            self.rect((x0, y1 - wall_h, x1, y1 - wall_h + 0.006), WALL_DARK)
        self.rect((x0, y0, x1, y1 - wall_h), face)
        if "north" not in joined:
            self.rect((x0, y0, x1, y0 + 0.012), TOP_LIT)

    def silhouette(self, open_sides):
        """Black ring on the outer silhouette only.

        Joined sides continue into the neighbouring cell, so the canvas is padded
        with opaque there and transparent on open sides before eroding: the ring
        then follows open edges and gaps, never a seam between two pieces.
        """
        a = self.img.getchannel("A").point(lambda v: 255 if v > 127 else 0)
        pad = Image.new("L", (C + 2 * RING, C + 2 * RING), 0)
        pad.paste(a, (RING, RING))
        pd = ImageDraw.Draw(pad)
        full = C + 2 * RING - 1
        if "north" not in open_sides:
            pd.rectangle([RING, 0, RING + C - 1, RING - 1], fill=255)
        if "south" not in open_sides:
            pd.rectangle([RING, RING + C, RING + C - 1, full], fill=255)
        if "west" not in open_sides:
            pd.rectangle([0, RING, RING - 1, RING + C - 1], fill=255)
        if "east" not in open_sides:
            pd.rectangle([RING + C, RING, full, RING + C - 1], fill=255)
        # Corners between two joined sides are solid too (a 2x2 block has no hole).
        for v, hz, box in (("north", "west", [0, 0, RING - 1, RING - 1]),
                           ("north", "east", [RING + C, 0, full, RING - 1]),
                           ("south", "west", [0, RING + C, RING - 1, full]),
                           ("south", "east", [RING + C, RING + C, full, full])):
            if v not in open_sides and hz not in open_sides:
                pd.rectangle(box, fill=255)
        er = pad
        for _ in range(RING):
            er = er.filter(ImageFilter.MinFilter(3))
        er = er.crop((RING, RING, RING + C, RING + C))
        ring = ImageChops.subtract(a, er)
        black = Image.new("RGBA", (C, C), BLACK + (255,))
        self.img.paste(black, (0, 0), ring)

    def save(self, path, mask_path=None):
        self.img.resize((CELL, CELL), Image.LANCZOS).save(path)
        if mask_path:
            self.mask.resize((CELL, CELL), Image.LANCZOS).save(mask_path)


def local_rect(facing, a0, a1, f0, f1):
    """Map a rect in a seat's own frame to screen fractions for one view.

    a runs across the seat from its counter-clockwise side (0) to its clockwise
    side (1); f runs from the front edge (0) to the back edge (1). The layout is
    placed per view; pixels are never rotated, so the light stays at the top.
    """
    fx, fy = DIRS[facing]
    cx, cy = DIRS[CW[facing]]
    pts = []
    for a in (a0, a1):
        for f in (f0, f1):
            pts.append((0.5 + cx * (a - 0.5) + fx * (0.5 - f),
                        0.5 + cy * (a - 0.5) + fy * (0.5 - f)))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))
