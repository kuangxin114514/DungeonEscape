# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t367.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T367RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m=importlib.reload(sys.modules["shop_interact_runtime"]); L("reloaded")
else:
    import shop_interact_runtime as m; L("imported")
try:
    m._SWORD_TMPL_CACHE.clear(); m._SWORD_TMPL_FAIL_LOGGED.clear()
except Exception: pass
st=m._read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
ht=m._read_bp_shield_template("BP_KayKitKnight_Shield1")
L("sword_tmpl=%s" % (st[0].get_name() if st else None))
L("shield_tmpl=%s" % (ht[0].get_name() if ht else None))
# confirm apply functions no longer mention dual in source via inspect? skip
src_s=open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",encoding="utf-8").read()
chunk=src_s[src_s.find("def apply_equipped_sword_look"):src_s.find("def ensure_equipped_pawn_class")]
L("sword_fn_has_dual=%s" % ("Sword1Shield1" in chunk))
chunk2=src_s[src_s.find("def apply_equipped_shield_look"):src_s.find("def buy_shield1")]
L("shield_fn_has_dual=%s" % ("Sword1Shield1" in chunk2))
fn=getattr(m,"bootstrap",None)
if callable(fn): fn(); L("bootstrap ok")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
