# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
import traceback
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\create_wbp_player_gold.txt"
lines = []
def log(m):
    s = str(m); lines.append(s)
    try: unreal.log("T311ADDTXT: " + s)
    except Exception: print(s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def main():
    paths = [
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree",
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C:WidgetTree",
    ]
    tree = None
    for p in paths:
        try:
            tree = unreal.load_object(None, p)
            log("load tree %s -> %s dir_has_construct=%s" % (p, tree, hasattr(tree, "construct_widget") if tree else None))
            if tree and hasattr(tree, "construct_widget"):
                break
        except Exception as e:
            log("load %s %s" % (p, e))
    wbp = unreal.EditorAssetLibrary.load_asset("/Game/UI/HUD/WBP_PlayerGold")
    log("wbp=%s" % wbp)
    if wbp is not None:
        for attr in ("widget_tree", "WidgetTree"):
            try:
                t = getattr(wbp, attr, None)
                log("attr %s -> %s construct=%s" % (attr, t, hasattr(t, "construct_widget") if t else None))
                if t and hasattr(t, "construct_widget"):
                    tree = t
            except Exception as e:
                log("attr %s %s" % (attr, e))
        try:
            t = wbp.get_editor_property("widget_tree")
            log("prop widget_tree -> %s type=%s construct=%s" % (t, type(t), hasattr(t, "construct_widget")))
            if hasattr(t, "construct_widget"):
                tree = t
        except Exception as e:
            log("prop " + str(e))
    if tree is None or not hasattr(tree, "construct_widget"):
        # try cast / find methods
        log("tree methods sample: %s" % ([m for m in dir(tree) if "construct" in m.lower() or "widget" in m.lower()][:40] if tree else None))
        flush(); return

    canvas = None
    for p in (
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree.CanvasPanel_0",
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C:WidgetTree.CanvasPanel_0",
    ):
        try:
            canvas = unreal.load_object(None, p)
            if canvas:
                log("canvas " + p)
                break
        except Exception:
            pass
    if canvas is None:
        try:
            canvas = tree.get_editor_property("root_widget")
            log("root_widget=" + str(canvas))
        except Exception as e:
            log("root " + str(e))
    # If Txt_Gold already exists, skip
    existing = unreal.load_object(None, "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree.Txt_Gold")
    if existing:
        log("Txt_Gold already exists")
        flush(); return

    txt = None
    try:
        txt = tree.construct_widget(unreal.TextBlock, "Txt_Gold")
        log("construct_widget -> " + str(txt))
    except Exception as e:
        log("construct_widget ERR " + str(e))
        log(traceback.format_exc())
        flush(); return
    try:
        txt.set_editor_property("text", unreal.Text(u"\u91d1\u5e01: 100"))
    except Exception as e:
        log("set text " + str(e))
    try:
        font = txt.get_editor_property("font")
        font.set_editor_property("size", 28)
        txt.set_editor_property("font", font)
    except Exception as e:
        log("font " + str(e))
    try:
        txt.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1.0, 0.85, 0.2, 1.0)))
    except Exception as e:
        log("color " + str(e))
    try:
        txt.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    if canvas is not None:
        try:
            slot = canvas.add_child_to_canvas(txt)
            log("slot=" + str(slot))
            if slot:
                anc = unreal.Anchors(); anc.minimum = unreal.Vector2D(1.0, 0.0); anc.maximum = unreal.Vector2D(1.0, 0.0)
                slot.set_anchors(anc)
                slot.set_alignment(unreal.Vector2D(1.0, 0.0))
                try:
                    slot.set_offsets(unreal.Margin(-268.0, 36.0, -48.0, 76.0))
                except Exception as e:
                    log("offsets " + str(e))
                try:
                    slot.set_auto_size(True)
                except Exception:
                    pass
        except Exception as e:
            log("add_child " + str(e))
            log(traceback.format_exc())
    # Collapse PB
    for p in (
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold:WidgetTree.PB_Health",
        "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C:WidgetTree.PB_Health",
    ):
        pb = unreal.load_object(None, p)
        if pb:
            try:
                pb.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
                log("collapsed " + p)
            except Exception as e:
                log("collapse " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/UI/HUD/WBP_PlayerGold")
        log("saved")
    except Exception as e:
        log("save " + str(e))
    # verify
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "WBP_PlayerGold" in pn:
            log("FOUND TEXT " + pn)
    flush()

main()