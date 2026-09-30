# Slopkea artwork

Every sprite is drawn from primitives by the scripts here. Nothing is generated and there are
no source PSDs, so the art rebuilds from a clean checkout with nothing but Pillow.

```sh
pip install pillow
python3 Source/Art/draw_sprites.py      # every texture and mask
python3 Source/Art/verify_art.py        # checks the textures against the defs and the C#
python3 Source/Art/make_about_art.py    # About/Preview.png and About/ModIcon.png
python3 Source/Art/contact_sheet.py /tmp/sheet.png   # every variant plus assembled layouts
```

All run from the repo root. The rules are the SloppyMods ones settled in the mending, Riimba
and TrashPower art (see their `Source/Art/README.md`):

* **Drawn, not generated.**
* **Black is the silhouette and nothing else.** Plank seams, cushion seams and tufting are a
  tone step, never an outline.
* **Height is a wall, not an outline.** A raised part is a lit top face over a darker wall
  `LIFT * h` deep, with a soft shadow down and right.
* **Rotations are views, not rotations.** Each sectional seat is laid out once in its own frame
  (`a` across, `f` front to back) and `local_rect` places it for each facing. Pixels are never
  rotated, and the C# prints the plane unrotated, so the light stays at the top of the screen.
* **Stuffable means masked.** Tintable parts are light neutral greys, which the stuff colour
  multiplies. The sectional's feet stay dark whatever it is built from, so it has masks. A
  `Graphic_Single` mask is `<name>_m.png`, and a `Graphic_Multi` mask is `<name>_<rot>m.png`
  with no underscore. The table is stuff all the way through, so it uses `Cutout` and has no mask.
* **Supersampled** at 4x and reduced with LANCZOS. One cell is 192px.

## Pieces that join up are drawn as variants

A building's texture is baked into the map mesh, so the joins cannot be overlays turned on the
fly. Each piece is drawn as every per-cell variant instead, and the C# picks one from its
neighbours.

* **Table:** `Slopkea_Table_<i>`, where `i` has a bit set for each side joined to another
  segment: N=1, E=2, S=4, W=8 (the TrashPower pipe atlas order). The rim and silhouette sit
  only on open sides. The apron (the table's wall) shows only on an open south side, and legs
  only at outside corners. Plank seams sit on fixed fractions of the cell, so they line up
  across cells.
* **Sectional:** `Slopkea_Sectional_<facing>_<cw><ccw>`, with each side `a` (armrest),
  `j` (joined to the next seat) or `c` (corner: the seat in front has its back to this side,
  so the backrest wraps round). A corner seat's front runs on into that perpendicular seat.
* **Joins carry straight across.** `slab(..., joined=)` drops the wall and the lit lip on any
  side where a part runs on into the same part of the next piece. That keeps the backrest one
  band all the way round an L or U, and the seating one unbroken surface inside it.

## Rocking chairs

Free-standing, so one view per facing and no variants: `Slopkea_RockingChair<Wood|Cloth>_<rot>`.
Two runners run past the seat front and back, each tapering over its last tenth at both ends
so it reads as a curve lifting off the floor. The wooden chair is all stuff (slats and
spindles as identical marks). The cloth chair's stuff is the upholstery only: its frame is a
fixed oak, black in the mask, so `verify_art.py` checks the tinted share is upholstery-sized.

The rocking is not in the art. `Building_SlopkeaRockingChair` is drawn in real time and eases
the whole sprite back and forth along its facing while someone sits in it.

## The contract with the C#

`verify_art.py` checks:

* every variant and mask exists at 192x192;
* every open side carries the silhouette ring, and no joined side has any black on it;
* the edges that meet across a join match in tone;
* each def's texPath resolves, including the `Graphic_Multi` masks;
* the `TexPrefix` in each C# class is the path the art is written to, and the sectional's
  facing names are in `Rot4` order.

`compose.py` mirrors `Building_SlopkeaTable.VariantIndex` and
`Building_SlopkeaSectional.SideState`, so the contact sheet and store art are laid out by the
same rules as the game.

## Sizes

| texture | size | why |
| --- | --- | --- |
| `Slopkea_Table_0..15` | 192x192 | 1x1 at `drawSize (1,1)`; `_0` is the def graphic |
| `Slopkea_Sectional_<facing>_<cw><ccw>` (+`_m`) | 192x192 | 36 variants and masks |
| `Slopkea_Sectional_<rot>` (+`m`) | 192x192 | the free-standing seat, as the def's `Graphic_Multi` |
| `Slopkea_RockingChair<Wood/Cloth>_<rot>` | 192x192 | 1x1; the cloth chair has `<rot>m` masks |
| `About/Preview.png` | 640x360 | composited from the shipped textures |
| `About/ModIcon.png` | 256x256 | one sectional corner, which still reads at 32px |
