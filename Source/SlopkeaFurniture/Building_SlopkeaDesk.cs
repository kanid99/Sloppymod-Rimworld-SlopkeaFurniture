using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One cell of a drag-to-shape desk. Works as a research bench (the interaction
    /// spot is in front of each cell), and joins with neighbouring desk cells like
    /// the dining table: edge banding and legs only on the outside of the shape.
    /// </summary>
    public class Building_SlopkeaDesk : Building_ResearchBench
    {
        // Must match Source/Art/draw_modular.py (desk_path).
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Desk/Slopkea_Desk_";

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

        public override void Print(SectionLayer layer)
        {
            Neighbors.PrintVariant(layer, this, TexPrefix + Neighbors.JoinedBits<Building_SlopkeaDesk>(this),
                ShaderDatabase.CutoutComplex);
        }
    }
}
