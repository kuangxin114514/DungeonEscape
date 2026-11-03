# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\set_sword1_cdo.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T330C: "+str(m))
    except Exception: print(m)
DST = "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
SWORD = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword_2H"
SCALE = 0.45
try:
    bp = unreal.load_asset(DST)
    mesh = unreal.load_asset(SWORD)
    changed=0
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight_Sword1" not in pn:
            continue
        try:
            cur = o.get_editor_property("static_mesh")
        except Exception:
            cur = None
        cur_name = cur.get_name() if cur else ""
        L("SMC %s cur=%s" % (o.get_name(), cur_name))
        if cur_name == "SM_KayKitSword" or o.get_name().startswith("StaticMesh_GEN"):
            # the sword slot (not shield StaticMesh1)
            if "StaticMesh1" in o.get_name():
                L("skip shield")
                continue
            try:
                o.set_editor_property("static_mesh", mesh)
                o.set_editor_property("relative_scale3d", unreal.Vector(SCALE, SCALE, SCALE))
                changed += 1
                L("SET sword OK scale=%s" % SCALE)
            except Exception as e:
                L("SET fail "+str(e))
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    try:
        unreal.EditorAssetLibrary.save_asset(DST)
    except Exception:
        pass
    # verify
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight_Sword1" not in pn:
            continue
        cur = o.get_editor_property("static_mesh")
        L("VERIFY %s -> %s scale=%s" % (o.get_name(), cur.get_name() if cur else None, o.get_editor_property("relative_scale3d")))
    L("changed=%d" % changed)
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
