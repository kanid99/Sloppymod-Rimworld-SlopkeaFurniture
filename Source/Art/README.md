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
`Slopkea_RockingChair<Wood|Cloth>_<rot>`. West is east mirrored, because both chairs are
symmetric side to side.

**They are drawn in three-quarter elevation, like vanilla furniture, not as a floor plan.**
From straight above, a rocking chair is just a box.

### Wooden: spindle-back rocker

All stuff. What makes it a rocker is the curved runners, so every view is built round them.

* **East:** the runner is a smile, low in the middle with both ends lifting off the floor.
* **South and north:** the runners are two long skids running past the chair at both ends.
  They widen towards the viewer, and each end rolls up off the floor. The legs stand on the
  runners and the arms tie into the back posts. The back rises over the seat, with spindles
  against a shaded panel. The panel runs up under the crest rail, so no enclosed gap is left
  for the silhouette to fill black.

### Cloth: glider rocker

The owner's reference is a nursery glider. It is overstuffed: a tall back in channel-tufted
pillows, pillow arm pads and a thick seat cushion, all in the stuff colour. The frame is
**white paint**, black in the mask, with wide flat arm panels. It stands on a **flat base with
glide links**, and has no curved runners. `pillow()` draws one channel: a rounded pad, lit on
top and shaded underneath.

### Motion

The motion is not in the art. `Building_SlopkeaRockingChair` is drawn in real time while
someone sits in it.

* **Wooden:** tilts up to 4 degrees on its runners in the side views, and slides along its
  facing in the front and back views.
* **Glider:** `Building_SlopkeaGlider` only ever slides, because that is what a glider does.

Parts are round-ended strokes (`Canvas.line`) and polygons. The silhouette ring is 3px here,
so the thin turned parts keep some colour inside their outline. `verify_art.py` checks that the
glider's tinted share is upholstery-sized.

## Desk, rug and cube shelving

Built on the same join scheme, in `draw_modular.py`:

* **Desk:** `Slopkea_Desk_<bits>`, in the table's bit order. It is a smooth slab, not
  planks. A light edge band runs round every open edge, and slim steel legs sit at the
  outside corners only. The legs are untinted, so the desk has `_m` masks.
* **Rug:** `Slopkea_Rug_<bits>_<corners>`. It is flat, so there is no wall, and the
  silhouette is 2px. The border runs along open sides. An **inside corner** (both sides
  joined, diagonal empty) also needs the border turning inside this cell, which the side bits
  alone cannot say. So there are four corner bits: NE=1, SE=2, SW=4, NW=8. Only the 47
  combinations whose corners have both sides joined are drawn.
* **Cube shelving:** `Slopkea_Shelf_<facing>_<cw><ccw>`, each side `o` (open) or `j` (joined).
  Units join only to a neighbour facing the same way. A joined side has half a wall, so a run
  shows shared walls. South shows the two cubes, north the plain back, and east and west the
  top with the open front edge-on.

The joined-edge check looks for an outline running *along* a joined edge: a black run of 12px
or more. An outline *crossing* the edge is legitimate, like the bottom of the desk's front
band. Painting a black strip down a joined edge makes it fail, which is how the check itself
was tested.

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
