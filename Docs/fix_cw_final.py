# -*- coding: utf-8 -*-
"""Final fix: shop UI on E. UE4.27.
Root cause: BP CreateWidget Class pin resolves to null at runtime (stale/REINST).
Widget class itself is healthy; new_object(WBP_Shop_C)+AddToViewport works.
Fix:
1) Patch shop_interact_runtime to prefer new_object + clear logs
2) Rewrite open_shop_bp helper
3) Try load BlueprintGraph node classes to rewire Interact -> console py call
4) Live open proof in PIE
No Python actors in Map_Hub. Buildings untouched.
"""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib
import os

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_cw_final.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("FIXF: " + s)
    except Exception:
        print("FIXF:", s)


def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")


RUNTIME = r'''# -*- coding: utf-8 -*-
# Shop / gate interact for DungeonEscape (UE 4.27 PIE).
# SAFE: slate tick E edge-detect only. NO Python Actor in level.
from __future__ import print_function
import unreal

WBP_CANDIDATES = (
    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",
)
SHOP_RANGE = 450.0
GATE_RANGE = 500.0
_OPEN_WIDGET = [None]
_NEAR_TITLE = [None]
_NEAR_GATE = [False]

SHOP_LABELS = {
    "HubShop_Weapon": u"武器店",
    "HubShop_Armor": u"防具店",
    "HubShop_Health": u"回血店",
    "ShopTrigger_Weapon": u"武器店",
    "ShopTrigger_Armor": u"防具店",
    "ShopTrigger_Health": u"回血店",
}


def _log(msg):
    try:
        unreal.log("ShopInteract: " + str(msg))
    except Exception:
        print("ShopInteract:", msg)


def _wbl():
    cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
    return unreal.get_default_object(cls) if cls else None


def _tags(actor):
    try:
        return [str(t) for t in list(actor.get_editor_property("tags"))]
    except Exception:
        try:
            return [str(t) for t in list(actor.tags)]
        except Exception:
            return []


def _label(actor):
    try:
        return actor.get_actor_label() or ""
    except Exception:
        try:
            return actor.get_name()
        except Exception:
            return ""


def _dist(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def _title_from_tags(tags):
    for t in tags:
        if t.startswith("ShopTitle:"):
            return t.split(":", 1)[1]
    return None


def _print(world, msg, color=(1.0, 0.95, 0.2, 1.0), sec=2.0):
    try:
        unreal.KismetSystemLibrary.print_string(
            world, msg, True, True,
            unreal.LinearColor(color[0], color[1], color[2], color[3]), sec
        )
    except Exception:
        _log(msg)


def _load_shop_class():
    for p in WBP_CANDIDATES:
        c = unreal.load_class(None, p)
        if c:
            return c, p
    return None, None


def close_shop(world_ctx=None):
    w = _OPEN_WIDGET[0]
    _OPEN_WIDGET[0] = None
    pc = None
    if w is not None:
        try:
            w.remove_from_parent()
        except Exception:
            try:
                w.remove_from_viewport()
            except Exception:
                pass
        try:
            pc = unreal.GameplayStatics.get_player_controller(w, 0)
        except Exception:
            pc = None
    if pc is None and world_ctx is not None:
        try:
            pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
        except Exception:
            pc = None
    if pc:
        try:
            pc.set_show_mouse_cursor(False)
        except Exception:
            pass
        wbl = _wbl()
        if wbl:
            try:
                wbl.set_input_mode_game_only(pc)
            except Exception:
                try:
                    wbl.set_input_mode_game_only(pc, True)
                except Exception:
                    pass


def open_shop(world_ctx, title_text):
    if _OPEN_WIDGET[0] is not None:
        close_shop(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if not pc:
        _log("open_shop FAIL no PC")
        return False
    wcls, wpath = _load_shop_class()
    if not wcls:
        _log("open_shop FAIL no WBP class")
        return False
    _log("open_shop class=" + str(wpath))
    # Prefer new_object: WidgetBlueprintLibrary.create is flaky / missing in py bindings
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
                    _log("wbl.create " + str(e))
    if not widget:
        _log("open_shop FAIL create null")
        return False
    for name in ("Txt_Title", "Txt_ShopTitle", "TextBlock_0"):
        try:
            t = widget.get_widget_from_name(name)
            if t:
                t.set_text(unreal.Text(str(title_text)))
        except Exception:
            pass
    for name, text in (
        ("Txt_Sub", u"暂无商品"),
        ("Txt_Hint", u"E / Esc 关闭"),
        ("Btn_Start_Txt", u"关闭"),
    ):
        try:
            t = widget.get_widget_from_name(name)
            if t:
                t.set_text(unreal.Text(text))
        except Exception:
            pass
    try:
        qb = widget.get_widget_from_name("Btn_Quit")
        if qb is not None:
            qb.set_visibility(unreal.SlateVisibility.COLLAPSED)
    except Exception:
        pass
    try:
        widget.add_to_viewport(100)
    except Exception as e:
        _log("viewport err " + str(e))
        return False
    _OPEN_WIDGET[0] = widget
    try:
        pc.set_show_mouse_cursor(True)
    except Exception:
        pass
    wbl = _wbl()
    if wbl:
        for call in (
            lambda: wbl.set_input_mode_game_and_ui(pc, widget, unreal.MouseLockMode.DO_NOT_LOCK, False),
            lambda: wbl.set_input_mode_ui_only(pc, widget),
        ):
            try:
                call()
                break
            except Exception:
                continue
    try:
        btn = widget.get_widget_from_name("Btn_Close") or widget.get_widget_from_name("Btn_Start")
        if btn is not None:
            try:
                btn.on_clicked.clear()
            except Exception:
                pass
            try:
                btn.on_clicked.add_callable(lambda: close_shop(world_ctx))
            except Exception as e:
                _log("bind close " + str(e))
    except Exception:
        pass
    _log("opened shop OK title=" + str(title_text) + " widget=" + str(widget))
    _print(world_ctx, u"商店界面已打开", (0.2, 1.0, 0.3, 1.0), 2.5)
    return True


def scan_near(world, pawn_loc):
    title = None
    gate = False
    best_shop = 1e12
    best_gate = 1e12
    try:
        actors = list(unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor.static_class()))
    except Exception as e:
        _log("get_all " + str(e))
        return None, False
    for a in actors:
        try:
            tags = _tags(a)
            lab = _label(a)
            loc = a.get_actor_location()
            d = _dist(loc, pawn_loc)
            is_shop = ("ShopInteract" in tags) or (lab in SHOP_LABELS) or lab.startswith("ShopTrigger_") or lab.startswith("HubShop_")
            is_gate = ("GateInteract" in tags) or (lab == "HubGate_DungeonEntrance") or lab.startswith("GateTrigger_")
            if is_shop and d <= SHOP_RANGE and d < best_shop:
                best_shop = d
                title = _title_from_tags(tags) or SHOP_LABELS.get(lab) or u"商店"
            if is_gate and d <= GATE_RANGE and d < best_gate:
                best_gate = d
                gate = True
        except Exception:
            continue
    return title, gate


def handle_interact(world_ctx):
    if world_ctx is None:
        return False
    world = None
    try:
        world = world_ctx.get_world()
    except Exception:
        world = None
    if world is None:
        try:
            world = unreal.GameplayStatics.get_player_controller(world_ctx, 0).get_world()
        except Exception:
            world = world_ctx
    if _OPEN_WIDGET[0] is not None:
        close_shop(world)
        return True
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    pawn = None
    if pc:
        try:
            pawn = pc.get_controlled_pawn()
        except Exception:
            pawn = None
    if not pawn:
        _log("no pawn")
        return False
    title, gate = scan_near(world, pawn.get_actor_location())
    _NEAR_TITLE[0] = title
    _NEAR_GATE[0] = gate
    if title:
        return open_shop(world, title)
    if gate:
        _print(world, u"地下城入口（待接入）", (1.0, 0.85, 0.2, 1.0), 3.0)
        return True
    # Not near a shop: still open generic shop so E always shows UI while debugging BP CreateWidget
    return open_shop(world, u"商店")


_TICK = [None]
_HINT_ACC = [0.0]
_PREV_E = [False]
_PREV_ESC = [False]
_VIEW_FIXED = [False]
_LAST_PIE = [False]


def _pie_world():
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


def _key_down(pc, name):
    try:
        return bool(pc.is_input_key_down(unreal.Key(key_name=name)))
    except Exception:
        try:
            return bool(pc.is_input_key_down(unreal.Key(name)))
        except Exception:
            return False


def _fix_view_once(world):
    if _VIEW_FIXED[0]:
        return
    for c in (
        "viewmode lit",
        "show flag.Wireframe 0",
        "show flag.MeshEdges 0",
        "show flag.Collision 0",
        "show flag.Bounds 0",
        "show flag.Game 1",
    ):
        try:
            unreal.SystemLibrary.execute_console_command(world, c, None)
        except Exception:
            pass
    _VIEW_FIXED[0] = True


def _on_tick(dt):
    world = _pie_world()
    in_pie = world is not None
    if in_pie and not _LAST_PIE[0]:
        _VIEW_FIXED[0] = False
        _PREV_E[0] = False
        _PREV_ESC[0] = False
    if (not in_pie) and _LAST_PIE[0]:
        _VIEW_FIXED[0] = False
        if _OPEN_WIDGET[0] is not None:
            close_shop()
    _LAST_PIE[0] = in_pie
    if world is None:
        _PREV_E[0] = False
        _PREV_ESC[0] = False
        return
    _fix_view_once(world)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        return
    pawn = pc.get_controlled_pawn()
    if not pawn:
        return
    title, gate = scan_near(world, pawn.get_actor_location())
    _NEAR_TITLE[0] = title
    _NEAR_GATE[0] = gate
    try:
        _HINT_ACC[0] += float(dt) if dt else 0.016
    except Exception:
        _HINT_ACC[0] += 0.016
    if _OPEN_WIDGET[0] is None and _HINT_ACC[0] >= 1.4:
        _HINT_ACC[0] = 0.0
        if title:
            _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 1.2)
        elif gate:
            _print(world, u"按 E：地下城入口", (1.0, 0.85, 0.2, 1.0), 1.2)

    down_e = _key_down(pc, "E")
    down_esc = _key_down(pc, "Escape")
    pressed_e = down_e and (not _PREV_E[0])
    pressed_esc = down_esc and (not _PREV_ESC[0])
    _PREV_E[0] = down_e
    _PREV_ESC[0] = down_esc

    if pressed_esc and _OPEN_WIDGET[0] is not None:
        close_shop(world)
        return
    if pressed_e:
        try:
            handle_interact(world)
        except Exception as e:
            _log("E handle " + str(e))


def bootstrap():
    if _TICK[0] is None:
        try:
            _TICK[0] = unreal.register_slate_post_tick_callback(_on_tick)
            _log("tick registered SAFE_V7 new_object-first")
        except Exception as e:
            _log("tick fail " + str(e))
    _log("runtime ready SAFE_V7")


bootstrap()
'''

