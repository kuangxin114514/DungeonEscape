# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t350.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T350RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m=importlib.reload(sys.modules["shop_interact_runtime"]); L("reloaded")
else:
    import shop_interact_runtime as m; L("imported")
try:
    m._SWORD_TMPL_CACHE.clear()
    m._SWORD_TMPL_FAIL_LOGGED.clear()
    L("cache cleared")
except Exception as e:
    L("cache clear "+str(e))
L("tag has T350=%s" % ("T350_DUAL_SWORD_SHIELD" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",encoding="utf-8").read()[:2500]))
L("SWORD1_ITEM=%s" % m.SWORD1_ITEM)
L("SHIELD1_ITEM=%s" % m.SHIELD1_ITEM)
L("path dual=%s" % m._bp_asset_path_for_leaf("BP_KayKitKnight_Sword1Shield1"))
L("path sword=%s" % m._bp_asset_path_for_leaf("BP_KayKitKnight_Sword1"))
L("path shield=%s" % m._bp_asset_path_for_leaf("BP_KayKitKnight_Shield1"))
L("pn dual=%s" % m._pn_matches_bp_leaf("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1Shield1.xxx:StaticMesh_GEN_VARIABLE", "BP_KayKitKnight_Sword1Shield1"))
L("pn sword vs dual=%s" % m._pn_matches_bp_leaf("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1Shield1.xxx:StaticMesh_GEN_VARIABLE", "BP_KayKitKnight_Sword1"))
L("pn shield vs dual=%s" % m._pn_matches_bp_leaf("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1Shield1.xxx:StaticMesh1_GEN_VARIABLE", "BP_KayKitKnight_Shield1"))
dual=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1Shield1")
L("dual_bp=%s" % dual)
sw=m._read_bp_sword_template("BP_KayKitKnight_Sword1Shield1", prefer_mesh_substr="Sword")
if sw:
    sm,loc,rot,sc=sw
    L("dual_sword mesh=%s scale=%s" % (sm.get_name() if sm else None, sc))
else:
    L("dual_sword=None")
sh=m._read_bp_shield_template("BP_KayKitKnight_Sword1Shield1")
if sh:
    sm,loc,rot,sc=sh
    L("dual_shield mesh=%s scale=%s" % (sm.get_name() if sm else None, sc))
else:
    L("dual_shield=None")
sw1=m._read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
L("sword1_only mesh=%s" % (sw1[0].get_name() if sw1 and sw1[0] else None))
sh1=m._read_bp_shield_template("BP_KayKitKnight_Shield1")
L("shield1_only mesh=%s" % (sh1[0].get_name() if sh1 and sh1[0] else None))
fn=getattr(m,"bootstrap",None)
if callable(fn):
    fn(); L("bootstrap ok")
else:
    L("no bootstrap")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
