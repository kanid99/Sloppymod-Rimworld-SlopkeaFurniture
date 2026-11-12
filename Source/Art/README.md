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
  what made ours read as boxes. *Since narrowed:* against vanilla's own tables, benches and
  bookcase, hard furniture is nearly square, so everything built of boards now passes
  `corner=CORNER` (0.012 of a cell, `slopkea_units.py`). Only upholstery, the rug, the woven
  rattan swing and the chairs keep the soft 0.035 corner.
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

* **Inside corners turn the outline.** In an L, the corner seat has both its front and its
  run side joined, but the cell diagonally inside the L is empty, and the two seats either
  side stop a little short of their cell edges. The corner seat is cut back to where those
  two fronts cross and outlined against its real neighbours: `silhouette(..., context=,
  empty_diagonals=)` takes the finished silhouettes of the two run seats (`run_alpha`), so
  the ring turns inside the corner seat and runs pixel for pixel into theirs. Nothing is
  restated as a number. `verify_art.py` assembles every L and fails if any tinted pixel
  touches the floor at the inside corner.

* **The table, desk and planter turn inside corners too.** Their side bits cannot say that
  the cell diagonally inside an L is empty, so a cell there gets a second number, the rug's
  scheme: NE=1, SE=2, SW=4, NW=8, written `<sides>_<corners>` (`variant_name`; the plain
  `<sides>` names are unchanged). `inside_corner_outline` (`slopkea_units.py`) outlines the
  corner cell against its two real neighbours, and the planter's rim turns there as well.
  The C# picks the name with `Neighbors.ShapeVariant`. 31 extra variants per piece.

* **Cushions part with a crease, not a line.** Between two joined seats the cushion is shaded
  towards the cell edge (`crease`, 0.045 of a cell deep, 15% at the edge), half from each seat.
  It was a hard seam on the boundary, which marked every cell of a run.

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

* **Seen from above, like vanilla's benches.** The counters are laid out off vanilla's
  electric stove (`TableStoveElectric`, 224x96 for 3x1): the worktop covers the cell in every
  facing, about 0.85 of a cell deep, and the bench's height shows as one strip about 0.13 of
  a cell tall along the screen-bottom edge only - the south face, whichever way it faces.
  There is no door elevation: that was what made the counters read as half-depth.
* **Stuff is the carcass:** the strip under the worktop, and the doors' top edge along the
  front in the east and west views. The worktop is a fixed pale stone, and the basin, tap,
  hob plate and knobs are fixed steel, all black in the mask.
* **Nothing sits on a cell boundary.** Door gaps fall every half cell, the same on a boundary
  as inside a module, so a run reads as one counter.
* **Fittings are never squashed.** The hob is a steel plate with four ringed burners, each
  about 0.3 of a cell across, with its controls along the plate's front; the sink's tap is at
  the back. Only those swap ends between facings.
* **Nearly square corners** (`silhouette(corner=0.012)`), as vanilla's benches have.
* **Tall units follow the same rule** (`slopkea_units.py`): hutch, wall oven and fridge are
  seen from above, with a taller strip (0.22 of a cell) because they are taller. The front is
  on that strip only when the unit faces south; facing north it is the plain back, and facing
  east or west the front is a band down that side.
* The wall cabinets are still drawn the old way (door fronts when facing south).

## One projection for storage

The wardrobe, cube shelving and bookcase use `slopkea_units.py` too, so every facing of a
piece is the same view: top covering the cell, the camera-side face as a strip along the
screen-bottom edge, square corners (`CORNER`). Before, their south view was a front
elevation and the other three were tops, so a piece changed projection when rotated. The
bookcase is laid out like vanilla's one-cell `BookcaseSmall` (frame, shadowed recess, pale
shelf floor, face strip), since vanilla's code draws the books over it.
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
  is untinted, and the frame and lattice take the stuff colour. Where the run turns in a cell (a north or south join and
  only one of east and west) the face-on part is half a cell, one panel hinged on the centre
  post, so the corner meets the edge-on rail instead of sticking out half a cell past it.
* **Planter:** the soil is untinted, and the timber rim runs only round the outside of the
  dragged shape, so the bed reads as one. Furrows sit on fixed fractions of the cell, so they
  line up across cells.

## Conversation pit

`draw_pit.py`. RimWorld can't lower the ground, so the pit is an illusion built from
three cues:

* **The floor** (`Slopkea_Pit_<sides>_<corners>`, rug-style joins): sunken carpet that
  darkens towards its walls. Round the outside of the shape run the rim and the step-down
  walls. The far wall shows its whole face, the side walls show a sliver, and the near wall
  shows only its rim, as you'd see them looking down into a pit. The walls cast shadows onto
  the carpet, and inside corners turn the far wall's face.
* **The seats** (`Slopkea_PitSeat_...`) are the sectional drawn built in: no plinth or feet,
  and the room's rim runs along their back and open ends, above the cushions.
* **No outline round the outside.** The rim is the room floor, so the edge is where it
  falls away: `drop_edge` draws a dark line on the rim's inner edge and a soft shadow below
  it. An outline round the outside would fence the pit off like a raised object.

The rim and walls are untinted plaster, and the carpet and seats take the stuff colour.

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
