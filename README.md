# Slopkea Furniture

Flat-pack, IKEA-inspired furniture for RimWorld 1.6. Some assembly required.

## Furniture
- **Everything is stuffable.** All Slopkea pieces inherit `SlopkeaFurnitureBase` and take stuff.
- **BÖRKSTÅD sectional seat** – 1x1 rotatable seats (fabric, leather, wood, metal, stone). Drag a line of them; backrests follow facing, armrests appear at open ends, and a seat whose front neighbour turns 90° gets a wrap-around corner backrest. Sittable, so they work as dining chairs.
- **GUNGVIK rocking chairs** – a spindle-back wooden rocker on curved runners (any wood), which tips on its runners while someone sits in it; and an overstuffed glider rocker (fabric or leather over a white painted frame, plus 25 wood), which glides back and forth.
- **LÅNGBORD desk segment** – drag out any desk shape; every cell is a research bench worked from its front.
- **KUBBLÅ cube shelf** – rotatable storage, two stacks per unit; units facing the same way join into one run.
- **MATTBIT rug segment** – drag out any rug shape; the border follows the outline, and furniture stands on it.
- **SKÅPKÖK kitchen run** – cabinet (stores food), sink (room cleanliness) and hob (electric stove; cooks everything the vanilla electric stove does, via `Patches/Slopkea_HobRecipes.xml`). Any modules facing the same way join into one counter.
- **HYLLVIK bookcase** – a vanilla bookcase (`Building_Bookcase`: holds, shows and lends out books, reading bonus) with empty shelves; vanilla fills them with whatever books are stored. Units facing the same way join into a run.
- **BÄNKLAG bench** – backless seating; benches facing the same way join into one pew.
- **GARDEROB wardrobe** – apparel storage, three stacks per unit; joins into a fitted run.
- **VIKSKÄRM room divider** – drag a line of paper screen (it turns corners); blocks line of sight, passable.
- **ODLÅDA planter box** – drag out a raised crop bed of any shape; grows ground crops at 110% fertility.
- **GLÖMSTRÄK table segment** – 1x1 dining-table panels placed with an area drag. Adjacent panels merge: rim only on exposed sides, legs only on outside corners. Any shape works and every cell is an eating surface.

## Layout
- `About/`, `loadFolders.xml` – mod metadata
- `Defs/` – ThingDefs
- `Patches/` – gives the hob the electric stove's recipes
- `1.6/Assemblies/` – compiled DLL
- `Source/SlopkeaFurniture/` – C# (`dotnet build -c Release`, references `Krafs.Rimworld.Ref`)
- `Source/Art/` – draws every texture and checks it against the defs and C#; see its README
