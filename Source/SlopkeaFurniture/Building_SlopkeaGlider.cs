namespace SlopkeaFurniture
{
    /// <summary>
    /// A nursery glider. Same as the rocking chair, but it glides back and forth on
    /// its links instead of tipping on curved runners, in every view.
    /// </summary>
    public class Building_SlopkeaGlider : Building_SlopkeaRockingChair
    {
        protected override bool Tilts => false;
    }
}
