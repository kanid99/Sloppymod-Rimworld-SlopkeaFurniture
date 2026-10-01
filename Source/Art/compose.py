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


def bits_index(cells, cell):
    """Mirror of Neighbors.JoinedBits: N=1, E=2, S=4, W=8 for each joined side."""
    return sum(b for side, b in BITS.items() if step(cell, side) in cells)


def rug_corners(cells, cell):
    """Mirror of Building_SlopkeaRug.CornerBits."""
    from draw_modular import CORNERS
    c = 0
    for s1, s2, bit in CORNERS.values():
        a, b = step(cell, s1), step(cell, s2)
        diag = step(a, s2)
        if a in cells and b in cells and diag not in cells:
            c |= bit
    return c


def shelf_states(scene, cell):
    """Mirror of Building_SlopkeaShelf.SideState, for (cw, ccw)."""
    facing = scene[cell][1]
    out = []
    for side in (CW[facing], CCW[facing]):
        n = scene.get(step(cell, side))
        out.append("j" if n and n[0] == "shelf" and n[1] == facing else "o")
    return tuple(out)


def render(scene, colors, size, cell_px=CELL, bg=(92, 84, 72), rugs=()):
    """scene: {(x, z): ("table",) | ("desk",) | ("sect", facing) | ("shelf", facing)},
    z up; rugs: a set of cells, drawn underneath. size in cells."""
    from draw_modular import desk_path, rug_path, shelf_path
    w, h = size
    out = Image.new("RGBA", (w * cell_px, h * cell_px), bg + (255,))
    rugs = set(rugs)
    tiles = [((x, z), tinted(rug_path(bits_index(rugs, (x, z)), rug_corners(rugs, (x, z))),
                             colors.get("rug", (160, 60, 50)))) for x, z in rugs]
    same = lambda kind: {c for c, t in scene.items() if t[0] == kind}
    for (x, z), thing in scene.items():
        if thing[0] == "table":
            tile = tinted(table_path(table_index(scene, (x, z))), colors["table"])
        elif thing[0] == "desk":
            i = bits_index(same("desk"), (x, z))
            tile = tinted(desk_path(i), colors.get("desk", (235, 232, 222)), desk_path(i, True))
        elif thing[0] in ("Cabinet", "Sink", "Hob", "book"):
            from draw_kitchen import book_path, kitchen_path
            kitchen = ("Cabinet", "Sink", "Hob")
            st = []
            for side in (CW[thing[1]], CCW[thing[1]]):
                n = scene.get(step((x, z), side))
                ok = n and n[1] == thing[1] and ((n[0] in kitchen) if thing[0] in kitchen else n[0] == thing[0])
                st.append("j" if ok else "o")
            if thing[0] == "book":
                p, m = book_path(thing[1], *st), book_path(thing[1], *st, mask=True)
            else:
                p, m = kitchen_path(thing[0], thing[1], *st), kitchen_path(thing[0], thing[1], *st, mask=True)
            tile = tinted(p, colors.get(thing[0], (235, 232, 222)), m)
        elif thing[0] in ("Bench", "Wardrobe"):
            from draw_more import side_path
            st = []
            for side in (CW[thing[1]], CCW[thing[1]]):
                n = scene.get(step((x, z), side))
                st.append("j" if n and n[0] == thing[0] and n[1] == thing[1] else "o")
            tile = tinted(side_path(thing[0], thing[1], *st), colors.get(thing[0], (200, 160, 110)),
                          side_path(thing[0], thing[1], *st, mask=True))
        elif thing[0] in ("divider", "planter"):
            from draw_more import divider_path, planter_path
            fn = divider_path if thing[0] == "divider" else planter_path
            i = bits_index(same(thing[0]), (x, z))
            tile = tinted(fn(i), colors.get(thing[0], (170, 120, 80)), fn(i, True))
        elif thing[0] == "shelf":
            cw, ccw = shelf_states(scene, (x, z))
            tile = tinted(shelf_path(thing[1], cw, ccw), colors.get("shelf", (240, 240, 236)),
                          shelf_path(thing[1], cw, ccw, True))
        else:
            cw, ccw = sectional_states(scene, (x, z))
            tile = tinted(sect_path(thing[1], cw, ccw), colors["sect"],
                          sect_path(thing[1], cw, ccw, mask=True))
        tiles.append(((x, z), tile))
    for (x, z), tile in tiles:
        if cell_px != CELL:
            tile = tile.resize((cell_px, cell_px), Image.LANCZOS)
        out.alpha_composite(tile, (x * cell_px, (h - 1 - z) * cell_px))
    return out
