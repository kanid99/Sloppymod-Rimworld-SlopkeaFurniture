using RimWorld;
using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// A rocking chair that rocks while someone sits in it. In the side views the
    /// sprite tilts a few degrees on its runner; front and back views cannot show
    /// a tilt, so there it eases back and forth along its facing instead. Drawn in
    /// real time (drawerType RealtimeOnly)
    /// because a map-mesh texture cannot move. The rock is driven by game ticks,
    /// so it stops when paused and speeds up with the game.
    /// </summary>
    public class Building_SlopkeaRockingChair : Building
    {
        private const float RockDistance = 0.035f;   // cells, at the end of each swing
        private const float RockAngle = 4f;          // degrees, side views
        private const float RockSpeed = 0.06f;       // radians per tick

        /// <summary>False for a glider: it swings flat on its links, so it only slides.</summary>
        protected virtual bool Tilts => true;

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
                float s = Mathf.Sin(t);
                if (Tilts && Rotation.IsHorizontal)
                {
                    Graphic.Draw(drawLoc, flip ? Rotation.Opposite : Rotation, this, s * RockAngle);
                    return;
                }
                drawLoc += Rotation.FacingCell.ToVector3() * (s * RockDistance);
            }
            base.DrawAt(drawLoc, flip);
        }
    }
}
