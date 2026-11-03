# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,sys,importlib,traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t340.txt"
L=[];log=lambda m:(L.append(str(m)),unreal.log("T340:"+str(m)))
try:
 py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
 if py not in sys.path: sys.path.insert(0,py)
 m=importlib.reload(sys.modules["shop_interact_runtime"]) if "shop_interact_runtime" in sys.modules else __import__("shop_interact_runtime")
 try:m.bootstrap()
 except Exception as e: log("boot "+str(e))
 log("meta="+str(dict(m._PLAYER_META)))
 w=m._pie_world(); log("world="+str(w))
 if w:
  try:
   ok=m.buy_sword1(w); log("buy="+str(ok)+" meta="+str(dict(m._PLAYER_META)))
  except Exception as e:
   log("buyERR "+str(e)); log(traceback.format_exc())
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  p=pc.get_controlled_pawn() if pc else None
  log("pawn="+str(p.get_class().get_path_name() if p else None))
  if p:
   for c in p.get_components_by_class(unreal.StaticMeshComponent.static_class()) or []:
    sm=c.get_editor_property("static_mesh")
    log("SMC %s %s sc=%s"%(c.get_name(), sm.get_name() if sm else None, c.get_editor_property("relative_scale3d")))
  log("cls1="+str(unreal.load_class(None,m._BP_KNIGHT_SWORD1)))
except Exception as e:
 log("ERR "+str(e)); log(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(L)+"\n")
print("WROTE")
