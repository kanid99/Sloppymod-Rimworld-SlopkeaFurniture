using RimWorld;
using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// A rocking chair that rocks while someone sits in it: the chair eases back
    /// and forth along its facing. Drawn in real time (drawerType RealtimeOnly)
    /// because a map-mesh texture cannot move. The rock is driven by game ticks,
    /// so it stops when paused and speeds up with the game.
    /// </summary>
    public class Building_SlopkeaRockingChair : Building
    {
        private const float RockDistance = 0.035f;   // cells, at the end of each swing
        private const float RockSpeed = 0.06f;       // radians per tick

        private bool Occupied()
        {
            Pawn p = Position.GetFirstPawn(Map);
            return p != null && !p.pather.Moving && p.GetPosture() == PawnPosture.Standing;
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            if (Spawned && Occupied())
            {
                // Offset per-thing so two chairs side by side do not rock in lockstep.
                float t = (Find.TickManager.TicksGame + thingIDNumber * 37) * RockSpeed;
                drawLoc += Rotation.FacingCell.ToVector3() * (Mathf.Sin(t) * RockDistance);
            }
            base.DrawAt(drawLoc, flip);
        }
    }
}
