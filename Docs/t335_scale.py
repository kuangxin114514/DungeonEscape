# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\t335_scale.txt"
lines=[]; SCALE=0.28
def L(m):
    lines.append(str(m))
    try: unreal.log("T335: "+str(m))
    except Exception: print(m)
mesh=unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword_2H")
n=0
for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
    pn=o.get_path_name()
    if "BP_KayKitKnight_Sword1" not in pn: continue
    if "GEN_VARIABLE" not in pn: continue
    if "StaticMesh1" in o.get_name(): continue
    sm=o.get_editor_property("static_mesh")
    if not sm or "Sword" not in sm.get_name(): continue
    o.set_editor_property("relative_scale3d", unreal.Vector(SCALE,SCALE,SCALE))
    n+=1; L("set %s scale=%s"%(o.get_name(),SCALE))
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
unreal.EditorAssetLibrary.save_loaded_asset(bp)
try: unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
except Exception as e: L(str(e))
# also runtime constant
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
import re
t2=re.sub(r"SWORD1_SCALE\s*=\s*[0-9.]+","SWORD1_SCALE = %.2f"%SCALE,t,count=1)
open(p,"w",encoding="utf-8").write(t2)
L("done n=%d"%n)
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
