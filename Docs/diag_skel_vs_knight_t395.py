# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_skel_vs_knight_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395c: "+str(m))
    except Exception: print(m)

# compare mesh rel / forward of skeleton vs knight BPs
paths=[
 "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton",
]
# find knight BPs
for p in unreal.EditorAssetLibrary.list_assets("/Game/Characters", recursive=True):
    if "BP_" in p and ("Knight" in p or "KayKit" in p or "Player" in p or "Character" in p):
        if p.endswith(".") or p.count(".")>2: continue
        paths.append(p.split(".")[0] if "." in p else p)

seen=set()
for BP in paths:
    if BP in seen: continue
    seen.add(BP)
    try:
        if not unreal.EditorAssetLibrary.does_asset_exist(BP): continue
        cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
        if cls is None: continue
        cdo=unreal.get_default_object(cls)
        if not isinstance(cdo, unreal.Character): continue
    except Exception:
        continue
    try:
        mesh=cdo.get_editor_property("mesh")
        rr=mesh.get_editor_property("relative_rotation")
        sm=mesh.get_editor_property("skeletal_mesh")
        cm=cdo.get_editor_property("character_movement")
        rate=cm.get_editor_property("rotation_rate")
        L("%s"%BP)
        L("  mesh=%s rel p=%.1f y=%.1f r=%.1f"%(sm.get_name() if sm else None, float(rr.pitch),float(rr.yaw),float(rr.roll)))
        L("  ortm=%s rate p=%.1f y=%.1f ucry=%s"%(cm.get_editor_property("orient_rotation_to_movement"), float(rate.pitch),float(rate.yaw), cdo.get_editor_property("use_controller_rotation_yaw")))
    except Exception as e:
        L("%s ERR %s"%(BP,e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done",len(lines))
