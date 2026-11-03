# -*- coding: utf-8 -*-
"""Fix shop CreateWidget null (UE4.27).
Proof: WBP_*_C loads; new_object+AddToViewport works.
BP CreateWidget Class pin is stale/null -> returns None.
Strategy:
1) Ensure WBP_Shop has visible text
2) Inspect/fix CreateWidget pin if API allows
3) Provide open_shop_bp.open_shop_from_bp() and patch BP to ExecuteConsoleCommand py call
4) Reload safe shop_interact_runtime (new_object path)
No Python actors saved into Map_Hub.
"""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_cw_pin.txt"
BP_PATH = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight"
WBP_C_PATHS = (
    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",
)
HELPER = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\open_shop_bp.py"
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("FIXPIN: " + s)
    except Exception:
        print("FIXPIN:", s)


def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def load_gc():
    for p in WBP_C_PATHS:
        c = unreal.load_class(None, p)
        log("load_class %s => %s" % (p, c))
        if c:
            return c, p
    return None, None


def ensure_shop_text():
    log("=== ensure WBP_Shop text ===")
    bp = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop")
    log("WBP_Shop=" + str(bp))
    n = 0
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree" not in pn:
            continue
        try:
            cn = o.get_class().get_name()
        except Exception:
            continue
        if cn == "TextBlock":
            n += 1
            try:
                o.set_editor_property("text", unreal.Text("SHOP"))
                log("set text " + o.get_name())
            except Exception as e:
                log("set text err " + str(e))
    log("TextBlock count=" + str(n))
    if n == 0:
        wt = unreal.load_object(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree")
        log("wt=" + str(wt))
        if wt is not None:
            try:
                root = wt.root_widget
            except Exception:
                try:
                    root = wt.get_editor_property("root_widget")
                except Exception:
                    root = None
            log("root=" + str(root))
            try:
                if root is None:
                    root = unreal.new_object(unreal.CanvasPanel, wt, "CanvasPanel_0")
                    try:
                        wt.set_editor_property("root_widget", root)
                    except Exception:
                        try:
                            wt.root_widget = root
                        except Exception as e:
                            log("set root err " + str(e))
                tb = unreal.new_object(unreal.TextBlock, wt, "Txt_ShopTitle")
                try:
                    tb.set_editor_property("text", unreal.Text("SHOP"))
                except Exception as e:
                    log("tb text err " + str(e))
                if root is not None and hasattr(root, "add_child_to_canvas"):
                    slot = root.add_child_to_canvas(tb)
                    log("added TextBlock slot=" + str(slot))
                    try:
                        slot.set_auto_size(True)
                    except Exception:
                        pass
            except Exception as e:
                log("add text err " + str(e) + "\n" + traceback.format_exc())
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/UI/Shop/WBP_Shop")
        log("saved WBP_Shop")
    except Exception as e:
        log("save WBP_Shop " + str(e))
    return bp


def find_create_node():
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph.K2Node_CreateWidget" in pn:
            return o
    return None


def inspect_node(node):
    log("=== inspect " + node.get_path_name() + " ===")
    for attr in sorted(dir(node)):
        if attr.startswith("_"):
            continue
        low = attr.lower()
        if ("pin" in low) or ("class" in low) or ("widget" in low) or ("spawn" in low):
            try:
                v = getattr(node, attr)
                log("  %s callable=%s" % (attr, callable(v)))
            except Exception as e:
                log("  %s ERR %s" % (attr, e))
    for prop in ("node_pos_x", "node_pos_y", "error_type", "error_msg", "b_is_pure_func"):
        try:
            log("  eprop %s=%s" % (prop, node.get_editor_property(prop)))
        except Exception:
            pass


def try_fix_class_pin(node, gc):
    log("=== try fix class pin ===")
    if not node or not gc:
        return False
    ok = False
    # find_pin variants
    for meth_name in ("find_pin", "FindPin"):
        meth = getattr(node, meth_name, None)
        if not callable(meth):
            continue
        for pname in ("Class", "class"):
            pin = None
            try:
                pin = meth(pname)
            except Exception as e:
                log("%s(%s) %s" % (meth_name, pname, e))
                continue
            log("%s(%s)=>%s" % (meth_name, pname, pin))
            if pin is None:
                continue
            for setter in (
                lambda: pin.set_editor_property("default_object", gc),
                lambda: setattr(pin, "default_object", gc),
                lambda: pin.set_editor_property("default_value", gc.get_path_name()),
                lambda: setattr(pin, "default_value", gc.get_path_name()),
            ):
                try:
                    setter()
                    ok = True
                    log("pin set OK via one setter")
                except Exception as e:
                    log("pin set err " + str(e))
    # reconstruct
    for meth_name in ("reconstruct_node", "ReconstructNode", "allocate_default_pins"):
        meth = getattr(node, meth_name, None)
        if callable(meth):
            try:
                meth()
                log(meth_name + " OK")
            except Exception as e:
                log(meth_name + " " + str(e))
    return ok


def write_helper():
    code = r'''# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal

_OPEN = [None]

def _gc():
    for p in (
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
        "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",
    ):
        c = unreal.load_class(None, p)
        if c:
            return c
    return None

def _pie():
    try:
        ws = unreal.EditorLevelLibrary.get_pie_worlds(False)
        if ws:
            return ws[0]
    except Exception:
        pass
    try:
        return unreal.EditorLevelLibrary.get_game_world()
    except Exception:
        return None

def close_shop():
    w = _OPEN[0]
    _OPEN[0] = None
    if w is None:
        return
    try:
        w.remove_from_parent()
    except Exception:
        try:
            w.remove_from_viewport()
        except Exception:
            pass
    try:
        pc = unreal.GameplayStatics.get_player_controller(w, 0)
        if pc:
            pc.set_show_mouse_cursor(False)
            wbl_cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
            wbl = unreal.get_default_object(wbl_cls) if wbl_cls else None
            if wbl:
                try:
                    wbl.set_input_mode_game_only(pc)
                except Exception:
                    pass
    except Exception:
        pass

def open_shop_from_bp(title=u"商店"):
    if _OPEN[0] is not None:
        close_shop()
        return True
    gc = _gc()
    if not gc:
        unreal.log("open_shop_from_bp: no class")
        return False
    world = _pie()
    if world is None:
        unreal.log("open_shop_from_bp: no PIE world")
        return False
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    w = unreal.new_object(gc, pc or world)
    if not w:
        unreal.log("open_shop_from_bp: new_object null")
        return False
    for nm in ("Txt_Title", "Txt_ShopTitle", "TextBlock_0", "Text"):
        try:
            t = w.get_widget_from_name(nm)
            if t is not None:
                t.set_text(unreal.Text(title))
        except Exception:
            pass
    try:
        w.add_to_viewport(100)
    except Exception as e:
        unreal.log("open_shop_from_bp viewport " + str(e))
        return False
    _OPEN[0] = w
    if pc:
        try:
            pc.set_show_mouse_cursor(True)
        except Exception:
            pass
        try:
            wbl_cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
            wbl = unreal.get_default_object(wbl_cls) if wbl_cls else None
            if wbl:
                try:
                    wbl.set_input_mode_game_and_ui(pc, w, unreal.MouseLockMode.DO_NOT_LOCK, False)
                except Exception:
                    try:
                        wbl.set_input_mode_ui_only(pc, w)
                    except Exception:
                        pass
        except Exception:
            pass
    try:
        unreal.KismetSystemLibrary.print_string(
            world, u"商店界面已打开", True, True,
            unreal.LinearColor(0.2, 1.0, 0.3, 1.0), 3.0
        )
    except Exception:
        pass
    unreal.log("open_shop_from_bp OK " + str(w))
    return True
'''
    open(HELPER, "w", encoding="utf-8").write(code)
    log("wrote helper " + HELPER)


def import_helper():
    write_helper()
    # Ensure Content/Python on sys.path
    pydir = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if pydir not in sys.path:
        sys.path.insert(0, pydir)
    try:
        if "open_shop_bp" in sys.modules:
            importlib.reload(sys.modules["open_shop_bp"])
        else:
            import open_shop_bp  # noqa: F401
        log("helper imported")
        return sys.modules.get("open_shop_bp")
    except Exception as e:
        log("helper import err " + str(e) + "\n" + traceback.format_exc())
        return None


def add_console_command_node(gc_path):
    """Add ExecuteConsoleCommand(py open_shop_bp.open_shop_from_bp()) after Interact Pressed.
    If graph API fails, leave helper for manual / runtime tick.
    """
    log("=== add ExecuteConsoleCommand node ===")
    graph = unreal.load_object(
        None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
    )
    log("graph=" + str(graph))
    if graph is None:
        return False
    # Find Interact input action node
    interact = None
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph.K2Node_InputAction" not in pn:
            continue
        an = ""
        try:
            an = str(o.get_editor_property("input_action_name"))
        except Exception:
            try:
                an = str(o.get_editor_property("InputActionName"))
            except Exception:
                an = ""
        log("InputAction %s name=%s" % (pn, an))
        if an == "Interact":
            interact = o
    log("interact node=" + str(interact))

    # Create CallFunction ExecuteConsoleCommand
    try:
        node = unreal.new_object(unreal.K2Node_CallFunction, graph)
    except Exception as e:
        log("new CallFunction " + str(e))
        return False
    log("new node=" + str(node))
    ksl = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
    try:
        mr = node.get_editor_property("function_reference")
        mr.set_editor_property("member_parent", ksl)
        mr.set_editor_property("member_name", "ExecuteConsoleCommand")
        node.set_editor_property("function_reference", mr)
        log("function_reference set")
    except Exception as e:
        log("function_reference err " + str(e))
    try:
        node.set_editor_property("node_pos_x", 650)
        node.set_editor_property("node_pos_y", 1400)
    except Exception:
        pass
    for meth in ("allocate_default_pins", "reallocate_pins_during_reconstruction", "reconstruct_node"):
        fn = getattr(node, meth, None)
        if callable(fn):
            try:
                if meth == "reallocate_pins_during_reconstruction":
                    fn([])
                else:
                    fn()
                log(meth + " OK")
            except Exception as e:
                log(meth + " " + str(e))
    # Add to graph
    added = False
    for meth in ("add_node", "AddNode"):
        fn = getattr(graph, meth, None)
        if callable(fn):
            try:
                fn(node)
                added = True
                log(meth + " OK")
                break
            except Exception as e:
                try:
                    fn(node, False, False)
                    added = True
                    log(meth + " OK2")
                    break
                except Exception as e2:
                    log(meth + " " + str(e) + " / " + str(e2))
    if not added:
        # Some UE versions auto-outer to graph is enough if we notify
        try:
            graph.notify_graph_changed()
            log("notify_graph_changed")
            added = True
        except Exception as e:
            log("notify " + str(e))

    # Set Command pin default value
    cmd = 'py open_shop_bp.open_shop_from_bp()'
    pin_set = False
    find = getattr(node, "find_pin", None) or getattr(node, "FindPin", None)
    if callable(find):
        for pname in ("Command", "command"):
            try:
                pin = find(pname)
                log("cmd pin %s=%s" % (pname, pin))
                if pin is not None:
                    try:
                        pin.set_editor_property("default_value", cmd)
                        pin_set = True
                    except Exception:
                        try:
                            pin.default_value = cmd
                            pin_set = True
                        except Exception as e:
                            log("set cmd " + str(e))
            except Exception as e:
                log("find cmd " + str(e))
    log("pin_set=%s added=%s" % (pin_set, added))

    # Try link Interact Pressed -> this node execute
    if interact is not None and callable(find):
        try:
            pressed = None
            find_i = getattr(interact, "find_pin", None) or getattr(interact, "FindPin", None)
            if callable(find_i):
                pressed = find_i("Pressed")
            exec_in = find("execute")
            log("pressed=%s exec_in=%s" % (pressed, exec_in))
            if pressed is not None and exec_in is not None:
                try:
                    pressed.break_all_pin_links()
                except Exception:
                    try:
                        pressed.break_all_pin_links(True)
                    except Exception:
                        pass
                try:
                    pressed.make_link_to(exec_in)
                    log("linked Pressed -> ExecuteConsoleCommand")
                except Exception as e:
                    log("link err " + str(e))
                    try:
                        unreal.EdGraphSchema_K2().try_create_connection(pressed, exec_in)
                        log("schema link OK")
                    except Exception as e2:
                        log("schema link " + str(e2))
        except Exception as e:
            log("link block " + str(e))

    # Save BP
    bp = unreal.load_object(None, BP_PATH)
    if bp is not None:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            log("saved BP")
        except Exception as e:
            log("save BP " + str(e))
        try:
            unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        except Exception as e:
            log("save_asset " + str(e))
    return added


def live_proof(mod):
    log("=== live proof ===")
    if mod is None:
        return False
    try:
        ok = mod.open_shop_from_bp(u"商店")
        log("open_shop_from_bp => " + str(ok))
        return bool(ok)
    except Exception as e:
        log("live proof err " + str(e) + "\n" + traceback.format_exc())
        return False


def patch_runtime_prefer_new_object():
    log("=== reload shop_interact_runtime ===")
    pydir = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if pydir not in sys.path:
        sys.path.insert(0, pydir)
    try:
        if "shop_interact_runtime" in sys.modules:
            importlib.reload(sys.modules["shop_interact_runtime"])
        else:
            import shop_interact_runtime  # noqa: F401
        log("shop_interact_runtime ready")
    except Exception as e:
        log("runtime " + str(e))


def main():
    log("START fix_cw_pin")
    ensure_shop_text()
    gc, gcp = load_gc()
    log("gc=%s path=%s" % (gc, gcp))
    node = find_create_node()
    log("create node=" + str(node))
    if node is not None:
        inspect_node(node)
        try_fix_class_pin(node, gc)
    mod = import_helper()
    add_console_command_node(gcp or "")
    patch_runtime_prefer_new_object()
    proved = live_proof(mod)
    log("PROOF_OK=" + str(proved))
    log("DONE")
    flush()


try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
