using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    // Must match Source/Art/draw_more.py (side_path, divider_path, planter_path).
    internal static class MorePaths
    {
        public const string Bench = "Things/Building/Furniture/Slopkea/Bench/Slopkea_Bench_";
        public const string Wardrobe = "Things/Building/Furniture/Slopkea/Wardrobe/Slopkea_Wardrobe_";
        public const string Divider = "Things/Building/Furniture/Slopkea/Divider/Slopkea_Divider_";
        public const string Planter = "Things/Building/Furniture/Slopkea/Planter/Slopkea_Planter_";
    }

    /// <summary>A backless bench seat. Benches facing the same way join into a pew.</summary>
    public class Building_SlopkeaBench : Building
    {
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

        public override void Print(SectionLayer layer) =>
            SideJoin.Print(layer, this, MorePaths.Bench, t => t.def == def);
    }

    /// <summary>Clothing storage. Wardrobes facing the same way join into one fitted run.</summary>
    public class Building_SlopkeaWardrobe : Building_Storage
    {
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

        public override void Print(SectionLayer layer) =>
            SideJoin.Print(layer, this, MorePaths.Wardrobe, t => t.def == def);
    }

    /// <summary>A folding screen that follows the line it is dragged along, in any direction.</summary>
    public class Building_SlopkeaDivider : Building
    {
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

        public override void Print(SectionLayer layer) =>
            Neighbors.PrintVariant(layer, this, MorePaths.Divider + Neighbors.JoinedBits<Building_SlopkeaDivider>(this),
                ShaderDatabase.CutoutComplex);
    }

    /// <summary>A raised bed, dragged to any shape; the rim runs only round the outside.</summary>
    public class Building_SlopkeaPlanter : Building_PlantGrower
    {
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

        public override void Print(SectionLayer layer) =>
            Neighbors.PrintVariant(layer, this, MorePaths.Planter + Neighbors.JoinedBits<Building_SlopkeaPlanter>(this),
                ShaderDatabase.CutoutComplex);
    }
}
