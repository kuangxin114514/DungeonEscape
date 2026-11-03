# -*- coding: utf-8 -*-
"""Open shop, paint huge runtime text onto widget tree, verify BP Create null cause,
and prefer WBP_Shop. Also list WBL methods; try native Create via call_method."""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_runtime_paint.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("PNT: " + s)
    except Exception:
        print("PNT:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def wbl_methods():
    log("=== WBL methods ===")
    cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
    log("cls=" + str(cls))
    cdo = unreal.get_default_object(cls) if cls else None
    log("cdo=" + str(cdo) + " type=" + str(type(cdo)))
    if not cdo:
        return
    names = [a for a in dir(cdo) if not a.startswith("_")]
    for a in names:
        if any(k in a.lower() for k in ("create", "widget", "viewport", "input", "focus")):
            log("  " + a)
    # try call_method
    for name in ("Create", "create", "CreateWidget"):
        try:
            r = cdo.call_method(name)
            log("call_method %s => %s" % (name, r))
        except Exception as e:
            log("call_method %s ERR %s" % (name, e))

def paint_and_open():
    log("=== paint open ===")
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    # Prefer WBP_Shop (has user text) over empty Simple
    import shop_interact_runtime as r
    # Temporarily force Shop first
    r.WBP_CANDIDATES = (
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
        "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",
    )
    importlib.reload(r)
    # reload resets WBP_CANDIDATES from file - patch file order back to Shop first
    path = PYDIR + r"\shop_interact_runtime.py"
    src = open(path, "r", encoding="utf-8").read()
    src = src.replace(
        'WBP_CANDIDATES = (\n    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",\n    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",\n    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",\n)',
        'WBP_CANDIDATES = (\n    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",\n    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",\n    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",\n)',
    )
    open(path, "w", encoding="utf-8").write(src)
    importlib.reload(r)

    w = r._pie_world()
    log("pie=" + str(w))
    if not w:
        log("NO_PIE")
        return False
    # close existing
    r.close_shop(w)
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    gc = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    log("pc=%s gc=%s" % (pc, gc))
    widget = unreal.new_object(gc, pc)
    log("widget=" + str(widget))
    if not widget:
        return False

    # Dump widget tree at RUNTIME (may not be protected)
    tree = None
    for getter in (
        lambda: widget.get_editor_property("widget_tree"),
        lambda: widget.get_editor_property("WidgetTree"),
        lambda: getattr(widget, "widget_tree", None),
        lambda: getattr(widget, "WidgetTree", None),
    ):
        try:
            tree = getter()
            if tree:
                log("tree=" + str(tree))
                break
        except Exception as e:
            log("tree get " + str(e))
    root = None
    if tree:
        for getter in (
            lambda: tree.get_editor_property("root_widget"),
            lambda: tree.get_editor_property("RootWidget"),
            lambda: getattr(tree, "root_widget", None),
            lambda: getattr(tree, "RootWidget", None),
        ):
            try:
                root = getter()
                if root is not None:
                    log("root=" + str(root) + " cls=" + root.get_class().get_name())
                    break
            except Exception as e:
                log("root get " + str(e))

    # Find all named widgets / text
    for name in ("Txt_Title", "Txt_ShopTitle", "TextBlock_0", "shop", "Text_Shop", "TextBlock_66", "Text"):
        try:
            tw = widget.get_widget_from_name(name)
            if tw:
                log("found name %s => %s" % (name, tw))
                try:
                    tw.set_text(unreal.Text(">>> SHOP <<<"))
                    log("  set_text OK")
                except Exception as e:
                    log("  set_text " + str(e))
                try:
                    tw.set_visibility(unreal.SlateVisibility.VISIBLE)
                except Exception:
                    pass
        except Exception as e:
            pass

    # Iterate ObjectIterator under widget path
    base = widget.get_path_name()
    log("widget path " + base)
    texts = []
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if base in pn or pn.startswith(base):
            texts.append(o)
            log("TextBlock " + pn)
    # Also search Image
    for o in unreal.ObjectIterator(unreal.Image):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if base in pn:
            log("Image " + pn)

    for tw in texts:
        try:
            tw.set_text(unreal.Text("SHOP UI OK"))
            tw.set_visibility(unreal.SlateVisibility.VISIBLE)
            log("painted " + tw.get_name())
        except Exception as e:
            log("paint err " + str(e))
        try:
            font = tw.get_editor_property("font")
            font.set_editor_property("size", 96)
            tw.set_editor_property("font", font)
        except Exception as e:
            try:
                # runtime Font
                tw.set_editor_property("font", unreal.SlateFontInfo())
            except Exception as e2:
                log("font " + str(e) + " / " + str(e2))

    # If NO text blocks found, try construct into tree at runtime
    if not texts and tree is not None:
        log("no texts — try runtime construct")
        for meth in ("construct_widget", "ConstructWidget"):
            fn = getattr(tree, meth, None)
            if callable(fn):
                try:
                    tb = fn(unreal.TextBlock, "RuntimeTitle")
                    log("constructed " + str(tb))
                    if tb and root and hasattr(root, "add_child"):
                        root.add_child(tb)
                except Exception as e:
                    log("construct " + str(e))

    try:
        widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        widget.add_to_viewport(200)
        widget.set_desired_size_in_viewport(unreal.Vector2D(1000, 700))
        try:
            widget.set_alignment_in_viewport(unreal.Vector2D(0.5, 0.5))
            widget.set_position_in_viewport(unreal.Vector2D(0.5, 0.5), True)
        except Exception:
            pass
        log("viewport OK")
    except Exception as e:
        log("viewport ERR " + str(e))
        return False

    try:
        pc.set_show_mouse_cursor(True)
    except Exception:
        pass
    wbl = r._wbl()
    if wbl:
        try:
            wbl.set_input_mode_game_and_ui(pc, widget, unreal.MouseLockMode.DO_NOT_LOCK, False)
        except Exception as e:
            log("input " + str(e))

    r._OPEN_WIDGET[0] = widget
    log("final vis=" + str(widget.get_visibility()) + " in_vp=" + str(widget.is_in_viewport()))
    _print_screen(w, u"商店界面已强制打开 — 应看到 SHOP")
    return True

def _print_screen(world, msg):
    try:
        unreal.KismetSystemLibrary.print_string(
            world, msg, True, True,
            unreal.LinearColor(0.2, 1.0, 0.3, 1.0), 8.0
        )
    except Exception:
        # load KismetSystemLibrary CDO
        try:
            cls = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
            cdo = unreal.get_default_object(cls)
            cdo.print_string(world, msg, True, True, unreal.LinearColor(0.2, 1, 0.3, 1), 8.0)
        except Exception as e:
            log("print " + str(e))

def probe_create_via_library(world):
    log("=== probe Create parity ===")
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    gc = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    wbl_cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
    wbl = unreal.get_default_object(wbl_cls)
    # Try every callable that might create
    for a in dir(wbl):
        if "create" in a.lower():
            fn = getattr(wbl, a)
            log("try %s callable=%s" % (a, callable(fn)))
            if not callable(fn):
                continue
            for args in (
                (pc, gc, pc),
                (world, gc, pc),
                (gc, pc),
                (pc, gc),
            ):
                try:
                    r = fn(*args)
                    log("  %s%s => %s" % (a, args, r))
                    if r:
                        return r
                except Exception as e:
                    log("  %s%s ERR %s" % (a, args, e))
    # try unreal.WidgetBlueprintLibrary static style if class methods exist
    try:
        log("unreal.WidgetBlueprintLibrary=" + str(getattr(unreal, "WidgetBlueprintLibrary", None)))
    except Exception:
        pass
    return None

def inspect_shop_asset_tree():
    log("=== WBP_Shop asset tree names ===")
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree" in pn:
            log("  " + pn + " | " + o.get_class().get_name())

def main():
    log("START")
    wbl_methods()
    inspect_shop_asset_tree()
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    import shop_interact_runtime as r
    w = r._pie_world()
    if w:
        probe_create_via_library(w)
    ok = paint_and_open()
    log("PROOF=" + str(ok))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