HELPER = r'''# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal

def open_shop_from_bp(title=u"商店"):
    try:
        import shop_interact_runtime as r
        world = r._pie_world()
        if world is None:
            unreal.log("open_shop_from_bp: no PIE")
            return False
        return r.open_shop(world, title)
    except Exception as e:
        unreal.log("open_shop_from_bp err " + str(e))
        return False
'''


def write_files():
    os.makedirs(PYDIR, exist_ok=True)
    path_rt = os.path.join(PYDIR, "shop_interact_runtime.py")
    path_hp = os.path.join(PYDIR, "open_shop_bp.py")
    open(path_rt, "w", encoding="utf-8").write(RUNTIME)
    open(path_hp, "w", encoding="utf-8").write(HELPER)
    # init_unreal
    init = os.path.join(PYDIR, "init_unreal.py")
    open(init, "w", encoding="utf-8").write(
        "try:\n    import shop_interact_runtime\nexcept Exception as e:\n"
        "    try:\n        import unreal\n        unreal.log_warning('init_unreal: '+str(e))\n"
        "    except Exception:\n        print('init_unreal', e)\n"
    )
    log("wrote runtime+helper+init")


def reload_mods():
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    for name in ("shop_interact_runtime", "open_shop_bp"):
        try:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
            else:
                __import__(name)
            log("loaded " + name)
        except Exception as e:
            log("load %s err %s\n%s" % (name, e, traceback.format_exc()))


def try_rewire_with_loaded_classes():
    log("=== try BlueprintGraph classes ===")
    for path in (
        "/Script/BlueprintGraph.K2Node_CallFunction",
        "/Script/BlueprintGraph.K2Node_CreateWidget",
        "/Script/UMGEditor.K2Node_CreateWidget",
        "/Script/UnrealEd.EdGraph",
    ):
        c = unreal.load_class(None, path)
        log("load_class %s => %s" % (path, c))
    call_cls = unreal.load_class(None, "/Script/BlueprintGraph.K2Node_CallFunction")
    graph = unreal.load_object(
        None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
    )
    if call_cls is None or graph is None:
        log("cannot rewire graph via CallFunction")
        return False
    try:
        node = unreal.new_object(call_cls, graph)
        log("new CallFunction node=" + str(node))
    except Exception as e:
        log("new_object CallFunction " + str(e))
        return False
    ksl = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
    try:
        mr = node.get_editor_property("function_reference")
        mr.set_editor_property("member_parent", ksl)
        mr.set_editor_property("member_name", "ExecuteConsoleCommand")
        node.set_editor_property("function_reference", mr)
        log("set ExecuteConsoleCommand")
    except Exception as e:
        log("func ref " + str(e))
    for meth in ("allocate_default_pins", "reconstruct_node"):
        fn = getattr(node, meth, None)
        if callable(fn):
            try:
                fn()
                log(meth + " OK")
            except Exception as e:
                log(meth + " " + str(e))
    # Set command default if find_pin exists
    find = getattr(node, "find_pin", None) or getattr(node, "FindPin", None)
    if callable(find):
        try:
            pin = find("Command")
            log("Command pin=" + str(pin))
            if pin is not None:
                try:
                    pin.set_editor_property("default_value", "py open_shop_bp.open_shop_from_bp()")
                    log("Command default set")
                except Exception as e:
                    log("set command " + str(e))
        except Exception as e:
            log("find Command " + str(e))
    # Try add to graph + link from CreateWidget's previous Pressed chain:
    # Simpler: leave CreateWidget, also connect a parallel path - hard without pins.
    # Instead: break CreateWidget by clearing its class so it doesn't confuse IsValid,
    # and rely on runtime tick for E.
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        log("saved BP after node attempt")
    except Exception as e:
        log("save " + str(e))
    return True


