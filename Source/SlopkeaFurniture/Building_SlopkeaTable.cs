using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One cell of a drag-to-shape dining table. Segments of the same def merge:
    /// the rim is only drawn on sides without a neighbouring segment, and legs only
    /// on outside corners, so any dragged shape reads as a single table.
    /// </summary>
    public class Building_SlopkeaTable : Building
    {
        private const string EdgeTex = "Slopkea/Table/Table_Edge";
        private const string LegTex = "Slopkea/Table/Table_Leg";

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
            base.Print(layer);
            Color color = DrawColor;
            Material edge = MaterialPool.MatFrom(EdgeTex, ShaderDatabase.Cutout, color);
            Material leg = MaterialPool.MatFrom(LegTex, ShaderDatabase.Cutout, color);
            Vector3 center = Position.ToVector3Shifted();
            center.y = def.Altitude + 0.01f;

            for (int i = 0; i < 4; i++)
            {
                Rot4 side = new Rot4(i);
                bool open = Neighbors.Get<Building_SlopkeaTable>(this, side.FacingCell) == null;
                if (open)
                {
                    Printer_Plane.PrintPlane(layer, center, Vector2.one, edge, side.AsAngle);
                }

                // Outside corner between this side and the next clockwise side.
                Rot4 next = side.Rotated(RotationDirection.Clockwise);
                bool nextOpen = Neighbors.Get<Building_SlopkeaTable>(this, next.FacingCell) == null;
                if (open && nextOpen)
                {
                    Vector3 legPos = center;
                    legPos.y += 0.005f;
                    Printer_Plane.PrintPlane(layer, legPos, Vector2.one, leg, side.AsAngle);
                }
            }
        }
    }
}
