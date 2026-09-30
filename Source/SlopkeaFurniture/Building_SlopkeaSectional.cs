using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// One seat of a modular sectional couch. Place seats in any line or L/U shape:
    /// backrests follow each seat's rotation, armrests appear only at open ends,
    /// and a seat whose front neighbour turns the corner grows a second backrest.
    /// </summary>
    public class Building_SlopkeaSectional : Building
    {
        private const string BackTex = "Slopkea/Sectional/Sectional_Back";
        private const string ArmTex = "Slopkea/Sectional/Sectional_Arm";

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
            Material back = MaterialPool.MatFrom(BackTex, ShaderDatabase.Cutout, color);
            Material arm = MaterialPool.MatFrom(ArmTex, ShaderDatabase.Cutout, color);
            Vector3 center = Position.ToVector3Shifted();
            center.y = def.Altitude + 0.01f;

            Rot4 facing = Rotation;
            Printer_Plane.PrintPlane(layer, center, Vector2.one, back, facing.Opposite.AsAngle);

            Building_SlopkeaSectional front = Neighbors.Get<Building_SlopkeaSectional>(this, facing.FacingCell);
            Rot4[] sides = { facing.Rotated(RotationDirection.Clockwise), facing.Rotated(RotationDirection.Counterclockwise) };
            foreach (Rot4 side in sides)
            {
                if (Neighbors.Get<Building_SlopkeaSectional>(this, side.FacingCell) != null) continue;

                // Corner seat: the seat in front of us faces along this side's axis
                // with its back toward this side, so the backrest wraps around.
                bool corner = front != null && front.Rotation == side.Opposite;
                Vector3 pos = center;
                pos.y += 0.005f;
                Printer_Plane.PrintPlane(layer, pos, Vector2.one, corner ? back : arm, side.AsAngle);
            }
        }
    }
}
