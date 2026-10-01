"""About/Preview.png (640x360) and About/ModIcon.png (256x256), composited from
the shipped textures so the store page cannot drift from the game.
python3 Source/Art/make_about_art.py   (from the repo root)"""
from PIL import Image, ImageDraw

from compose import render

WOOD = (133, 94, 62)
FABRIC = (70, 110, 150)
YELLOW = (255, 204, 0)


def main():
    scene = {}
    # An L sectional facing a dragged-out table.
    for x in range(0, 4):
        scene[(x, 4)] = ("sect", "south")
    for z in range(1, 4):
        scene[(0, z)] = ("sect", "east")
    for x in range(5, 9):
        for z in range(1, 3):
            scene[(x, z)] = ("table",)
    scene[(6, 3)] = ("table",)
    scene[(7, 3)] = ("table",)
    for x in (5, 8):
        scene[(x, 0)] = ("sect", "north")
    scene[(9, 1)] = ("sect", "west")
    img = render(scene, {"table": WOOD, "sect": FABRIC}, (10, 5), 56, bg=(92, 84, 72))
    prev = Image.new("RGBA", (640, 360), (0, 81, 186, 255))
    prev.alpha_composite(img, ((640 - img.width) // 2, 20))
    d = ImageDraw.Draw(prev)
    d.rectangle([0, 310, 640, 360], fill=YELLOW + (255,))
    d.text((20, 326), "SLOPKEA FURNITURE  -  some assembly required", fill=(0, 51, 120))
    prev.convert("RGB").save("About/Preview.png")

    # The icon is one corner of the sectional: it still reads at 32px.
    icon_scene = {(0, 1): ("sect", "south"), (1, 1): ("sect", "south"), (0, 0): ("sect", "east")}
    icon = render(icon_scene, {"sect": FABRIC, "table": WOOD}, (2, 2), 112, bg=(0, 81, 186))
    out = Image.new("RGBA", (256, 256), (0, 81, 186, 255))
    out.alpha_composite(icon, (16, 16))
    out.convert("RGB").save("About/ModIcon.png")


if __name__ == "__main__":
    main()
