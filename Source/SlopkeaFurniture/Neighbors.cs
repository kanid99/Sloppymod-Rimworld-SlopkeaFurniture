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

        /// <summary>Bit set per side with a matching neighbour: N=1, E=2, S=4, W=8.</summary>
        public static int JoinedBits<T>(Thing self) where T : Thing
        {
            int i = 0;
            for (int r = 0; r < 4; r++)
            {
                if (Get<T>(self, new Rot4(r).FacingCell) != null) i |= 1 << r;
            }
            return i;
        }

        /// <summary>
        /// Inside corners of a dragged shape: a bit is set where both sides have a
        /// matching neighbour but the cell diagonally between them does not, so
        /// the outline has to turn the corner inside this cell. NE=1, SE=2, SW=4,
        /// NW=8. Must match Source/Art/slopkea_units.py (CORNER_BITS).
        /// </summary>
        public static int InsideCornerBits<T>(Thing self) where T : Thing
        {
            int c = 0;
            IntVec3 n = IntVec3.North, e = IntVec3.East, s = IntVec3.South, w = IntVec3.West;
            bool hasN = Get<T>(self, n) != null, hasE = Get<T>(self, e) != null;
            bool hasS = Get<T>(self, s) != null, hasW = Get<T>(self, w) != null;
            if (hasN && hasE && Get<T>(self, n + e) == null) c |= 1;
            if (hasS && hasE && Get<T>(self, s + e) == null) c |= 2;
            if (hasS && hasW && Get<T>(self, s + w) == null) c |= 4;
            if (hasN && hasW && Get<T>(self, n + w) == null) c |= 8;
            return c;
        }

        /// <summary>
        /// The texture name's tail for a drag-to-shape cell: its side bits, plus
        /// "_&lt;corner bits&gt;" when it sits at an inside corner. Must match
        /// Source/Art/slopkea_units.py (variant_name).
        /// </summary>
        public static string ShapeVariant<T>(Thing self) where T : Thing
        {
            int corners = InsideCornerBits<T>(self);
            int sides = JoinedBits<T>(self);
            return corners == 0 ? sides.ToString() : sides + "_" + corners;
        }

        /// <summary>
        /// A wall, or anything wall-like (natural rock, a full impassable block),
        /// in the cell in direction `dir`: furniture runs flush up to it.
        /// </summary>
        public static bool IsWall(Thing self, IntVec3 dir)
        {
            IntVec3 c = self.Position + dir;
            if (!c.InBounds(self.Map)) return false;
            Building e = c.GetEdifice(self.Map);
            return e != null && e != self && e.def.passability == Traversability.Impassable && e.def.fillPercent >= 0.99f;
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
            PrintVariant(layer, thing, texPath, shader, thing.def.Altitude);
        }

        public static void PrintVariant(SectionLayer layer, Thing thing, string texPath, Shader shader, float altitude)
        {
            Graphic g = GraphicDatabase.Get<Graphic_Single>(texPath, shader, Vector2.one, thing.DrawColor, thing.DrawColorTwo);
            Vector3 center = thing.Position.ToVector3Shifted();
            center.y = altitude;
            Printer_Plane.PrintPlane(layer, center, Vector2.one, g.MatSingle);
        }
    }
}
