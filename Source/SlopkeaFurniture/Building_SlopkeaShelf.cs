using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One unit of KALLAX-style cube shelving: a storage building holding a stack per
    /// cube. Units facing the same way join along their sides into one run with
    /// shared walls; each side is open (o) or joined (j).
    /// </summary>
    public class Building_SlopkeaShelf : Building_Storage
    {
        // Must match Source/Art/draw_modular.py (shelf_path).
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Shelf/Slopkea_Shelf_";
        private static readonly string[] FacingNames = { "north", "east", "south", "west" };

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            Neighbors.DirtyAround(map, Position);
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 pos = Position;
            base.DeSpawn(mode);
            Neighbors.DirtyAround(map, pos);
        }

        public char SideState(Rot4 side)
        {
            Building_SlopkeaShelf n = Neighbors.Get<Building_SlopkeaShelf>(this, side.FacingCell);
            return n != null && n.Rotation == Rotation ? 'j' : 'o';
        }

        public override void Print(SectionLayer layer)
        {
            char cw = SideState(Rotation.Rotated(RotationDirection.Clockwise));
            char ccw = SideState(Rotation.Rotated(RotationDirection.Counterclockwise));
            Neighbors.PrintVariant(layer, this, TexPrefix + FacingNames[Rotation.AsInt] + "_" + cw + ccw,
                ShaderDatabase.CutoutComplex);
        }
    }
}
