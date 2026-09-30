using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One cell of a drag-to-shape rug. Not an edifice, so furniture stands on it.
    /// The border runs along the outside of the shape and turns every inside corner:
    /// a corner bit is set when both of its sides are rug but the diagonal is not.
    /// </summary>
    public class Building_SlopkeaRug : Building
    {
        // Must match Source/Art/draw_modular.py (rug_path, CORNERS).
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Rug/Slopkea_Rug_";

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

        private bool IsRug(IntVec3 offset) => Neighbors.Get<Building_SlopkeaRug>(this, offset) != null;

        /// <summary>NE=1, SE=2, SW=4, NW=8.</summary>
        public int CornerBits()
        {
            int c = 0;
            IntVec3 n = IntVec3.North, e = IntVec3.East, s = IntVec3.South, w = IntVec3.West;
            if (IsRug(n) && IsRug(e) && !IsRug(n + e)) c |= 1;
            if (IsRug(s) && IsRug(e) && !IsRug(s + e)) c |= 2;
            if (IsRug(s) && IsRug(w) && !IsRug(s + w)) c |= 4;
            if (IsRug(n) && IsRug(w) && !IsRug(n + w)) c |= 8;
            return c;
        }

        public override void Print(SectionLayer layer)
        {
            string path = TexPrefix + Neighbors.JoinedBits<Building_SlopkeaRug>(this) + "_" + CornerBits();
            Neighbors.PrintVariant(layer, this, path, ShaderDatabase.Cutout);
        }
    }
}
