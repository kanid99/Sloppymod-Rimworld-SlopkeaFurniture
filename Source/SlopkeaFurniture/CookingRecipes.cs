using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// The hob and wall oven cook exactly what the electric stove cooks. Vanilla
    /// (and other mods) attach stove recipes two ways - on each recipe's
    /// recipeUsers, which Patches/Slopkea_HobRecipes.xml covers, and on the
    /// stove's own recipes list, which a patch cannot copy. So once every def has
    /// loaded, the stove's full list is copied across. Matching recipes is also
    /// what lets bills be copied from a vanilla stove and pasted onto ours.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class CookingRecipes
    {
        private static readonly string[] Cookers = { "Slopkea_Hob", "Slopkea_WallOven" };

        static CookingRecipes()
        {
            ThingDef stove = DefDatabase<ThingDef>.GetNamedSilentFail("ElectricStove");
            if (stove == null) return;
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            foreach (string name in Cookers)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null) continue;
                if (def.recipes == null) def.recipes = new List<RecipeDef>();
                foreach (RecipeDef r in stove.AllRecipes)
                {
                    if (!def.recipes.Contains(r)) def.recipes.Add(r);
                }
                cache?.SetValue(def, null);
            }
        }
    }
}
