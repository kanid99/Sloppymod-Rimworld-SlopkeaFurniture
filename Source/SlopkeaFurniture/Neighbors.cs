using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>Shared helpers for furniture that redraws itself based on matching neighbours.</summary>
    public static class Neighbors
    {
        public static T Get<T>(Thing self, IntVec3 dir) where T : Thing
        {
            IntVec3 c = self.Position + dir;
            if (!c.InBounds(self.Map)) return null;
            foreach (Thing t in c.GetThingList(self.Map))
            {
                if (t is T match && t.def == self.def) return match;
            }
            return null;
        }

        /// <summary>Force the surrounding cells to re-print so their joins update.</summary>
        public static void DirtyAround(Map map, IntVec3 center)
        {
            if (map == null) return;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(new TargetInfo(center, map)))
            {
                if (c.InBounds(map)) map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Things);
            }
        }
    }
}
