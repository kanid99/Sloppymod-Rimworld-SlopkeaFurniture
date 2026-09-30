using RimWorld;
using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>Shared helpers for furniture that picks its texture from matching neighbours.</summary>
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

        /// <summary>
        /// Print one pre-drawn variant over the cell. The variants are views, drawn
        /// per facing, so the plane is never rotated (that would rotate the light too).
        /// </summary>
        public static void PrintVariant(SectionLayer layer, Thing thing, string texPath, Shader shader)
        {
            Graphic g = GraphicDatabase.Get<Graphic_Single>(texPath, shader, Vector2.one, thing.DrawColor, thing.DrawColorTwo);
            Vector3 center = thing.Position.ToVector3Shifted();
            center.y = thing.def.Altitude;
            Printer_Plane.PrintPlane(layer, center, Vector2.one, g.MatSingle);
        }
    }
}
