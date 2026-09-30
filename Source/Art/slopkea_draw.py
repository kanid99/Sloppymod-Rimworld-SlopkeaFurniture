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
RING = 7 * SS       # silhouette ring width (7px final: VFE's outline is ~2.7% of a cell)
LIFT = 0.55         # how far one cell of height rises up the screen

# Stuff-tinted tones. RimWorld multiplies these by the stuff colour, so they are
# light neutral greys; depth is the step between them, never an outline.
TOP_LIT = (252, 252, 252)
TOP = (236, 236, 236)
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

    def _pts(self, pts):
        return [(px(x), px(y)) for x, y in pts]

    def poly(self, pts, fill, tint=True):
        self.d.polygon(self._pts(pts), fill=fill)
        self.md.polygon(self._pts(pts), fill=(255, 0, 0) if tint else (0, 0, 0))

    def line(self, pts, width, fill, tint=True):
        """A thick stroke with round joints and round ends."""
        w = px(width)
        p = self._pts(pts)
        for d, f in ((self.d, fill), (self.md, (255, 0, 0) if tint else (0, 0, 0))):
            d.line(p, fill=f, width=w, joint="curve")
            for x, y in (p[0], p[-1]):
                d.ellipse([x - w // 2, y - w // 2, x + w // 2, y + w // 2], fill=f)

    def ellipse(self, r, fill, tint=True):
        box = [px(r[0]), px(r[1]), px(r[2]), px(r[3])]
        self.d.ellipse(box, fill=fill)
        self.md.ellipse(box, fill=(255, 0, 0) if tint else (0, 0, 0))

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

    def ramp(self, r, c_top, c_bottom, tint=True):
        """A vertical ramp, one row per supersampled pixel."""
        x0, y0, x1, y1 = (px(v) for v in r)
        n = max(1, y1 - y0)
        for k in range(n):
            f = k / n
            c = tuple(int(a + (b - a) * f) for a, b in zip(c_top, c_bottom))
            self.d.line([(x0, y0 + k), (x1 - 1, y0 + k)], fill=c)
        self.md.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(255, 0, 0) if tint else (0, 0, 0))

    def slab(self, r, h, face=TOP, wall=WALL, joined=(), tint=True, lit=TOP_LIT, wall_dark=WALL_DARK):
        """A raised part: lit top face over a darker wall LIFT*h deep, lit lip on top.

        `joined` lists the screen sides where this part runs on into the same part
        of the next piece. There is no wall or lip on those: the face carries
        straight across the seam, so a backrest or a seat reads as one run.
        """
        x0, y0, x1, y1 = r
        wall_h = 0 if "south" in joined else min(LIFT * h, (y1 - y0) * 0.6)
        self.soft_shadow(r)
        if wall_h:
            self.rect((x0, y1 - wall_h, x1, y1), wall, tint)
            self.rect((x0, y1 - wall_h, x1, y1 - wall_h + 0.006), wall_dark, tint)
        if face == TOP and "north" not in joined and "south" not in joined:
            # Upholstery and tops puff up to the light: a soft ramp down the face,
            # brightest at the top - VFE's pillowy shading, as tone. Not across a
            # north/south join, where it would repeat per cell as stripes.
            self.ramp((x0, y0, x1, y1 - wall_h), TOP_LIT, face, tint)
        else:
            self.rect((x0, y0, x1, y1 - wall_h), face, tint)
        if "north" not in joined:
            self.rect((x0, y0, x1, y0 + 0.012), lit, tint)

    def _padded_alpha(self, open_sides, pad):
        """The silhouette, padded by `pad` px: opaque past joined sides (they carry
        on into the neighbour), transparent past open ones. Every silhouette effect
        works on this, so none of them ever marks a seam between two pieces."""
        a = self.img.getchannel("A").point(lambda v: 255 if v > 127 else 0)
        P = Image.new("L", (C + 2 * pad, C + 2 * pad), 0)
        P.paste(a, (pad, pad))
        d = ImageDraw.Draw(P)
        full = C + 2 * pad - 1
        boxes = {"north": [pad, 0, pad + C - 1, pad - 1], "south": [pad, pad + C, pad + C - 1, full],
                 "west": [0, pad, pad - 1, pad + C - 1], "east": [pad + C, pad, full, pad + C - 1]}
        for side, box in boxes.items():
            if side not in open_sides:
                # Carry the silhouette's own edge on, not a solid block: a joined
                # side continues whatever touches that edge (a gap between legs
                # stays a gap).
                edge = {"north": (0, 0, C, 1), "south": (0, C - 1, C, C),
                        "west": (0, 0, 1, C), "east": (C - 1, 0, C, C)}[side]
                strip = a.crop(edge).resize((box[2] - box[0] + 1, box[3] - box[1] + 1))
                P.paste(strip, (box[0], box[1]))
        # Corners between two joined sides are solid too (a 2x2 block has no hole).
        for v, hz, box in (("north", "west", [0, 0, pad - 1, pad - 1]),
                           ("north", "east", [pad + C, 0, full, pad - 1]),
                           ("south", "west", [0, pad + C, pad - 1, full]),
                           ("south", "east", [pad + C, pad + C, full, full])):
            if v not in open_sides and hz not in open_sides:
                d.rectangle(box, fill=255)
        return a, P

    def silhouette(self, open_sides, ring=RING):
        """Finish a sprite against its silhouette, in the order VFE's furniture
        reads: rounded outer corners, soft light on the upper-left edges and shade
        on the lower-right, then the black ring. All three follow OPEN edges and
        gaps only; joined sides are padded as carrying on, so seams stay clean.
        """
        pad = int(0.2 * C)
        a, P = self._padded_alpha(open_sides, pad)
        crop = lambda im: im.crop((pad, pad, pad + C, pad + C))

        # 1. Round the outer corners: blur and re-threshold the padded silhouette.
        # Only ever removes pixels, and a joined side is flat, so it stays square.
        rounded = crop(P.filter(ImageFilter.GaussianBlur(int(0.035 * C))).point(
            lambda v: 255 if v > 150 else 0))
        cut = ImageChops.subtract(a, rounded)
        if cut.getbbox():
            clear = Image.new("RGBA", (C, C), (0, 0, 0, 0))
            self.img.paste(clear, (0, 0), cut)
            self.mask.paste((0, 0, 0), (0, 0), cut)
            a = ImageChops.multiply(a, rounded)
            _, P = self._padded_alpha(open_sides, pad)

        # 2. Edge light: inside the silhouette, near an edge that faces up-left,
        # lift towards white; near one facing down-right, sink towards black.
        # Soft, a tenth of a cell deep - VFE's airbrushed rim, as tone not line.
        dd = int(0.10 * C)
        blur = ImageFilter.GaussianBlur(int(0.05 * C))
        up_left = P.transform(P.size, Image.AFFINE, (1, 0, -dd, 0, 1, -dd))     # P(x-d, y-d)
        down_right = P.transform(P.size, Image.AFFINE, (1, 0, dd, 0, 1, dd))    # P(x+d, y+d)
        inv = lambda im: im.point(lambda v: 255 - v)
        light = crop(ImageChops.multiply(P, inv(up_left)).filter(blur))
        shade = crop(ImageChops.multiply(P, inv(down_right)).filter(blur))
        light = ImageChops.multiply(light, a).point(lambda v: int(v * 0.30))
        shade = ImageChops.multiply(shade, a).point(lambda v: int(v * 0.22))
        rgb = self.img.convert("RGB")
        rgb = Image.composite(Image.new("RGB", (C, C), (255, 255, 255)), rgb, light)
        rgb = Image.composite(Image.new("RGB", (C, C), (0, 0, 0)), rgb, shade)
        rgb.putalpha(self.img.getchannel("A"))
        self.img = rgb
        self.d = ImageDraw.Draw(self.img)

        # 3. The black ring.
        er = P
        for _ in range(ring):
            er = er.filter(ImageFilter.MinFilter(3))
        ring_px = ImageChops.subtract(a, crop(er))
        black = Image.new("RGBA", (C, C), BLACK + (255,))
        self.img.paste(black, (0, 0), ring_px)

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
