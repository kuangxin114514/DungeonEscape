# -*- coding: utf-8 -*-
"""Rebuild WBP_Shop with unmistakable UI; force-open visible in PIE; diagnose CreateWidget Class."""
from __future__ import print_function
import unreal
import traceback
import sys

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_visible_shop.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("VIS: " + s)
    except Exception:
        print("VIS:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def rebuild_wbp_shop():
    """Ensure WBP_Shop has a big visible TextBlock on Canvas."""
    log("=== rebuild WBP_Shop widget tree ===")
    bp = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop")
    if not bp:
        log("NO WBP_Shop")
        return False
    # WidgetBlueprint tree API in UE4.27 Python is limited.
    # Try WidgetTree
    tree = None
    for prop in ("widget_tree", "WidgetTree"):
        try:
            tree = bp.get_editor_property(prop)
            log("tree via %s = %s" % (prop, tree))
            break
        except Exception as e:
            log("%s ERR %s" % (prop, e))
    if tree is None:
        tree = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree")
        log("tree load_object = " + str(tree))
    if tree is None:
        log("no tree")
        return False
    root = None
    for prop in ("root_widget", "RootWidget"):
        try:
            root = tree.get_editor_property(prop)
            log("root via %s = %s" % (prop, root))
        except Exception as e:
            log("root %s ERR %s" % (prop, e))
    # List all widgets in tree
    widgets = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree." in pn:
            widgets.append((pn, o))
    log("tree objs=%d" % len(widgets))
    for pn, o in widgets[:40]:
        log("  %s class=%s" % (pn.split(".")[-1], o.get_class().get_name() if hasattr(o, "get_class") else "?"))
    # Find TextBlock and force properties
    for pn, o in widgets:
        cname = o.get_class().get_name() if hasattr(o, "get_class") else ""
        if "Text" in cname:
            log("patching text " + pn)
            try:
                o.set_editor_property("text", unreal.Text("SHOP OPEN"))
                log("  text set")
            except Exception as e:
                try:
                    # FText via string
                    o.set_editor_property("text", "SHOP OPEN")
                    log("  text set str")
                except Exception as e2:
                    log("  text ERR %s / %s" % (e, e2))
            for prop, val in (
                ("color_and_opacity", None),
            ):
                pass
            # Font size via font info
            try:
                font = o.get_editor_property("font")
                log("  font=" + str(font))
                try:
                    font.set_editor_property("size", 72)
                    o.set_editor_property("font", font)
                    log("  font size 72")
                except Exception as e:
                    log("  font size ERR " + str(e))
            except Exception as e:
                log("  font get ERR " + str(e))
            try:
                o.set_editor_property("visibility", unreal.SlateVisibility.VISIBLE)
            except Exception as e:
                log("  vis ERR " + str(e))
    # Save
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/UI/Shop/WBP_Shop")
        log("saved WBP_Shop")
    except Exception as e:
        log("save ERR " + str(e))
    return True

def force_open_visible():
    log("=== force open visible shop ===")
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    import importlib
    import shop_interact_runtime as r
    importlib.reload(r)
    w = r._pie_world()
    log("pie=" + str(w))
    if not w:
        log("NO_PIE — start PIE first")
        return False
    # Close existing
    try:
        if r._OPEN_WIDGET[0]:
            r._OPEN_WIDGET[0].remove_from_parent()
            r._OPEN_WIDGET[0] = None
    except Exception:
        pass
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    gc = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    log("pc=%s gc=%s" % (pc, gc))
    widget = unreal.new_object(gc, outer=pc)
    log("widget=" + str(widget))
    if not widget:
        return False
    # Force visibility VISIBLE on root
    try:
        widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        log("set_visibility VISIBLE")
    except Exception as e:
        log("set_vis ERR " + str(e))
    try:
        widget.set_is_enabled(True)
    except Exception:
        pass
    try:
        widget.add_to_viewport(100)
        log("add_to_viewport 100")
    except Exception as e:
        log("add ERR " + str(e))
        return False
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(800, 600))
        log("desired size set")
    except Exception as e:
        log("desired ERR " + str(e))
    try:
        widget.set_alignment_in_viewport(unreal.Vector2D(0.5, 0.5))
        widget.set_position_in_viewport(unreal.Vector2D(960, 540), True)
        log("pos center")
    except Exception as e:
        log("pos ERR " + str(e))
    try:
        pc.b_show_mouse_cursor = True
        unreal.WidgetBlueprintLibrary.set_input_mode_ui_only_ex(pc, widget)
        log("input UI only")
    except Exception as e:
        log("input ERR " + str(e))
    # Walk children and force text visible
    try:
        # get_all_widgets / widget tree at runtime
        for meth in ("get_all_children", "GetAllChildren"):
            pass
        root = widget.get_root_widget() if hasattr(widget, "get_root_widget") else None
        log("runtime root=" + str(root))
    except Exception as e:
        log("root runtime ERR " + str(e))
    # Check visibility after
    try:
        log("final vis=" + str(widget.get_visibility()))
        log("is_in_viewport=" + str(widget.is_in_viewport() if hasattr(widget, "is_in_viewport") else "?"))
    except Exception as e:
        log("check ERR " + str(e))
    r._OPEN_WIDGET[0] = widget
    return True

def diagnose_createwidget_node_export():
    """Export CreateWidget node via ObjectExporter or AssetRegistry tags."""
    log("=== CreateWidget node dump ===")
    node = unreal.load_object(
        None,
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph.K2Node_CreateWidget_0",
    )
    log("node=" + str(node))
    if not node:
        return
    # dir filtered
    for a in sorted(dir(node)):
        if a.startswith("_"):
            continue
        if any(k in a.lower() for k in ("class", "pin", "widget", "default", "export", "alloc")):
            try:
                v = getattr(node, a)
                if callable(v):
                    log("  meth " + a)
                else:
                    log("  %s=%s" % (a, v))
            except Exception as e:
                log("  %s ERR %s" % (a, e))
    # Try export_text
    try:
        # unreal.Exporter?
        for name in dir(unreal):
            if "Export" in name:
                log("export api " + name)
    except Exception:
        pass
    # Copy properties via get_editor_property known C++ names from K2Node_CreateWidget
    for p in (
        "class_requiring_game_mode_base",
        "CustomProperties",
        "node_comment",
        "node_guid",
        "node_pos_x",
        "node_pos_y",
        "enabled_state",
        "error_type",
    ):
        try:
            log("prop %s=%s" % (p, node.get_editor_property(p)))
        except Exception as e:
            log("prop %s ERR %s" % (p, e))

def try_compile_widget_and_character():
    log("=== compile assets ===")
    for path in (
        "/Game/UI/Shop/WBP_Shop",
        "/Game/UI/Shop/WBP_Shop2",
        "/Game/Characters/Player/KayKit/BP_KayKitKnight",
    ):
        try:
            ok = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
            log("save %s => %s" % (path, ok))
        except Exception as e:
            log("save %s ERR %s" % (path, e))
    # Blueprint compile via subsystem if available
    try:
        sub = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        log("AssetEditorSubsystem=" + str(sub))
    except Exception as e:
        log("AES ERR " + str(e))

def main():
    log("START")
    diagnose_createwidget_node_export()
    rebuild_wbp_shop()
    try_compile_widget_and_character()
    ok = force_open_visible()
    log("FORCE_OPEN=" + str(ok))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
