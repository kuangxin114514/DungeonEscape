# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\find_skel_bp_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395h: "+str(m))
    except Exception: print(m)

for folder in ["/Game/Characters/Enemies/Skeleton","/Game/Characters","/Game"]:
    try:
        assets=unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
    except Exception as e:
        L("list %s %s"%(folder,e)); continue
    for a in assets:
        if "Skeleton" in a and ("BP_" in a or "Enemy" in a):
            L(a)
            exists=unreal.EditorAssetLibrary.does_asset_exist(a)
            L("  exists=%s"%exists)

# find from live class
for o in unreal.ObjectIterator(unreal.Blueprint):
    try: n=o.get_name(); pn=o.get_path_name()
    except Exception: continue
    if "Skeleton" in n or "Skeleton" in pn:
        L("BP obj %s"%pn)

for o in unreal.ObjectIterator(unreal.Character):
    try: cn=o.get_class().get_name(); pn=o.get_path_name()
    except Exception: continue
    if "Skeleton" in cn:
        L("char %s class=%s"%(pn,cn))
        try:
            mov=o.get_editor_property("character_movement")
            L("  ortm=%s ucdr=%s y=%.1f"%(mov.get_editor_property("orient_rotation_to_movement"), mov.get_editor_property("use_controller_desired_rotation"), float(mov.get_editor_property("rotation_rate").yaw)))
        except Exception as e:
            L("  "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
