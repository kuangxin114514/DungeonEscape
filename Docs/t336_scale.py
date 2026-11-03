# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,re
SCALE=0.01
n=0
for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
    pn=o.get_path_name()
    if "BP_KayKitKnight_Sword1" not in pn or "GEN_VARIABLE" not in pn: continue
    if "StaticMesh1" in o.get_name(): continue
    sm=o.get_editor_property("static_mesh")
    if not sm or "Sword" not in sm.get_name(): continue
    o.set_editor_property("relative_scale3d", unreal.Vector(SCALE,SCALE,SCALE)); n+=1
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
unreal.EditorAssetLibrary.save_loaded_asset(bp)
try: unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
except Exception: pass
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
open(p,"w",encoding="utf-8").write(re.sub(r"SWORD1_SCALE\s*=\s*[0-9.]+","SWORD1_SCALE = 0.01",t,count=1))
print("OK",n)
