# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, sys
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\verify_gold_find2.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("VF2: "+str(m))
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import shop_interact_runtime as m
cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
world=unreal.EditorLevelLibrary.get_editor_world()
# pick a live PC
pc=None
for o in unreal.ObjectIterator(unreal.PlayerController):
    try:
        pn=o.get_path_name()
    except Exception:
        continue
    if "Transient" in pn or "Map_" in pn or "UEDPIE" in pn:
        pc=o
        log("pc cand "+pn)
        break
if pc is None:
    for o in unreal.ObjectIterator(unreal.PlayerController):
        pc=o; break
log("pc="+str(pc))
wbl=m._wbl()
log("wbl="+str(wbl))
widget=None
if wbl and pc:
    for attempt in (
        lambda: wbl.call_method("create", (), {"world_context_object": world, "widget_type": cls, "owning_player": pc}),
        lambda: wbl.call_method("create", (), {"world_context_object": pc, "widget_type": cls, "owning_player": pc}),
        lambda: wbl.call_method("create", (world, cls, pc)),
        lambda: wbl.call_method("create", (pc, cls, pc)),
    ):
        try:
            widget=attempt()
            log("attempt -> "+str(widget))
            if widget: break
        except Exception as e:
            log("attempt err "+str(e))
if widget:
    t=m._find_named_widget(widget, "TextBlock_0")
    log("find TextBlock_0 -> "+str(t))
    if t is None:
        # dump widgets whose outer is widget
        n=0
        for o in unreal.ObjectIterator(unreal.Widget):
            try:
                if not m._outer_chain_contains(o, widget):
                    continue
            except Exception:
                continue
            n+=1
            if n<=20:
                log("child "+o.get_class().get_name()+" "+o.get_name()+" "+o.get_path_name()[-80:])
        log("owned widgets n="+str(n))
    else:
        try:
            t.set_text(unreal.Text(u"\u91d1\u5e01: 100"))
            log("set_text ok")
        except Exception as e:
            log("set "+str(e))
        try:
            widget.add_to_viewport(51)
            widget.set_alignment_in_viewport(unreal.Vector2D(1.0,0.0))
            widget.set_position_in_viewport(unreal.Vector2D(-48.0,36.0), True)
            log("added viewport")
        except Exception as e:
            log("vp "+str(e))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")