namespace SlopkeaFurniture
{
    /// <summary>
    /// SÄNKA conversation pit floor: dragged out in any shape like the rug, and
    /// joined the same way, but drawn as a sunken carpet with the pit's step-down
    /// walls round the outside of the shape. Not an edifice, so a coffee table or
    /// the pit seats stand on it.
    /// </summary>
    public class Building_SlopkeaPit : Building_SlopkeaRug
    {
        // Must match Source/Art/draw_pit.py (pit_path).
        protected override string TexPrefix => "Things/Building/Furniture/Slopkea/Pit/Slopkea_Pit_";
    }

    /// <summary>
    /// SÄNKA pit seat: built-in banquette seating run round the inside of the pit.
    /// Joins exactly like the sectional (runs, wrapped corners, back to back), but
    /// is drawn built in - no plinth or feet.
    /// </summary>
    public class Building_SlopkeaPitSeat : Building_SlopkeaSectional
    {
        // Must match Source/Art/draw_pit.py (pitseat_path).
        protected override string TexPrefix => "Things/Building/Furniture/Slopkea/Pit/Slopkea_PitSeat_";
    }
}
