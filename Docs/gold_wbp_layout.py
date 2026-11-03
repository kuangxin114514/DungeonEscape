# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\gold_wbp_layout.txt"
lines=[]
def log(m):
    lines.append(str(m))
    try: unreal.log("GLAY: "+str(m))
    except Exception: print(m)
try:
    DST="/Game/UI/HUD/WBP_PlayerGold"
    unreal.EditorAssetLibrary.load_asset(DST)
    for o in unreal.ObjectIterator(unreal.Object):
        try:
            pn=o.get_path_name()
        except Exception:
            continue
        if "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree." not in pn:
            continue
        cn=o.get_class().get_name() if o.get_class() else "?"
        nm=o.get_name()
        log("%s %s"%(cn,nm))
    cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
    log("cls="+str(cls))
    if cls:
        cdo=unreal.get_default_object(cls)
        log("cdo="+str(cdo))
        try:
            cdo.set_editor_property("is_focusable", False)
            log("focusable false")
        except Exception as e:
            log("focus err "+str(e))
    unreal.EditorAssetLibrary.save_asset(DST)
    log("saved")
except Exception as e:
    log("TOPERR "+str(e))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE")