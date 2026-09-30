# Slopkea Furniture

Flat-pack, IKEA-inspired furniture for RimWorld 1.6. Some assembly required.

## Furniture
- **Everything is stuffable.** All Slopkea pieces inherit `SlopkeaFurnitureBase` and take stuff.
- **BÖRKSTÅD sectional seat** – 1x1 rotatable seats (fabric, leather, wood, metal, stone). Drag a line of them; backrests follow facing, armrests appear at open ends, and a seat whose front neighbour turns 90° gets a wrap-around corner backrest. Sittable, so they work as dining chairs.
- **GLÖMSTRÄK table segment** – 1x1 dining-table panels placed with an area drag. Adjacent panels merge: rim only on exposed sides, legs only on outside corners. Any shape works and every cell is an eating surface.

## Layout
- `About/`, `loadFolders.xml` – mod metadata
- `Defs/` – ThingDefs
- `1.6/Assemblies/` – compiled DLL
- `Source/SlopkeaFurniture/` – C# (`dotnet build -c Release`, references `Krafs.Rimworld.Ref`)
- `Source/make_textures.py` – regenerates the placeholder textures (needs Pillow)
