# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t340_bp.txt"
L=[]
def log(m):
 L.append(str(m)); unreal.log("T340B:"+str(m))
cls=unreal.load_class(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1.BP_KayKitKnight_Sword1_C")
log("cls="+str(cls))
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
log("bp="+str(bp))
for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
 pn=o.get_path_name()
 if "BP_KayKitKnight_Sword1" not in pn: continue
 if "GEN_VARIABLE" not in pn: continue
 sm=o.get_editor_property("static_mesh")
 log("%s mesh=%s scale=%s loc=%s"%(o.get_name(), sm.get_name() if sm else None, o.get_editor_property("relative_scale3d"), o.get_editor_property("relative_location")))
# read ensure function snippet from disk via python path
import shop_interact_runtime as m
import importlib,sys
sys.path.insert(0,r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
importlib.reload(m)
log("SWORD1_SCALE="+str(m.SWORD1_SCALE))
log("desired default meta eq="+str(m._PLAYER_META.get("equipped_sword")))
open(OUT,"w",encoding="utf-8").write("\n".join(L)+"\n")
print("WROTE")
