"""Lays out a scene the way the game would: picks each cell's variant with the
same neighbour rules as the C# and tints it with a stuff colour through its mask.
Used by the contact sheet, the store art and verify_art.py."""
from PIL import Image, ImageChops

from draw_sprites import BITS, sect_path, table_path
from slopkea_draw import CELL, CW, CCW, DIRS, OPP

# Screen dir -> map offset: map z runs UP, so screen y is negated.
def step(cell, side):
    dx, dy = DIRS[side]
    return (cell[0] + dx, cell[1] - dy)


def table_index(scene, cell):
    """Mirror of Building_SlopkeaTable.VariantIndex."""
    return sum(b for s, b in BITS.items() if scene.get(step(cell, s), ("",))[0] == "table")


def sectional_states(scene, cell):
    """Mirror of Building_SlopkeaSectional.SideState, for (cw, ccw)."""
    facing = scene[cell][1]
    front = scene.get(step(cell, facing))
    out = []
    for side in (CW[facing], CCW[facing]):
        n = scene.get(step(cell, side))
        if n and n[0] == "sect":
            out.append("j")
        elif front and front[0] == "sect" and front[1] == OPP[side]:
            out.append("c")
        else:
            out.append("a")
    return tuple(out)


def tinted(path, color, mask_path=None):
    im = Image.open(path).convert("RGBA")
    tint = Image.new("RGBA", im.size, color + (255,))
    mult = ImageChops.multiply(im, tint)
    if mask_path:
        m = Image.open(mask_path).convert("RGB").getchannel("R")
        mult = Image.composite(mult, im, m)
    mult.putalpha(im.getchannel("A"))
    return mult


def render(scene, colors, size, cell_px=CELL, bg=(92, 84, 72)):
    """scene: {(x, z): ("table",) | ("sect", facing)}, z up. size in cells."""
    w, h = size
    out = Image.new("RGBA", (w * cell_px, h * cell_px), bg + (255,))
    for (x, z), thing in scene.items():
        if thing[0] == "table":
            tile = tinted(table_path(table_index(scene, (x, z))), colors["table"])
        else:
            cw, ccw = sectional_states(scene, (x, z))
            tile = tinted(sect_path(thing[1], cw, ccw), colors["sect"],
                          sect_path(thing[1], cw, ccw, mask=True))
        if cell_px != CELL:
            tile = tile.resize((cell_px, cell_px), Image.LANCZOS)
        out.alpha_composite(tile, (x * cell_px, (h - 1 - z) * cell_px))
    return out
