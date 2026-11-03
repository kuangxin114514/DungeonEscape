# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\verify_gold_create.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("VGOLD: "+str(m))
cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
log("cls="+str(cls))
# create without PC if possible
w=None
try:
    w=unreal.new_object(cls)
    log("new_object="+str(w))
except Exception as e:
    log("new_object fail "+str(e))
if w is not None:
    for nm in ("Txt_Gold","TextBlock_0","Txt_HP"):
        try:
            t=w.get_widget_from_name(nm)
            log("get %s -> %s"%(nm,t))
        except Exception as e:
            log("get %s err %s"%(nm,e))
    # try set text
    try:
        t=w.get_widget_from_name("TextBlock_0")
        if t:
            t.set_text(unreal.Text(u"\u91d1\u5e01: 100"))
            log("set_text ok")
            try:
                log("vis="+str(t.get_visibility()))
            except Exception:
                pass
    except Exception as e:
        log("set "+str(e))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")