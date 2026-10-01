# Slopkea artwork

Every sprite is drawn from primitives by the scripts here. Nothing is generated and there are
no source PSDs, so the art rebuilds from a clean checkout with nothing but Pillow.

```sh
pip install pillow
python3 Source/Art/draw_sprites.py      # every texture and mask
python3 Source/Art/verify_art.py        # checks the textures against the defs and the C#
python3 Source/Art/make_about_art.py    # About/Preview.png and About/ModIcon.png
python3 Source/Art/contact_sheet.py /tmp/sheet.png   # every variant plus assembled layouts
python3 Source/Art/measure_furniture.py [VFE path]   # style metrics vs Vanilla Furniture Expanded
python3 Source/Art/compare_vfe.py /tmp/cmp.png [VFE path]   # side by side with VFE
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

## Measured against Vanilla Furniture Expanded

Furniture sits beside VFE's in most modlists, so it is measured against VFE's furniture
textures. `measure_furniture.py` scores the grey, stuff-tinted faces of every sprite, and
`compare_vfe.py` renders the two side by side at the same scale and stuff colours. Both need a
VFE checkout.

| | before | after | VFE median | VFE range |
| --- | --- | --- | --- | --- |
| grey face luminance (median) | 228 | 223 | 218 | 83-253 |
| highlight (p90) | 228 | 237 | 245 | 170-255 |
| tonal contrast (std) | 29.2 | 32.5 | 31.8 | 4-56 |
| outline width (% of a cell) | 1.3 | 2.3 | 2.7 | 0-4.6 |
| distinct grey levels | 47 | 84 | 83 | 12-108 |

What the pass changed, all in `Canvas.silhouette`, so every piece got it at once:

* **Outline 4px to 7px at 192px a cell.** Ours was half VFE's weight and vanished at play
  zoom. Thin parts are scaled to match: the chairs 5px, the rug 4px.
* **Rounded outer corners.** VFE rounds every silhouette corner, and square corners were
  what made ours read as boxes.
* **Edge light.** A soft lift towards white just inside up-left-facing edges, and a sink
  towards black inside down-right ones. This is VFE's airbrushed rim, done as tone and not
  as a line. It is what doubled the grey levels.
* **Faces ramp.** A top face puffs up to the light, brightest at the top. This lifts the
  highlights and makes upholstery read soft.
* **Chunkier legs** on the table and desk, and lighter cubby and bookcase interiors.

All of these follow open edges only. The silhouette is padded as carrying on past a joined
side, so a seam between two pieces never gets a rim, a rounded corner or an outline. The
ramp is skipped across north/south joins, where it would repeat per cell as stripes.
`verify_art.py` still checks every joined edge.

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

## Kitchen run and bookcase

These are in `draw_kitchen.py`. They join along their sides like the cube shelving:
`Slopkea_<Cabinet|Sink|Hob>_<facing>_<cw><ccw>` and `Slopkea_Bookcase_<facing>_<cw><ccw>`.
The three kitchen modules join *each other* (`ISlopkeaKitchenModule` in the C#), so a run can
mix them in any order.

* **Stuff is the carcass.** The worktop is a fixed pale stone, and the handles, basin, hob
  and knobs are fixed steel and black glass, all black in the mask.
* **The worktop overhangs,** so it always runs edge to edge. Only the carcass is inset at an
  open end.
* **Doors are recessed panels,** made of tone steps and never outlined. Side views show the
  doors edge-on.
* **The bookcase is drawn empty.** It is vanilla's `Building_Bookcase`, which draws the
  books actually stored in it, in real time, over the case. The subclass only overrides
  `Graphic` with a `Graphic_Multi` per join state. That is why its files are named
  `Slopkea_Bookcase_<cw><ccw>_<facing>` (`Graphic_Multi` appends the facing), and why the
  def is `MapMeshAndRealTime`. `Slopkea_BookendEast` and `Slopkea_BookendNorth` are the
  bookends vanilla stands at the end of a row.

Rotation is the way the **front** faces, as for every Slopkea piece. That is the opposite of
vanilla workbenches, whose rotation is the way the worker faces, so the hob's
`interactionCellOffset` is `(0,0,1)`, which puts the cook at the front.

## Bench, wardrobe, divider and planter

These are in `draw_more.py`. The bench and wardrobe join along their sides like the
shelving. The divider and planter take bit variants like the table.

* **Bench:** it has no front or back, so north draws as south and west as east. Legs stand
  only at open ends.
* **Wardrobe:** two doors per unit, steel knobs (untinted), and a shared carcass wall
  between joined units.
* **Divider:** it follows its joins. An east-west run shows the paper panels face-on, and a
  north-south run is seen edge-on as the frame's top rail, so a corner shows both. The paper
  is untinted, and the frame and lattice take the stuff colour.
* **Planter:** the soil is untinted, and the timber rim runs only round the outside of the
  dragged shape, so the bed reads as one. Furrows sit on fixed fractions of the cell, so they
  line up across cells.

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
