using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>Marks a kitchen run module. Any two modules facing the same way join.</summary>
    public interface ISlopkeaKitchenModule
    {
    }

    /// <summary>
    /// Shared join-and-print for side-joining units (kitchen modules, bookcase):
    /// each side is open (o) or joined (j), and the unit prints
    /// &lt;prefix&gt;&lt;facing&gt;_&lt;cw&gt;&lt;ccw&gt;, the view drawn for that facing.
    /// </summary>
    public static class SideJoin
    {
        private static readonly string[] FacingNames = { "north", "east", "south", "west" };

        public static char State(Thing self, Rot4 side, System.Func<Thing, bool> joinsWith)
        {
            IntVec3 c = self.Position + side.FacingCell;
            if (!c.InBounds(self.Map)) return 'o';
            foreach (Thing t in c.GetThingList(self.Map))
            {
                if (t != self && t.Rotation == self.Rotation && joinsWith(t)) return 'j';
            }
            return 'o';
        }

        public static void Print(SectionLayer layer, Thing self, string prefix, System.Func<Thing, bool> joinsWith)
        {
            char cw = State(self, self.Rotation.Rotated(RotationDirection.Clockwise), joinsWith);
            char ccw = State(self, self.Rotation.Rotated(RotationDirection.Counterclockwise), joinsWith);
            Neighbors.PrintVariant(layer, self, prefix + FacingNames[self.Rotation.AsInt] + "_" + cw + ccw,
                ShaderDatabase.CutoutComplex);
        }

        public static bool IsKitchen(Thing t) => t is ISlopkeaKitchenModule;
    }

    // Must match Source/Art/draw_kitchen.py (kitchen_path).
    internal static class KitchenPaths
    {
        public const string Dir = "Things/Building/Furniture/Slopkea/Kitchen/Slopkea_";
    }

    /// <summary>Kitchen cabinet: a worktop over cupboards that store food.</summary>
    public class Building_SlopkeaCabinet : Building_Storage, ISlopkeaKitchenModule
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
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Cabinet_", SideJoin.IsKitchen);
    }

    /// <summary>Kitchen sink: a counter with a basin. Keeps the room cleaner.</summary>
    public class Building_SlopkeaSink : Building, ISlopkeaKitchenModule
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
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Sink_", SideJoin.IsKitchen);
    }

    /// <summary>Kitchen hob: an electric stove built into the run.</summary>
    public class Building_SlopkeaHob : Building_WorkTable_HeatPush, ISlopkeaKitchenModule
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
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Hob_", SideJoin.IsKitchen);
    }
}
