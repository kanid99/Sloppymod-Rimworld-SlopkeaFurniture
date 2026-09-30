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

Free-standing, so they have one view per facing and no variants:
`Slopkea_RockingChair<Wood|Cloth>_<rot>`.

**They are drawn in elevation, not as a floor plan.** From straight above, a rocking chair is
a box with two sticks beside it, and the first version read exactly like that. What makes it a
rocking chair is the curved runner and the tall back, so each view is built to show them.
Vanilla furniture takes the same three-quarter view.

* **East:** side profile, and the view that sells it. The runner is a smile, low in the middle
  with both ends lifting off the floor. The legs stand on it, and the back post leans back
  to a round crest.
* **South:** from the front. The tall back rises above the seat, with spindles on the wooden
  chair and a tufted pad on the cloth one. The runners come towards us under it and end in
  curled tips.
* **North:** from behind. The back of the backrest is nearest and rises up the screen, and the
  runners run out past it at both ends.
* **West:** east mirrored, because the chair is symmetric side to side.

Parts are round-ended strokes (`Canvas.line`) rather than slabs, and the silhouette ring is
3px here rather than 4px, so the thin turned parts keep some wood inside their outline.

The wooden chair is all stuff. On the cloth chair, the stuff is only the upholstery: the frame
is a fixed oak, black in the mask. `verify_art.py` checks that the tinted share is
upholstery-sized. It is 15-80% because a side view shows less pad.

**The rocking is not in the art.** `Building_SlopkeaRockingChair` is drawn in real time while
someone sits in it. In the side views it tilts the sprite up to 4 degrees on its runner. The
front and back views cannot show a tilt, so there it eases back and forth along its facing.

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
