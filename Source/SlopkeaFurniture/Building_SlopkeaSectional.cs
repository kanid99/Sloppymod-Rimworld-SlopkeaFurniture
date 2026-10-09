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
        protected virtual string TexPrefix => "Things/Building/Furniture/Slopkea/Sectional/Slopkea_Sectional_";
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
        /// What the back meets: "b" - a seat back to back with this one (facing
        /// the other way) or a wall, so the back runs flush and back-to-back rows
        /// read as one island with a shared spine; "p" - the side of a seat at
        /// right angles, as when seats sit back-to-side round a square: then there
        /// is no backrest, the seat is an all-round cushion and an upholstered
        /// round post stands where they meet; "" - nothing, an ordinary back.
        /// </summary>
        public string BackState()
        {
            IntVec3 behind = Rotation.Opposite.FacingCell;
            if (Neighbors.IsWall(this, behind)) return "b";
            Building_SlopkeaSectional b = Neighbors.Get<Building_SlopkeaSectional>(this, behind);
            if (b == null) return "";
            if (b.Rotation == Rotation.Opposite) return "b";
            return b.Rotation != Rotation ? "p" : "";
        }

        public string VariantPath()
        {
            char cw = SideState(Rotation.Rotated(RotationDirection.Clockwise));
            char ccw = SideState(Rotation.Rotated(RotationDirection.Counterclockwise));
            return TexPrefix + FacingNames[Rotation.AsInt] + "_" + cw + ccw + BackState();
        }

        public override void Print(SectionLayer layer)
        {
            Neighbors.PrintVariant(layer, this, VariantPath(), ShaderDatabase.CutoutComplex);
        }
    }
}
