# -*- coding: utf-8 -*-
"""Fix: use WidgetBlueprintLibrary.create via call_method so WidgetTree initializes.
Prove TextBlock_0 exists and is visible. Patch shop_interact_runtime.open_shop."""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_create_real.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("CR: " + s)
    except Exception:
        print("CR:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def get_wbl():
    cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
    return unreal.get_default_object(cls) if cls else None

def create_widget_proper(world, wcls, pc):
    """Create UserWidget with initialized WidgetTree (not new_object)."""
    wbl = get_wbl()
    if not wbl:
        log("no wbl")
        return None
    attempts = []
    # kwargs style
    attempts.append(("kw1", lambda: wbl.call_method(
        "create",
        (),
        {
            "world_context_object": world,
            "widget_type": wcls,
            "owning_player": pc,
        },
    )))
    attempts.append(("kw2", lambda: wbl.call_method(
        "create",
        (),
        {
            "world_context_object": pc,
            "widget_type": wcls,
            "owning_player": pc,
        },
    )))
    # tuple args
    attempts.append(("t1", lambda: wbl.call_method("create", (world, wcls, pc))))
    attempts.append(("t2", lambda: wbl.call_method("create", (pc, wcls, pc))))
    # Create capital C
    attempts.append(("Ckw", lambda: wbl.call_method(
        "Create",
        (),
        {
            "world_context_object": world,
            "widget_type": wcls,
            "owning_player": pc,
        },
    )))
    for name, fn in attempts:
        try:
            w = fn()
            log("%s => %s" % (name, w))
            if w:
                return w
        except Exception as e:
            log("%s ERR %s" % (name, e))
    return None

def count_children(widget):
    base = widget.get_path_name()
    texts, images, allc = [], [], []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if base + "." in pn or (base in pn and pn != base):
            allc.append(pn)
            cn = o.get_class().get_name()
            if "Text" in cn:
                texts.append(o)
            if cn == "Image":
                images.append(o)
    log("children=%d texts=%d images=%d" % (len(allc), len(texts), len(images)))
    for pn in allc[:30]:
        log("  ch " + pn)
    return texts

def patch_runtime():
    path = PYDIR + r"\shop_interact_runtime.py"
    src = open(path, "r", encoding="utf-8").read()
    if "call_method(\"create\"" in src or "call_method('create'" in src:
        log("runtime already has call_method create")
        return
    old = '''    # Prefer new_object: WidgetBlueprintLibrary.create is flaky / missing in py bindings
    widget = None
    try:
        widget = unreal.new_object(wcls, pc)
    except Exception as e:
        _log("new_object err " + str(e))
    if not widget:
        wbl = _wbl()
        if wbl:
            for args in (
                lambda: wbl.create(pc, wcls, pc),
                lambda: wbl.create(world_ctx, wcls, pc),
            ):
                try:
                    widget = args()
                    if widget:
                        break
                except Exception as e:
                    _log("wbl.create " + str(e))'''
    new = '''    # CRITICAL: must use WidgetBlueprintLibrary.create (via call_method).
    # unreal.new_object skips WidgetTree init => empty invisible widget.
    widget = None
    wbl = _wbl()
    if wbl:
        for attempt in (
            lambda: wbl.call_method(
                "create", (),
                {"world_context_object": world_ctx, "widget_type": wcls, "owning_player": pc},
            ),
            lambda: wbl.call_method(
                "create", (),
                {"world_context_object": pc, "widget_type": wcls, "owning_player": pc},
            ),
            lambda: wbl.call_method("create", (world_ctx, wcls, pc)),
            lambda: wbl.call_method("create", (pc, wcls, pc)),
        ):
            try:
                widget = attempt()
                if widget:
                    _log("create OK via call_method")
                    break
            except Exception as e:
                _log("call_method create " + str(e))
    if not widget:
        try:
            widget = unreal.new_object(wcls, pc)
            _log("fallback new_object (tree may be empty)")
        except Exception as e:
            _log("new_object err " + str(e))'''
    if old not in src:
        log("OLD BLOCK NOT FOUND — manual patch needed")
        # write helper file instead
        open(PYDIR + r"\create_widget_fix.py", "w", encoding="utf-8").write(
            "OLD_MISSING\n"
        )
        return False
    src2 = src.replace(old, new, 1)
    # also ensure visibility after add_to_viewport
    if "set_desired_size_in_viewport" not in src2:
        src2 = src2.replace(
            "try:\n        widget.add_to_viewport(100)",
            "try:\n        widget.set_visibility(unreal.SlateVisibility.VISIBLE)\n"
            "    except Exception:\n        pass\n"
            "    try:\n        widget.add_to_viewport(100)",
        )
    open(path, "w", encoding="utf-8").write(src2)
    log("runtime patched with call_method create")
    return True

def also_fix_textblock_slot():
    """Ensure TextBlock_0 slot is centered with size on the asset."""
    slot = unreal.load_object(
        None,
        "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree.CanvasPanel_0.CanvasPanelSlot_0",
    )
    # find which slot owns TextBlock_0
    log("slot0=" + str(slot))
    tb = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree.TextBlock_0")
    log("tb=" + str(tb))
    if tb:
        try:
            tb.set_editor_property("text", unreal.Text("SHOP"))
            log("asset text=SHOP")
        except Exception as e:
            log("asset text ERR " + str(e))
        try:
            font = tb.get_editor_property("font")
            font.set_editor_property("size", 96)
            tb.set_editor_property("font", font)
            log("asset font 96")
        except Exception as e:
            log("font ERR " + str(e))
        try:
            tb.set_editor_property(
                "color_and_opacity",
                unreal.SlateColor(unreal.LinearColor(1.0, 0.95, 0.1, 1.0)),
            )
            log("asset color yellow")
        except Exception as e:
            log("color ERR " + str(e))
    # Find slot content
    for i in range(8):
        s = unreal.load_object(
            None,
            "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree.CanvasPanel_0.CanvasPanelSlot_%d" % i,
        )
        if not s:
            continue
        try:
            content = s.get_editor_property("content")
        except Exception:
            try:
                content = s.get_editor_property("Content")
            except Exception as e:
                log("slot%d content ERR %s" % (i, e))
                continue
        log("slot%d content=%s" % (i, content))
        if content and "TextBlock" in str(content):
            try:
                s.set_anchors(unreal.Anchors(0.5, 0.5, 0.5, 0.5))
                s.set_alignment(unreal.Vector2D(0.5, 0.5))
                s.set_offsets(unreal.Margin(-300, -80, 600, 160))
                s.set_auto_size(True)
                log("slot%d centered" % i)
            except Exception as e:
                log("slot%d layout ERR %s" % (i, e))
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/UI/Shop/WBP_Shop")
        log("saved WBP_Shop")
    except Exception as e:
        log("save " + str(e))

def main():
    log("START")
    also_fix_textblock_slot()
    patch_runtime()

    # Find PIE world
    world = None
    for o in unreal.ObjectIterator(unreal.World):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "UEDPIE" in pn and "Map_Hub" in pn:
            world = o
            break
    log("pie=" + str(world))
    if not world:
        log("NO_PIE")
        flush()
        return

    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    wcls = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    log("pc=%s wcls=%s" % (pc, wcls))

    # Compare new_object vs create
    wo = unreal.new_object(wcls, pc)
    log("new_object=" + str(wo))
    if wo:
        count_children(wo)
        try:
            wo.remove_from_parent()
        except Exception:
            pass

    widget = create_widget_proper(world, wcls, pc)
    log("proper=" + str(widget))
    if not widget:
        log("CREATE FAILED")
        flush()
        return
    texts = count_children(widget)
    for tw in texts:
        try:
            tw.set_text(unreal.Text("SHOP OPEN"))
            tw.set_visibility(unreal.SlateVisibility.VISIBLE)
            log("set text on " + tw.get_name())
        except Exception as e:
            log("set text ERR " + str(e))
    # also by name
    for name in ("TextBlock_0", "Txt_Title"):
        try:
            t = widget.get_widget_from_name(name)
            log("get_widget_from_name %s => %s" % (name, t))
            if t:
                t.set_text(unreal.Text("SHOP OPEN"))
        except Exception as e:
            log("gwf %s %s" % (name, e))

    try:
        widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        widget.add_to_viewport(250)
        log("on viewport")
    except Exception as e:
        log("vp ERR " + str(e))
    try:
        pc.set_show_mouse_cursor(True)
    except Exception:
        pass
    wbl = get_wbl()
    if wbl:
        try:
            wbl.set_input_mode_ui_only_ex(pc, widget)
            log("ui only ex")
        except Exception as e:
            log("ui only " + str(e))

    # Reload runtime and open_shop
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    import shop_interact_runtime as r
    importlib.reload(r)
    # store as open
    try:
        if r._OPEN_WIDGET[0]:
            r._OPEN_WIDGET[0].remove_from_parent()
    except Exception:
        pass
    r._OPEN_WIDGET[0] = widget
    ok2 = r.open_shop(world, u"武器店")
    log("open_shop after patch=" + str(ok2) + " w=" + str(r._OPEN_WIDGET[0]))
    if r._OPEN_WIDGET[0]:
        count_children(r._OPEN_WIDGET[0])
        log("vis=" + str(r._OPEN_WIDGET[0].get_visibility()))
        log("invp=" + str(r._OPEN_WIDGET[0].is_in_viewport()))

    log("PROOF_PROPER_CREATE=" + str(widget is not None))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