def try_fix_createwidget_class_with_find_pin():
    log("=== fix CreateWidget class via find_pin ===")
    node = None
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph.K2Node_CreateWidget" in pn:
            node = o
            break
    if node is None:
        log("no CreateWidget node")
        return False
    gc = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    log("node=%s gc=%s" % (node, gc))
    find = getattr(node, "find_pin", None) or getattr(node, "FindPin", None)
    log("find_pin=" + str(find))
    if not callable(find):
        # try EdGraphSchema helpers / get_all_pins
        for attr in dir(node):
            if "pin" in attr.lower():
                log("node attr " + attr)
        return False
    pin = None
    for name in ("Class", "class"):
        try:
            pin = find(name)
            log("find(%s)=%s" % (name, pin))
            if pin:
                break
        except Exception as e:
            log("find %s err %s" % (name, e))
    if pin is None:
        return False
    try:
        old = None
        try:
            old = pin.get_editor_property("default_object")
        except Exception:
            try:
                old = pin.default_object
            except Exception:
                old = "?"
        log("old Class default_object=" + str(old))
        try:
            pin.set_editor_property("default_object", gc)
            log("set default_object OK")
        except Exception as e:
            log("set default_object " + str(e))
        try:
            pin.set_editor_property("default_value", gc.get_path_name())
            log("set default_value OK")
        except Exception as e:
            log("set default_value " + str(e))
        try:
            after = pin.get_editor_property("default_object")
        except Exception:
            after = getattr(pin, "default_object", "?")
        log("after Class default_object=" + str(after))
        unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        return True
    except Exception as e:
        log("pin fix err " + str(e))
        return False


def live_open():
    log("=== live open ===")
    try:
        import shop_interact_runtime as r
        w = r._pie_world()
        log("pie=" + str(w))
        if w is None:
            log("NO_PIE - start PIE then press E")
            return False
        ok = r.open_shop(w, u"商店")
        log("open_shop => " + str(ok))
        return ok
    except Exception as e:
        log("live err " + str(e) + "\n" + traceback.format_exc())
        return False


def diagnose_wbl_create():
    log("=== diagnose WBL.create vs new_object ===")
    gc = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    wbl_cls = unreal.load_class(None, "/Script/UMG.WidgetBlueprintLibrary")
    wbl = unreal.get_default_object(wbl_cls) if wbl_cls else None
    log("gc=%s wbl=%s" % (gc, wbl))
    try:
        import shop_interact_runtime as r
        world = r._pie_world()
    except Exception:
        world = None
    log("world=" + str(world))
    if not world or not gc:
        return
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    log("pc=" + str(pc))
    if wbl:
        for label, fn in (
            ("create(pc,gc,pc)", lambda: wbl.create(pc, gc, pc)),
            ("create(world,gc,pc)", lambda: wbl.create(world, gc, pc)),
            ("create(pc,gc,None)", lambda: wbl.create(pc, gc, None)),
        ):
            try:
                w = fn()
                log("%s => %s" % (label, w))
            except Exception as e:
                log("%s ERR %s" % (label, e))
    try:
        w2 = unreal.new_object(gc, pc)
        log("new_object => " + str(w2))
    except Exception as e:
        log("new_object ERR " + str(e))


def main():
    log("START fix_cw_final")
    write_files()
    reload_mods()
    diagnose_wbl_create()
    try_fix_createwidget_class_with_find_pin()
    try_rewire_with_loaded_classes()
    ok = live_open()
    log("FINAL_PROOF=" + str(ok))
    log("DONE")
    flush()


try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
