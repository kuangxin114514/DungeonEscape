# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t344.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T344: "+str(m))
    except Exception: print(m)

# Count GEN_VARIABLE sword comps currently in memory for both BPs
for leaf in ("BP_KayKitKnight_Sword1", "BP_KayKitKnight"):
    n=0; samples=[]
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if leaf not in pn or "GEN_VARIABLE" not in pn: continue
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else None
        n+=1
        if len(samples)<5:
            samples.append("%s mesh=%s"%(o.get_name(), sname))
    L("%s GEN_VARIABLE SMC count=%d samples=%s"%(leaf,n,samples))

# Try load_asset then recount
for path in (
    "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight",
):
    a=unreal.load_asset(path)
    L("load_asset %s -> %s"%(path, a.get_name() if a else None))

for leaf in ("BP_KayKitKnight_Sword1", "BP_KayKitKnight"):
    n=0; samples=[]
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if leaf not in pn or "GEN_VARIABLE" not in pn: continue
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else None
        n+=1
        if len(samples)<5:
            samples.append("%s mesh=%s"%(o.get_name(), sname))
    L("AFTER LOAD %s GEN_VARIABLE SMC count=%d samples=%s"%(leaf,n,samples))

# meta
try:
    import shop_interact_runtime as m
    L("equipped=%s gold=%s inv=%s"%(m.get_equipped_sword(), m.get_gold(), m.get_inventory()))
except Exception as e:
    L("meta err "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
