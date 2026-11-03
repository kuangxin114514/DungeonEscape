# -*- coding: utf-8 -*-
"""Build a bulletproof WBP_ShopSimple with Canvas+Image+Text; open it visibly in PIE.
Also try to fix CreateWidget by reconstructing node / compiling BP after PIE stop."""
from __future__ import print_function
import unreal
import traceback
import sys

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_build_shop_wbp.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("BLD: " + s)
    except Exception:
        print("BLD:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def ensure_shop_simple():
    path = "/Game/UI/Shop/WBP_ShopSimple"
    bp = unreal.load_object(None, path + ".WBP_ShopSimple")
    log("existing=" + str(bp))
    if bp is None:
        try:
            factory = unreal.WidgetBlueprintFactory()
            try:
                factory.set_editor_property("parent_class", unreal.UserWidget)
            except Exception as e:
                log("parent set " + str(e))
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            bp = asset_tools.create_asset("WBP_ShopSimple", "/Game/UI/Shop", unreal.WidgetBlueprint, factory)
            log("created=" + str(bp))
        except Exception as e:
            log("create ERR " + str(e))
            bp = unreal.load_object(None, path + ".WBP_ShopSimple")
    if bp is None:
        return None
    tree = unreal.load_object(None, path + ".WBP_ShopSimple:WidgetTree")
    log("tree=" + str(tree))
    if tree is None:
        try:
            tree = bp.get_editor_property("widget_tree")
        except Exception:
            try:
                tree = bp.get_editor_property("WidgetTree")
            except Exception as e:
                log("no tree " + str(e))
                return bp
    # Try construct widgets
    root = None
    try:
        root = tree.get_editor_property("root_widget")
    except Exception:
        try:
            root = tree.get_editor_property("RootWidget")
        except Exception as e:
            log("root get " + str(e))
    log("root=" + str(root))
    # construct_widget
    canvas = None
    for meth in ("construct_widget", "ConstructWidget"):
        fn = getattr(tree, meth, None)
        if not callable(fn):
            continue
        log("has " + meth)
        try:
            # construct_widget(Class, Name)
            canvas = fn(unreal.CanvasPanel, "RootCanvas")
            log("canvas=" + str(canvas))
        except Exception as e:
            try:
                canvas = fn(unreal.CanvasPanel)
                log("canvas2=" + str(canvas))
            except Exception as e2:
                log("construct " + str(e) + " / " + str(e2))
    if canvas is not None:
        try:
            tree.set_editor_property("root_widget", canvas)
            log("set root canvas")
        except Exception as e:
            try:
                tree.set_editor_property("RootWidget", canvas)
                log("set RootWidget canvas")
            except Exception as e2:
                log("set root ERR " + str(e) + " / " + str(e2))
        # Add Image full screen
        try:
            img = tree.construct_widget(unreal.Image, "BgImage")
            log("img=" + str(img))
            if img:
                try:
                    img.set_editor_property("color_and_opacity", unreal.LinearColor(0.05, 0.05, 0.15, 0.92))
                except Exception as e:
                    log("img color " + str(e))
                # Canvas slot
                try:
                    slot = canvas.add_child_to_canvas(img)
                    log("img slot=" + str(slot))
                    if slot:
                        slot.set_anchors(unreal.Anchors(0, 0, 1, 1))
                        slot.set_offsets(unreal.Margin(0, 0, 0, 0))
                except Exception as e:
                    log("img add " + str(e))
        except Exception as e:
            log("img construct " + str(e))
        try:
            txt = tree.construct_widget(unreal.TextBlock, "Txt_Title")
            log("txt=" + str(txt))
            if txt:
                try:
                    txt.set_editor_property("text", unreal.Text("SHOP"))
                except Exception:
                    try:
                        txt.set_text(unreal.Text("SHOP"))
                    except Exception as e:
                        log("txt text " + str(e))
                try:
                    font = txt.get_editor_property("font")
                    font.set_editor_property("size", 96)
                    txt.set_editor_property("font", font)
                except Exception as e:
                    log("font " + str(e))
                try:
                    txt.set_editor_property("color_and_opacity", unreal.SlateColor(unreal.LinearColor(1, 1, 0, 1)))
                except Exception as e:
                    log("txt color " + str(e))
                try:
                    slot = canvas.add_child_to_canvas(txt)
                    if slot:
                        slot.set_anchors(unreal.Anchors(0.5, 0.5, 0.5, 0.5))
                        slot.set_alignment(unreal.Vector2D(0.5, 0.5))
                        slot.set_offsets(unreal.Margin(-200, -50, 400, 100))
                        log("txt slotted")
                except Exception as e:
                    log("txt add " + str(e))
        except Exception as e:
            log("txt construct " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(path)
        log("saved simple")
    except Exception as e:
        log("save " + str(e))
    return bp

def patch_runtime_open_visible():
    """Rewrite open_shop section to force VISIBLE + desired size."""
    path = PYDIR + r"\shop_interact_runtime.py"
    src = open(path, "r", encoding="utf-8").read()
    marker = "try:\n        widget.add_to_viewport(100)"
    inject = """try:
        widget.set_visibility(unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(900, 600))
    except Exception:
        pass
    try:
        widget.set_alignment_in_viewport(unreal.Vector2D(0.5, 0.5))
        widget.set_position_in_viewport(unreal.Vector2D(0.5, 0.5), True)
    except Exception:
        pass
    try:
        widget.add_to_viewport(100)"""
    if "set_desired_size_in_viewport" in src:
        log("runtime already patched")
        return
    if marker not in src:
        log("marker missing, skip patch")
        return
    src2 = src.replace(marker, inject, 1)
    # Prefer ShopSimple first for visibility
    src2 = src2.replace(
        'WBP_CANDIDATES = (\n    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",\n    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",\n    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",\n)',
        'WBP_CANDIDATES = (\n    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",\n    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",\n    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",\n)',
    )
    open(path, "w", encoding="utf-8").write(src2)
    log("runtime patched")

def force_open():
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    import importlib
    import shop_interact_runtime as r
    importlib.reload(r)
    w = r._pie_world()
    log("pie=" + str(w))
    if not w:
        return False
    ok = r.open_shop(w, u"商店测试")
    log("open_shop=" + str(ok) + " w=" + str(r._OPEN_WIDGET[0]))
    wid = r._OPEN_WIDGET[0]
    if wid:
        try:
            log("vis=" + str(wid.get_visibility()))
        except Exception as e:
            log("vis err " + str(e))
        try:
            log("in_vp=" + str(wid.is_in_viewport()))
        except Exception as e:
            log("in_vp err " + str(e))
        # Force again
        try:
            wid.set_visibility(unreal.SlateVisibility.VISIBLE)
            wid.invalidate_layout_and_volatility()
        except Exception as e:
            log("force " + str(e))
    return ok

def try_reconstruct_createwidget():
    log("=== reconstruct CreateWidget ===")
    node = unreal.load_object(
        None,
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph.K2Node_CreateWidget_0",
    )
    if not node:
        log("no node")
        return
    for meth in (
        "reallocate_pins_during_reconstruction",
        "ReallocatePinsDuringReconstruction",
        "reconstruct_node",
        "ReconstructNode",
        "allocate_default_pins",
        "AllocateDefaultPins",
        "post_realloc_pins",
        "PostReallocPins",
    ):
        fn = getattr(node, meth, None)
        log("meth %s = %s" % (meth, fn))
        if callable(fn):
            try:
                fn()
                log("  called OK")
            except TypeError:
                try:
                    fn([])
                    log("  called [] OK")
                except Exception as e:
                    log("  " + str(e))
            except Exception as e:
                log("  " + str(e))
    # Try setting a Class via find_function / call_method
    for a in sorted(dir(node)):
        if "class" in a.lower() and not a.startswith("_"):
            log("attr " + a)

def main():
    log("START")
    ensure_shop_simple()
    patch_runtime_open_visible()
    try_reconstruct_createwidget()
    ok = force_open()
    log("PROOF=" + str(ok))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
