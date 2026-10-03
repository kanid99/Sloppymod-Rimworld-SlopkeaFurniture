using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One seat of a modular sectional couch. Place seats in any line or L/U shape.
    /// Each side of a seat is an armrest (a), joined to the next seat (j), or a
    /// corner backrest (c) when the seat in front turns the corner; the seat prints
    /// the pre-drawn view for its facing and those two states.
    /// </summary>
    public class Building_SlopkeaSectional : Building
    {
        // Must match Source/Art/draw_sprites.py (sect_path).
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Sectional/Slopkea_Sectional_";
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
            if (Neighbors.Get<Building_SlopkeaSectional>(this, side.FacingCell) != null) return 'j';
            // Corner seat: the seat in front has its back to this side, so the backrest wraps.
            Building_SlopkeaSectional front = Neighbors.Get<Building_SlopkeaSectional>(this, Rotation.FacingCell);
            if (front != null && front.Rotation == side.Opposite) return 'c';
            return 'a';
        }

        /// <summary>
        /// The back is joined: a seat back to back with this one (facing the other
        /// way), or a wall behind. The back then runs flush ("b"), so back-to-back
        /// rows read as one island couch with a shared spine.
        /// </summary>
        public bool BackJoined()
        {
            IntVec3 behind = Rotation.Opposite.FacingCell;
            Building_SlopkeaSectional b = Neighbors.Get<Building_SlopkeaSectional>(this, behind);
            return (b != null && b.Rotation == Rotation.Opposite) || Neighbors.IsWall(this, behind);
        }

        public string VariantPath()
        {
            char cw = SideState(Rotation.Rotated(RotationDirection.Clockwise));
            char ccw = SideState(Rotation.Rotated(RotationDirection.Counterclockwise));
            return TexPrefix + FacingNames[Rotation.AsInt] + "_" + cw + ccw + (BackJoined() ? "b" : "");
        }

        public override void Print(SectionLayer layer)
        {
            Neighbors.PrintVariant(layer, this, VariantPath(), ShaderDatabase.CutoutComplex);
        }
    }
}
