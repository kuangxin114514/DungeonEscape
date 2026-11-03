# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, sys
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\verify_gold_find.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("VFIND: "+str(m))
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import shop_interact_runtime as m
cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
w=unreal.new_object(cls)
log("w="+str(w))
# widget_tree?
for attr in ("widget_tree","WidgetTree"):
    try:
        v=w.get_editor_property("widget_tree")
        log("widget_tree="+str(v))
        if v:
            try:
                rw=v.get_editor_property("root_widget")
                log("root="+str(rw)+" name="+str(rw.get_name() if rw else None))
            except Exception as e:
                log("root err "+str(e))
    except Exception as e:
        log("wt err "+str(e))
for nm in ("Txt_Gold","TextBlock_0","Txt_HP","CanvasPanel_0"):
    try:
        t=m._find_named_widget(w, nm)
        log("find %s -> %s"%(nm,t))
    except Exception as e:
        log("find %s err %s"%(nm,e))
# WidgetBlueprintLibrary
try:
    pc=unreal.EditorLevelLibrary.get_level_viewport_camera_info
except Exception:
    pass
try:
    # try create via library with editor world
    world=None
    try:
        world=unreal.EditorLevelLibrary.get_editor_world()
    except Exception as e:
        log("world "+str(e))
    log("world="+str(world))
    if world:
        # get first player controller in PIE if any
        pcs=[]
        try:
            for o in unreal.ObjectIterator(unreal.PlayerController):
                pcs.append(o)
        except Exception as e:
            log("pc iter "+str(e))
        log("pcs=%d"%len(pcs))
        if pcs:
            ww=unreal.WidgetBlueprintLibrary.create(pcs[0], cls, pcs[0])
            log("create="+str(ww))
            t=m._find_named_widget(ww, "TextBlock_0")
            log("find after create "+str(t))
            if t:
                t.set_text(unreal.Text(u"\u91d1\u5e01: 100"))
                log("set ok")
except Exception as e:
    log("lib "+str(e))
# Also walk all children of new_object
try:
    n=int(w.get_children_count())
    log("children_count="+str(n))
except Exception as e:
    log("cc "+str(e))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")