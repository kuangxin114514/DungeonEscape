# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t346_shield.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("T346: "+str(m))
    except Exception: print(m)

for p in (
 "/Game/Characters/Player/KayKit/Mesh/Round_Shield",
 "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield",
 "/Game/UI/Shop/WBP_Shop_Armor",
):
    a=unreal.load_asset(p)
    L("load %s -> %s cls=%s"%(p, a.get_name() if a else None, a.get_class().get_name() if a else None))

# armor shop buttons/text
for o in unreal.ObjectIterator(unreal.Button):
    try: pn=o.get_path_name()
    except Exception: continue
    if "WBP_Shop_Armor" not in pn: continue
    L("BTN %s name=%s"%(pn, o.get_name()))
for o in unreal.ObjectIterator(unreal.TextBlock):
    try: pn=o.get_path_name()
    except Exception: continue
    if "WBP_Shop_Armor" not in pn: continue
    try: tx=o.get_text()
    except Exception:
        try: tx=o.get_editor_property("text")
        except Exception: tx="?"
    L("TB %s text=%s"%(o.get_name(), tx))

# current knight shield GEN_VARIABLE
for leaf in ("BP_KayKitKnight_Sword1","BP_KayKitKnight"):
    unreal.load_asset("/Game/Characters/Player/KayKit/"+leaf)
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if leaf not in pn or "GEN_VARIABLE" not in pn: continue
        if leaf=="BP_KayKitKnight" and "Sword1" in pn: continue
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        try:
            loc=o.get_editor_property("relative_location")
            rot=o.get_editor_property("relative_rotation")
            sc=o.get_editor_property("relative_scale3d")
        except Exception:
            loc=rot=sc=None
        L("%s %s mesh=%s loc=%s rot=%s sc=%s"%(leaf,o.get_name(), sm.get_name() if sm else None, loc, rot, sc))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
