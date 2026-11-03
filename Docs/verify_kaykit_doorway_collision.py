# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\verify_kaykit_doorway_collision.txt"
checks = [
    "/Game/Environments/KayKitDungeon/Meshes/Walls/SM_wall_doorway",
    "/Game/Environments/KayKitDungeon/Meshes/Walls/SM_wall_open_scaffold",
    "/Game/Environments/KayKitDungeon/Meshes/Walls/SM_wall",  # solid control
    "/Game/Environments/KayKitDungeon/Meshes/Walls/SM_wall_corner",  # solid control
]
lines = []
for p in checks:
    m = unreal.EditorAssetLibrary.load_asset(p)
    bs = m.get_editor_property("body_setup")
    flag = str(bs.get_editor_property("collision_trace_flag"))
    ag = bs.get_editor_property("agg_geom")
    convex = len(ag.get_editor_property("convex_elems") or [])
    boxes = len(ag.get_editor_property("box_elems") or [])
    lines.append("%s flag=%s convex=%d boxes=%d" % (p.rsplit("/",1)[-1], flag, convex, boxes))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("VERIFY_OK")
