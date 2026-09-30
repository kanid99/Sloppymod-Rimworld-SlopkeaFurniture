using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One cell of a drag-to-shape dining table. Segments of the same def merge:
    /// each cell prints the variant for which of its sides are joined, so the rim,
    /// apron and legs only appear on the outside of whatever shape was dragged out.
    /// </summary>
    public class Building_SlopkeaTable : Building
    {
        // Must match Source/Art/draw_sprites.py (table_path, BITS).
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Table/Slopkea_Table_";

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

        /// <summary>Bit set per joined side: N=1, E=2, S=4, W=8.</summary>
        public int VariantIndex()
        {
            return Neighbors.JoinedBits<Building_SlopkeaTable>(this);
        }

        public override void Print(SectionLayer layer)
        {
            Neighbors.PrintVariant(layer, this, TexPrefix + VariantIndex(), ShaderDatabase.Cutout);
        }
    }
}
