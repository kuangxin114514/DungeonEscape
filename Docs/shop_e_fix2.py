# -*- coding: utf-8 -*-
import sys, unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_e_fix2.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("SHOPFIX2:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0, PY)
    if "shop_interact_runtime" in sys.modules:
        old=sys.modules["shop_interact_runtime"]
        try:
            h=old._TICK_HANDLE[0]
            if h is not None:
                try: unreal.unregister_slate_post_tick_callback(h)
                except Exception:
                    try: unreal.unregister_slate_pre_tick_callback(h)
                    except Exception: pass
        except Exception: pass
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as sir
    log("tick="+str(sir._TICK_HANDLE[0]))
    log("PC applied="+str(sir._PC_APPLIED[0]))
    gm=unreal.get_default_object(unreal.load_class(None,"/Game/Core/GameFlow/GM_Hub.GM_Hub_C"))
    log("GM_Hub PC="+str(gm.get_editor_property("player_controller_class")))
    # confirm WBP + triggers still present
    by={}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        by[a.get_actor_label() or ""]=a
    for n in ("ShopTrigger_Weapon","ShopTrigger_Armor","ShopTrigger_Health","GateTrigger_DungeonEntrance",
              "InteractHint_Weapon","InteractHint_Armor","InteractHint_Health","InteractHint_Gate"):
        log("%s present=%s"%(n, n in by))
    log("WBP="+str(unreal.load_class(None,"/Game/UI/Shop/WBP_Shop.WBP_Shop_C")))
    log("DONE")
except Exception:
    log(traceback.format_exc())
flush()