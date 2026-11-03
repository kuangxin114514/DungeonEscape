# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_gold_wbp.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("FIXGOLD: "+str(m))
DST="/Game/UI/HUD/WBP_PlayerGold"
unreal.EditorAssetLibrary.load_asset(DST)
# Fix SOURCE blueprint TextBlock (not _C)
src_tb=None
gen_tb=None
for o in unreal.ObjectIterator(unreal.TextBlock):
    try:
        pn=o.get_path_name()
    except Exception:
        continue
    if "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree." in pn:
        src_tb=o
    elif "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C:WidgetTree." in pn:
        gen_tb=o
log("src=%s gen=%s"%(src_tb,gen_tb))
for tb, tag in ((src_tb,"src"),(gen_tb,"gen")):
    if tb is None: continue
    try:
        tb.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
        tb.set_editor_property("text", unreal.Text(u"\u91d1\u5e01: 100"))
        font=tb.get_editor_property("font")
        font.set_editor_property("size", 28)
        tb.set_editor_property("font", font)
        tb.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1.0,0.85,0.2,1.0)))
        slot=tb.slot
        if slot is not None:
            anc=unreal.Anchors(); anc.minimum=unreal.Vector2D(1.0,0.0); anc.maximum=unreal.Vector2D(1.0,0.0)
            try: slot.set_anchors(anc)
            except Exception: slot.set_editor_property("anchors", anc)
            try: slot.set_alignment(unreal.Vector2D(1.0,0.0))
            except Exception: slot.set_editor_property("alignment", unreal.Vector2D(1.0,0.0))
            try: slot.set_offsets(unreal.Margin(-260.0, 24.0, -24.0, 64.0))
            except Exception: slot.set_editor_property("offsets", unreal.Margin(-260.0, 24.0, -24.0, 64.0))
            try: slot.set_auto_size(True)
            except Exception: pass
        log(tag+" fixed")
    except Exception as e:
        log(tag+" err "+str(e))
# Compile widget blueprint if possible
wbp=unreal.EditorAssetLibrary.load_asset(DST)
try:
    unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
    log("compiled")
except Exception as e:
    log("compile "+str(e))
try:
    # older API
    unreal.KismetSystemLibrary.execute_console_command(None, "KeepSourceAssetsLoaded")
except Exception:
    pass
unreal.EditorAssetLibrary.save_asset(DST)
log("saved")
# Also collapse any leftover panels that might cover screen from Shop2
for o in unreal.ObjectIterator(unreal.Object):
    try:
        pn=o.get_path_name()
    except Exception:
        continue
    if "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree." not in pn:
        continue
    cn=o.get_class().get_name() if o.get_class() else "?"
    nm=o.get_name()
    if cn in ("Button","Image","Border","SizeBox","Overlay","HorizontalBox","VerticalBox","UniformGridPanel","WrapBox") and nm not in ("CanvasPanel_0",):
        try:
            o.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
            log("hide %s %s"%(cn,nm))
        except Exception:
            pass
unreal.EditorAssetLibrary.save_asset(DST)
cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
log("class="+str(cls))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")