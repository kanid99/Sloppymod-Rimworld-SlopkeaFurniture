using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>Marks a kitchen run module. Any two modules facing the same way join.</summary>
    public interface ISlopkeaKitchenModule
    {
    }

    /// <summary>A full-height module (hutch, oven, fridge): wall cabinets butt up to it.</summary>
    public interface ISlopkeaTallModule
    {
    }

    /// <summary>A counter module that can carry wall cabinets.</summary>
    public interface IWallCabinetHolder
    {
        bool WallCabinets { get; }
    }

    /// <summary>
    /// Shared join-and-print for side-joining units: each side is open (o) or
    /// joined (j) - joined to a matching neighbour, or flush to a wall - and the
    /// unit prints &lt;prefix&gt;&lt;facing&gt;_&lt;cw&gt;&lt;ccw&gt;[b], the view for that facing.
    /// "b" (kitchen only) is the back flush to a wall.
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
            return Neighbors.IsWall(self, side.FacingCell) ? 'j' : 'o';
        }

        public static string Variant(Thing self, System.Func<Thing, bool> joinsWith, bool backVariants)
        {
            char cw = State(self, self.Rotation.Rotated(RotationDirection.Clockwise), joinsWith);
            char ccw = State(self, self.Rotation.Rotated(RotationDirection.Counterclockwise), joinsWith);
            string back = backVariants && Neighbors.IsWall(self, self.Rotation.Opposite.FacingCell) ? "b" : "";
            return FacingNames[self.Rotation.AsInt] + "_" + cw + ccw + back;
        }

        public static void Print(SectionLayer layer, Thing self, string prefix, System.Func<Thing, bool> joinsWith,
            bool backVariants = false)
        {
            Neighbors.PrintVariant(layer, self, prefix + Variant(self, joinsWith, backVariants), ShaderDatabase.CutoutComplex);
        }

        public static bool IsKitchen(Thing t) => t is ISlopkeaKitchenModule;
    }

    // Must match Source/Art/draw_kitchen.py and draw_kitchen_tall.py (kitchen_path).
    internal static class KitchenPaths
    {
        public const string Dir = "Things/Building/Furniture/Slopkea/Kitchen/Slopkea_";
    }

    /// <summary>The wall cabinets a counter module can be fitted with, drawn above pawns.</summary>
    public static class WallCabinets
    {
        // Wall cabinets hang above head height, so they print over pawns.
        private static readonly float Altitude = AltitudeLayer.PawnUnused.AltitudeFor();

        private static bool RunsOn(Thing t) =>
            t is ISlopkeaTallModule || (t is IWallCabinetHolder h && h.WallCabinets);

        public static void Print(SectionLayer layer, Thing self)
        {
            Neighbors.PrintVariant(layer, self, KitchenPaths.Dir + "WallCab_" + SideJoin.Variant(self, RunsOn, true),
                ShaderDatabase.CutoutComplex, Altitude);
        }

        public static Gizmo Toggle(Thing self, System.Func<bool> get, System.Action<bool> set)
        {
            return new Command_Toggle
            {
                defaultLabel = "Wall cabinets",
                defaultDesc = "Fit (or remove) wall cabinets above this counter. Neighbouring fitted counters join into one run.",
                icon = ContentFinder<Texture2D>.Get("UI/Slopkea/WallCabinets"),
                isActive = get,
                toggleAction = () =>
                {
                    set(!get());
                    if (self.Spawned) Neighbors.DirtyAround(self.Map, self.Position);
                    if (self.Spawned) self.Map.mapDrawer.MapMeshDirty(self.Position, MapMeshFlagDefOf.Things);
                }
            };
        }
    }

    /// <summary>Kitchen cabinet: a worktop over cupboards that store food.</summary>
    public class Building_SlopkeaCabinet : Building_Storage, ISlopkeaKitchenModule, IWallCabinetHolder
    {
        private bool wallCabinets;
        public bool WallCabinets => wallCabinets;

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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wallCabinets, "slopkeaWallCabinets");
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            yield return SlopkeaFurniture.WallCabinets.Toggle(this, () => wallCabinets, v => wallCabinets = v);
        }

        public override void Print(SectionLayer layer)
        {
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Cabinet_", SideJoin.IsKitchen, true);
            if (wallCabinets) SlopkeaFurniture.WallCabinets.Print(layer, this);
        }
    }

    /// <summary>Kitchen sink: a counter with a basin. Keeps the room cleaner.</summary>
    public class Building_SlopkeaSink : Building, ISlopkeaKitchenModule, IWallCabinetHolder
    {
        private bool wallCabinets;
        public bool WallCabinets => wallCabinets;

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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wallCabinets, "slopkeaWallCabinets");
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            yield return SlopkeaFurniture.WallCabinets.Toggle(this, () => wallCabinets, v => wallCabinets = v);
        }

        public override void Print(SectionLayer layer)
        {
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Sink_", SideJoin.IsKitchen, true);
            if (wallCabinets) SlopkeaFurniture.WallCabinets.Print(layer, this);
        }
    }

    /// <summary>Kitchen hob: an electric stove built into the run.</summary>
    public class Building_SlopkeaHob : Building_WorkTable_HeatPush, ISlopkeaKitchenModule, IWallCabinetHolder
    {
        private bool wallCabinets;
        public bool WallCabinets => wallCabinets;

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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref wallCabinets, "slopkeaWallCabinets");
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            yield return SlopkeaFurniture.WallCabinets.Toggle(this, () => wallCabinets, v => wallCabinets = v);
        }

        public override void Print(SectionLayer layer)
        {
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Hob_", SideJoin.IsKitchen, true);
            if (wallCabinets) SlopkeaFurniture.WallCabinets.Print(layer, this);
        }
    }

    /// <summary>Hutch: open shelving over a counter, joining the run. Storage.</summary>
    public class Building_SlopkeaHutch : Building_Storage, ISlopkeaKitchenModule, ISlopkeaTallModule
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
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Hutch_", SideJoin.IsKitchen, true);
    }

    /// <summary>Wall oven: a tall built-in oven tower. A cooking station, like the hob.</summary>
    public class Building_SlopkeaOven : Building_WorkTable_HeatPush, ISlopkeaKitchenModule, ISlopkeaTallModule
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
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Oven_", SideJoin.IsKitchen, true);
    }

    /// <summary>
    /// Built-in fridge: food storage that, while powered, stops what is stored in
    /// it from rotting. RimWorld decides rot from the cell's temperature; rather
    /// than patch that, the fridge holds each stored item's rot progress where it
    /// was when it went in (checked every rare tick), so it keeps like it's frozen.
    /// Unpowered, food rots as normal.
    /// </summary>
    public class Building_SlopkeaFridge : Building_Storage, ISlopkeaKitchenModule, ISlopkeaTallModule
    {
        private readonly Dictionary<Thing, float> held = new Dictionary<Thing, float>();
        private readonly HashSet<Thing> seen = new HashSet<Thing>();

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
            held.Clear();
            Neighbors.DirtyAround(map, pos);
        }

        private bool Powered
        {
            get
            {
                CompPowerTrader power = GetComp<CompPowerTrader>();
                return power == null || power.PowerOn;
            }
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!Spawned) return;
            if (!Powered)
            {
                held.Clear();
                return;
            }
            seen.Clear();
            foreach (IntVec3 c in AllSlotCells())
            {
                foreach (Thing t in c.GetThingList(Map))
                {
                    CompRottable rot = t.TryGetComp<CompRottable>();
                    if (rot == null) continue;
                    seen.Add(t);
                    if (held.TryGetValue(t, out float p) && rot.RotProgress > p) rot.RotProgress = p;
                    else held[t] = rot.RotProgress;
                }
            }
            if (held.Count > seen.Count)
            {
                List<Thing> gone = new List<Thing>();
                foreach (Thing t in held.Keys) if (!seen.Contains(t)) gone.Add(t);
                foreach (Thing t in gone) held.Remove(t);
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string state = Powered ? "Keeping food fresh." : "No power: food will rot.";
            return s.NullOrEmpty() ? state : s + "\n" + state;
        }

        public override void Print(SectionLayer layer) =>
            SideJoin.Print(layer, this, KitchenPaths.Dir + "Fridge_", SideJoin.IsKitchen, true);
    }
}
