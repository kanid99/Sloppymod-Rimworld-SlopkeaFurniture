using RimWorld;
using UnityEngine;
using Verse;

namespace SlopkeaFurniture
{
    /// <summary>
    /// BILLY-style bookcase. Everything a bookcase does - holding, drawing and
    /// lending out books - is vanilla's Building_Bookcase. This only swaps the
    /// graphic for the empty, joined view that matches its neighbours: units facing
    /// the same way join into one run, each side open (o) or joined (j).
    /// </summary>
    public class Building_SlopkeaBookcase : Building_Bookcase
    {
        // Must match Source/Art/draw_kitchen.py (book_path): <prefix><cw><ccw>, and
        // Graphic_Multi appends _<facing>.
        private const string TexPrefix = "Things/Building/Furniture/Slopkea/Bookcase/Slopkea_Bookcase_";

        private Graphic joinedGraphic;

        public override Graphic Graphic => joinedGraphic ?? base.Graphic;

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            RefreshGraphic();
            Neighbors.DirtyAround(map, Position);
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = Map;
            IntVec3 pos = Position;
            base.DeSpawn(mode);
            joinedGraphic = null;
            Neighbors.DirtyAround(map, pos);
        }

        public override void Notify_ColorChanged()
        {
            joinedGraphic = null;
            base.Notify_ColorChanged();
            if (Spawned) RefreshGraphic();
        }

        // A neighbour appearing or leaving re-prints this cell, so the join is
        // re-read here, before vanilla prints (and later draws) through Graphic.
        public override void Print(SectionLayer layer)
        {
            RefreshGraphic();
            base.Print(layer);
        }

        private void RefreshGraphic()
        {
            char cw = SideJoin.State(this, Rotation.Rotated(RotationDirection.Clockwise), t => t.def == def);
            char ccw = SideJoin.State(this, Rotation.Rotated(RotationDirection.Counterclockwise), t => t.def == def);
            joinedGraphic = GraphicDatabase.Get<Graphic_Multi>(TexPrefix + cw + ccw, ShaderDatabase.CutoutComplex,
                def.graphicData.drawSize, DrawColor, DrawColorTwo);
        }
    }
}
