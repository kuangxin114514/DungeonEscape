# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\create_wbp_player_gold.txt"
lines=[]
def log(m):
    s=str(m); lines.append(s)
    try: unreal.log("T311DUP2: "+s)
    except Exception: print(s)
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")

SRC="/Game/UI/Shop/WBP_Shop2"
DST="/Game/UI/HUD/WBP_PlayerGold"
unreal.EditorAssetLibrary.load_asset(SRC)
log("src loaded")
if unreal.EditorAssetLibrary.does_asset_exist(DST):
    try:
        unreal.EditorAssetLibrary.delete_asset(DST)
        log("deleted old")
    except Exception as e:
        log("del "+str(e))
dup=unreal.EditorAssetLibrary.duplicate_asset(SRC, DST)
log("dup="+str(dup))
unreal.EditorAssetLibrary.load_asset(DST)
# Collect widgets belonging to gold package
texts=[]; buttons=[]; images=[]; others=[]
for o in unreal.ObjectIterator(unreal.Object):
    try:
        pn=o.get_path_name()
    except Exception:
        continue
    if "/Game/UI/HUD/WBP_PlayerGold" not in pn:
        continue
    cn=o.get_class().get_name() if o.get_class() else "?"
    if cn=="TextBlock":
        texts.append(o)
    elif cn=="Button":
        buttons.append(o)
    elif cn=="Image":
        images.append(o)
    elif cn in ("ProgressBar","EditableText","EditableTextBox","CheckBox","Slider"):
        others.append(o)
log("texts=%d buttons=%d images=%d others=%d"%(len(texts),len(buttons),len(images),len(others)))
primary=texts[0] if texts else None
for o in texts:
    log("TB "+o.get_name()+" path="+o.get_path_name()[-90:])
if primary is not None:
    try:
        primary.set_editor_property("text", unreal.Text(u"\u91d1\u5e01: 100"))
        log("set text ok "+primary.get_name())
    except Exception as e:
        log("set text "+str(e))
    try:
        font=primary.get_editor_property("font")
        font.set_editor_property("size", 28)
        primary.set_editor_property("font", font)
        log("font size 28")
    except Exception as e:
        log("font "+str(e))
    try:
        primary.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1.0,0.85,0.2,1.0)))
    except Exception as e:
        log("color "+str(e))
    try:
        primary.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    try:
        slot=primary.slot
        log("slot type="+str(type(slot))+" "+str(slot))
        if slot is not None:
            anc=unreal.Anchors()
            anc.minimum=unreal.Vector2D(1.0, 0.0)
            anc.maximum=unreal.Vector2D(1.0, 0.0)
            try:
                slot.set_anchors(anc)
            except Exception:
                try: slot.set_editor_property("anchors", anc)
                except Exception as e: log("anc "+str(e))
            try:
                slot.set_alignment(unreal.Vector2D(1.0, 0.0))
            except Exception:
                try: slot.set_editor_property("alignment", unreal.Vector2D(1.0,0.0))
                except Exception as e: log("align "+str(e))
            # Offsets: left, top, right, bottom — for top-right anchored, left/right are often negative from right edge
            try:
                slot.set_offsets(unreal.Margin(-260.0, 24.0, -24.0, 64.0))
            except Exception:
                try:
                    slot.set_editor_property("offsets", unreal.Margin(-260.0, 24.0, -24.0, 64.0))
                except Exception as e:
                    log("off "+str(e))
            try:
                slot.set_auto_size(True)
            except Exception:
                pass
            log("slot moved")
    except Exception as e:
        log("slot fail "+str(e))
# Hide clutter
for o in buttons+images+others:
    try:
        o.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
        log("hide "+o.get_class().get_name()+" "+o.get_name())
    except Exception as e:
        log("hide fail "+str(e))
# Hide extra texts
for o in texts[1:]:
    try:
        o.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
        log("hide extra text "+o.get_name())
    except Exception:
        pass
try:
    unreal.EditorAssetLibrary.save_asset(DST)
    log("saved")
except Exception as e:
    log("save "+str(e))
cls=unreal.load_class(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C")
log("class="+str(cls))
# verify after save reload
unreal.EditorAssetLibrary.load_asset(DST)
n=0
for o in unreal.ObjectIterator(unreal.TextBlock):
    try:
        pn=o.get_path_name()
    except Exception:
        continue
    if "/Game/UI/HUD/WBP_PlayerGold" in pn:
        n+=1
        vis=None
        try: vis=o.get_editor_property("visibility")
        except Exception: pass
        log("verify TB %s vis=%s"%(o.get_name(),vis))
log("verify n=%d"%n)
flush()