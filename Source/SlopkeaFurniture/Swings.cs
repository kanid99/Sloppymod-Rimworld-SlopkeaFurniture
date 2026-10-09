using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// A hanging porch swing: two seats wide, swinging gently back and forth along
    /// its facing while anyone sits in it - slower and further than a rocking chair.
    /// </summary>
    public class Building_SlopkeaSwing : Building_SlopkeaRockingChair
    {
        protected override bool Tilts => false;
        protected override float RockDistance => 0.07f;
        protected override float RockSpeed => 0.035f;
    }

    /// <summary>Only under a roof: a swing needs something to hang from.</summary>
    public class PlaceWorker_SlopkeaNeedsRoof : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
            Thing thingToIgnore = null, Thing thing = null)
        {
            foreach (IntVec3 c in GenAdj.OccupiedRect(loc, rot, checkingDef.Size))
            {
                if (!c.InBounds(map) || !map.roofGrid.Roofed(c))
                    return new AcceptanceReport("Needs a roof to hang from.");
            }
            return true;
        }
    }
}
