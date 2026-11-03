# -*- coding: utf-8 -*-
"""Fix Map_Hub E-interact (Character InputAction -> Python BFL) + restore Lit/Game view.
Buildings Hub* LOCKED. UE 4.27.
"""
from __future__ import print_function
import unreal
import sys
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_interact_and_view.txt"
PY_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
BP_CHAR = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
WBP_SHOP = "/Game/UI/Shop/WBP_Shop.WBP_Shop_C"
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("FIXIV: " + s)
    except Exception:
        print("FIXIV:", s)


def flush():
    try:
        open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    except Exception as e:
        print("flush", e)


def snapshot_buildings():
    snap = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab.startswith(
            ("HubShop_", "HubWall_", "HubCorner_", "HubGate_", "HubMed_", "HubKay_", "HubEnv_", "HubFloor", "HubGround")
        ):
            loc = a.get_actor_location()
            rot = a.get_actor_rotation()
            scl = a.get_actor_scale3d()
            snap[lab] = (
                round(loc.x, 2), round(loc.y, 2), round(loc.z, 2),
                round(rot.yaw, 2), round(scl.x, 4), round(scl.y, 4), round(scl.z, 4),
            )
    return snap


def find_pins(node):
    try:
        return list(node.pins)
    except Exception:
        try:
            return list(node.get_editor_property("pins"))
        except Exception:
            return []


def pin_named(node, *names):
    lower = [n.lower() for n in names]
    for p in find_pins(node):
        try:
            n = str(p.get_editor_property("pin_name")).lower()
        except Exception:
            n = ""
        for t in lower:
            if t == n or t in n:
                return p
    return None


def pin_exec_out(node, *prefer):
    prefs = list(prefer) + ["pressed", "then", "execute"]
    for prefer_name in prefs:
        for p in find_pins(node):
            try:
                if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                    if str(p.get_editor_property("pin_name")).lower() == prefer_name.lower():
                        return p
            except Exception:
                pass
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                try:
                    if str(p.get_editor_property("pin_type")).find("exec") >= 0 or True:
                        pn = str(p.get_editor_property("pin_name")).lower()
                        if pn in ("pressed", "then", "execute", "completed"):
                            return p
                except Exception:
                    pass
        except Exception:
            pass
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                return p
        except Exception:
            pass
    return None


def pin_exec_in(node):
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_INPUT:
                return p
        except Exception:
            pass
    return None


def try_link(a, b):
    if not a or not b:
        return False
    try:
        a.make_link_to(b)
        return True
    except Exception:
        try:
            unreal.EdGraphSchema_K2().try_create_connection(a, b)
            return True
        except Exception as e:
            log("link fail " + str(e))
            return False


def set_call_func(node, owner_cls, func_name):
    try:
        mr = node.get_editor_property("function_reference")
        mr.set_editor_property("member_name", func_name)
        mr.set_editor_property("member_parent", owner_cls)
        node.set_editor_property("function_reference", mr)
        return True
    except Exception as e:
        log("set_call %s: %s" % (func_name, e))
        return False


def fix_viewports():
    log("--- fix viewports ---")
    world = None
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
    except Exception:
        world = None
    cmds = [
        "viewmode lit",
        "show flag.Wireframe 0",
        "show flag.MeshEdges 0",
        "show flag.Collision 0",
        "show flag.CollisionVisibility 0",
        "show flag.CollisionPawn 0",
        "show flag.Bounds 0",
        "show flag.BSPVertices 0",
        "show flag.ModeWidgets 1",
        "r.ShowMaterialClipmap 0",
    ]
    for c in cmds:
        try:
            if world:
                unreal.SystemLibrary.execute_console_command(world, c, None)
            else:
                unreal.SystemLibrary.execute_console_command(None, c, None)
            log("cmd " + c)
        except Exception as e:
            log("cmd fail %s %s" % (c, e))
    # Game View (hide editor-only sprites/volumes in viewport)
    for fn_name in ("editor_set_game_view", "set_game_view"):
        try:
            fn = getattr(unreal.EditorLevelLibrary, fn_name, None)
            if fn:
                fn(True)
                log("EditorLevelLibrary.%s(True)" % fn_name)
        except Exception as e:
            log("%s %s" % (fn_name, e))
    # Patch user settings strings so next open stays Lit / no wireframe edges
    try:
        import configparser
        # Use UE paths via unreal - also rewrite ini with simple replace
    except Exception:
        pass
    ini = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Saved\Config\Windows\EditorPerProjectUserSettings.ini"
    try:
        with open(ini, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        orig = txt
        # Force Lit in PerspViewModeIndex
        txt = txt.replace("PerspViewModeIndex=VMI_Wireframe", "PerspViewModeIndex=VMI_Lit")
        txt = txt.replace("PerspViewModeIndex=VMI_BrushWireframe", "PerspViewModeIndex=VMI_Lit")
        txt = txt.replace("PerspViewModeIndex=VMI_Unlit", "PerspViewModeIndex=VMI_Lit")
        # Editor show flags: Wireframe/MeshEdges/Collision off, Game on when possible
        for old, new in (
            ("Wireframe=1", "Wireframe=0"),
            ("MeshEdges=1", "MeshEdges=0"),
            (",Collision=1,", ",Collision=0,"),
            ("Bounds=1", "Bounds=0"),
            (",Game=0,", ",Game=1,"),
        ):
            txt = txt.replace(old, new)
        if txt != orig:
            with open(ini, "w", encoding="utf-8") as f:
                f.write(txt)
            log("patched EditorPerProjectUserSettings.ini")
        else:
            log("ini already clean or patterns not found")
    except Exception as e:
        log("ini patch " + str(e))


def ensure_map_gm_hub():
    log("--- ensure Map_Hub GameMode=GM_Hub ---")
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("loaded Map_Hub")
    except Exception as e:
        log("load_map " + str(e))
        return False
    gm_cls = unreal.load_class(None, GM_HUB + ".GM_Hub_C")
    if not gm_cls:
        log("GM_Hub_C missing")
        return False
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        # WorldSettings actor
        ws = None
        try:
            ws = world.world_settings
        except Exception:
            ws = None
        if ws is None:
            for a in unreal.EditorLevelLibrary.get_all_level_actors():
                if "WorldSettings" in a.get_class().get_name():
                    ws = a
                    break
        if ws is None:
            log("no WorldSettings")
            return False
        try:
            cur = ws.get_editor_property("default_game_mode")
        except Exception:
            try:
                cur = ws.get_editor_property("DefaultGameMode")
            except Exception:
                cur = None
        log("WorldSettings DefaultGameMode was " + str(cur))
        try:
            ws.set_editor_property("default_game_mode", gm_cls)
        except Exception:
            ws.set_editor_property("DefaultGameMode", gm_cls)
        log("WorldSettings DefaultGameMode -> GM_Hub")
        # Also ensure GM_Hub pawn is KayKit
        try:
            gm_bp = unreal.EditorAssetLibrary.load_asset(GM_HUB)
            unreal.BlueprintEditorLibrary.compile_blueprint(gm_bp)
            g = gm_bp.get_editor_property("generated_class")
            if callable(g):
                g = g()
            cdo = unreal.get_default_object(g)
            pawn = unreal.load_class(None, BP_CHAR + ".BP_KayKitKnight_C")
            if pawn:
                cdo.set_editor_property("default_pawn_class", pawn)
                log("GM_Hub DefaultPawn -> BP_KayKitKnight")
            # Reset PC to engine default; Character InputAction owns Interact
            try:
                cdo.set_editor_property("player_controller_class", unreal.PlayerController.static_class())
                log("GM_Hub PC -> PlayerController (Character handles Interact)")
            except Exception as e:
                log("reset PC " + str(e))
            unreal.EditorAssetLibrary.save_loaded_asset(gm_bp)
        except Exception as e:
            log("GM_Hub pawn " + str(e))
        unreal.EditorLevelLibrary.save_current_level()
        return True
    except Exception as e:
        log("ensure_map " + str(e) + "\n" + traceback.format_exc())
        return False


def ensure_triggers_and_hints(before):
    log("--- ensure triggers/hints ---")
    by = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        by[a.get_actor_label() or ""] = a
    shop_map = {
        "ShopTrigger_Weapon": ("HubShop_Weapon", "武器店", "Weapon"),
        "ShopTrigger_Armor": ("HubShop_Armor", "防具店", "Armor"),
        "ShopTrigger_Health": ("HubShop_Health", "回血店", "Health"),
    }
    for tlab, (hub, title, kind) in shop_map.items():
        hub_a = by.get(hub)
        if not hub_a:
            log("MISSING " + hub)
            continue
        loc = hub_a.get_actor_location()
        tloc = unreal.Vector(loc.x, loc.y, loc.z + 100.0)
        trig = by.get(tlab)
        if trig is None:
            trig = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.TriggerBox.static_class(), tloc, unreal.Rotator()
            )
            trig.set_actor_label(tlab)
            try:
                trig.set_folder_path("Interact")
            except Exception:
                pass
            log("spawned " + tlab)
            by[tlab] = trig
        else:
            try:
                trig.set_actor_location(tloc, False, True)
            except Exception:
                try:
                    trig.set_actor_location(tloc, False, False)
                except Exception:
                    pass
        try:
            trig.set_editor_property("tags", ["ShopInteract", "ShopTitle:" + title, "ShopKind:" + kind])
        except Exception as e:
            log("tags " + str(e))
        box = trig.get_component_by_class(unreal.BoxComponent)
        if box:
            try:
                box.set_box_extent(unreal.Vector(200.0, 200.0, 200.0), True)
            except Exception:
                pass
            try:
                box.set_collision_profile_name("OverlapAllDynamic")
            except Exception:
                pass
            try:
                box.set_editor_property("generate_overlap_events", True)
            except Exception:
                pass
            # Hide collision wire in game; editor may still show if Game View off
            try:
                box.set_hidden_in_game(True)
            except Exception:
                pass
        try:
            trig.set_actor_hidden_in_game(True)
        except Exception:
            pass
        # Also tag the shop mesh so Character can find HubShop_* by label fallback
        try:
            tags = list(hub_a.get_editor_property("tags") or [])
        except Exception:
            tags = []
        need = ["ShopInteract", "ShopTitle:" + title, "ShopKind:" + kind]
        changed = False
        for t in need:
            if t not in [str(x) for x in tags]:
                tags.append(t)
                changed = True
        if changed:
            try:
                hub_a.set_editor_property("tags", tags)
                log("tagged " + hub)
            except Exception as e:
                log("tag hub " + str(e))

    gate_hub = by.get("HubGate_DungeonEntrance")
    gate = by.get("GateTrigger_DungeonEntrance")
    if gate_hub:
        gloc = gate_hub.get_actor_location()
        tloc = unreal.Vector(gloc.x, gloc.y, gloc.z + 100.0)
        if gate is None:
            gate = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.TriggerBox.static_class(), tloc, unreal.Rotator()
            )
            gate.set_actor_label("GateTrigger_DungeonEntrance")
            try:
                gate.set_folder_path("Interact")
            except Exception:
                pass
            log("spawned gate")
            by["GateTrigger_DungeonEntrance"] = gate
        else:
            try:
                gate.set_actor_location(tloc, False, True)
            except Exception:
                try:
                    gate.set_actor_location(tloc, False, False)
                except Exception:
                    pass
        try:
            gate.set_editor_property("tags", ["GateInteract"])
        except Exception:
            pass
        box = gate.get_component_by_class(unreal.BoxComponent) if gate else None
        if box:
            try:
                box.set_box_extent(unreal.Vector(220.0, 220.0, 200.0), True)
            except Exception:
                pass
            try:
                box.set_collision_profile_name("OverlapAllDynamic")
            except Exception:
                pass
            try:
                box.set_hidden_in_game(True)
            except Exception:
                pass
        try:
            gate.set_actor_hidden_in_game(True)
        except Exception:
            pass
        try:
            tags = list(gate_hub.get_editor_property("tags") or [])
        except Exception:
            tags = []
        if "GateInteract" not in [str(x) for x in tags]:
            tags.append("GateInteract")
            try:
                gate_hub.set_editor_property("tags", tags)
                log("tagged gate hub")
            except Exception:
                pass

    # Hints
    markers = [
        ("InteractHint_Weapon", "HubShop_Weapon", "按E 武器店"),
        ("InteractHint_Armor", "HubShop_Armor", "按E 防具店"),
        ("InteractHint_Health", "HubShop_Health", "按E 回血店"),
        ("InteractHint_Gate", "HubGate_DungeonEntrance", "按E 地下城"),
    ]
    for mlab, hub, text in markers:
        hub_a = by.get(hub)
        if not hub_a:
            continue
        loc = hub_a.get_actor_location()
        mloc = unreal.Vector(loc.x, loc.y, loc.z + 220.0)
        m = by.get(mlab)
        if m is None:
            m = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.TextRenderActor.static_class(), mloc, unreal.Rotator()
            )
            if m:
                m.set_actor_label(mlab)
                try:
                    m.set_folder_path("Interact")
                except Exception:
                    pass
                log("spawned hint " + mlab)
                by[mlab] = m
        if m:
            try:
                m.set_actor_location(mloc, False, True)
            except Exception:
                try:
                    m.set_actor_location(mloc, False, False)
                except Exception:
                    pass
            try:
                tr = m.get_component_by_class(unreal.TextRenderComponent)
                if tr:
                    tr.set_text(text)
                    try:
                        tr.set_world_size(48.0)
                    except Exception:
                        pass
                    try:
                        tr.set_text_render_color(unreal.Color(255, 220, 64, 255))
                    except Exception:
                        pass
            except Exception as e:
                log("hint text " + str(e))

    after = snapshot_buildings()
    ok = before == after
    log("buildings_unchanged=%s" % ok)
    if not ok:
        for k in before:
            if before.get(k) != after.get(k):
                log("CHANGED " + k)
    return ok


def write_runtime_bfl():
    """Rewrite Content/Python/shop_interact_runtime.py: BFL for Character InputAction + light PC backup."""
    log("--- write runtime ---")
    path = PY_DIR + r"\shop_interact_runtime.py"
    code = r'''# Shop / gate interact for DungeonEscape (UE 4.27 PIE).
# Character BP InputAction "Interact" calls DE_HubInteractLib.try_hub_interact.
# Loaded by init_unreal.py.
from __future__ import print_function
import unreal

WBP_SHOP = "/Game/UI/Shop/WBP_Shop.WBP_Shop_C"
SHOP_RANGE = 380.0
GATE_RANGE = 420.0
_OPEN_WIDGET = [None]
_NEAR_TITLE = [None]
_NEAR_GATE = [False]

SHOP_LABELS = {
    "HubShop_Weapon": "武器店",
    "HubShop_Armor": "防具店",
    "HubShop_Health": "回血店",
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
        _log("no PC")
        return False
    wcls = unreal.load_class(None, WBP_SHOP)
    if not wcls:
        _log("missing WBP_Shop")
        return False
    widget = None
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
                _log("create " + str(e))
    if not widget:
        try:
            widget = unreal.new_object(wcls, pc)
        except Exception as e:
            _log("new_object " + str(e))
            return False
    try:
        t = widget.get_widget_from_name("Txt_Title")
        if t:
            t.set_text(unreal.Text(title_text))
    except Exception:
        pass
    try:
        s = widget.get_widget_from_name("Txt_Sub")
        if s:
            s.set_text(unreal.Text("暂无商品"))
    except Exception:
        pass
    try:
        h = widget.get_widget_from_name("Txt_Hint")
        if h:
            h.set_text(unreal.Text("E / Esc 关闭"))
    except Exception:
        pass
    try:
        ct = widget.get_widget_from_name("Btn_Start_Txt")
        if ct:
            ct.set_text(unreal.Text("关闭"))
    except Exception:
        pass
    try:
        qb = widget.get_widget_from_name("Btn_Quit")
        if qb is not None:
            try:
                qb.set_visibility(unreal.SlateVisibility.COLLAPSED)
            except Exception:
                pass
    except Exception:
        pass
    try:
        widget.add_to_viewport(10)
    except Exception as e:
        _log("viewport " + str(e))
        return False
    _OPEN_WIDGET[0] = widget
    try:
        pc.set_show_mouse_cursor(True)
    except Exception:
        pass
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
    _log("opened shop " + str(title_text))
    return True


def scan_near(world, pawn_loc):
    title = None
    gate = False
    best_shop = 1e12
    best_gate = 1e12
    actors = []
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
            is_shop = ("ShopInteract" in tags) or (lab in SHOP_LABELS) or lab.startswith("ShopTrigger_")
            is_gate = ("GateInteract" in tags) or (lab == "HubGate_DungeonEntrance") or lab.startswith("GateTrigger_")
            if is_shop and d <= SHOP_RANGE and d < best_shop:
                best_shop = d
                title = _title_from_tags(tags) or SHOP_LABELS.get(lab) or "商店"
            if is_gate and d <= GATE_RANGE and d < best_gate:
                best_gate = d
                gate = True
        except Exception:
            continue
    return title, gate


def handle_interact(world_ctx):
    """Core E handler used by Character InputAction via BFL."""
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
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if _OPEN_WIDGET[0] is not None:
        close_shop(world)
        return True
    pawn = None
    if pc:
        try:
            pawn = pc.get_controlled_pawn()
        except Exception:
            pawn = None
    if pawn is None:
        try:
            if isinstance(world_ctx, unreal.Pawn) or "Character" in world_ctx.get_class().get_name():
                pawn = world_ctx
        except Exception:
            pass
    if not pawn:
        _log("no pawn")
        return False
    title, gate = scan_near(world, pawn.get_actor_location())
    _NEAR_TITLE[0] = title
    _NEAR_GATE[0] = gate
    if title:
        return open_shop(world, title)
    if gate:
        _print(world, "地下城入口（待接入）", (1.0, 0.85, 0.2, 1.0), 3.0)
        return True
    _print(world, "附近没有可交互目标", (1.0, 0.4, 0.4, 1.0), 1.5)
    return False


@unreal.uclass()
class DE_HubInteractLib(unreal.BlueprintFunctionLibrary):
    @unreal.ufunction(static=True, params=[unreal.Object], ret=bool, meta=dict(Category="DungeonEscape", WorldContext="world_context_object"))
    def try_hub_interact(world_context_object):
        try:
            return bool(handle_interact(world_context_object))
        except Exception as e:
            _log("try_hub_interact err " + str(e))
            return False

    @unreal.ufunction(static=True, params=[unreal.Object], ret=None, meta=dict(Category="DungeonEscape", WorldContext="world_context_object"))
    def close_hub_shop(world_context_object):
        try:
            close_shop(world_context_object)
        except Exception as e:
            _log("close_hub_shop err " + str(e))


# Keep a tiny slate backup that ONLY closes on Esc when widget open, and shows near hint.
_TICK = [None]
_HINT_ACC = [0.0]
_PREV_E = [False]
_PREV_ESC = [False]


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


def _on_tick(dt):
    world = _pie_world()
    if world is None:
        if _OPEN_WIDGET[0] is not None:
            close_shop()
        return
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
            _print(world, "按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 1.2)
        elif gate:
            _print(world, "按 E：地下城入口", (1.0, 0.85, 0.2, 1.0), 1.2)
    # Esc close backup; E is primary via Character InputAction
    try:
        down_esc = bool(pc.is_input_key_down(unreal.Key(key_name="Escape")))
    except Exception:
        down_esc = False
    pressed_esc = down_esc and (not _PREV_ESC[0])
    _PREV_ESC[0] = down_esc
    if _OPEN_WIDGET[0] is not None and pressed_esc:
        close_shop(world)


def bootstrap():
    if _TICK[0] is None:
        try:
            _TICK[0] = unreal.register_slate_post_tick_callback(_on_tick)
            _log("hint tick registered")
        except Exception as e:
            _log("tick fail " + str(e))
    _log("runtime ready v4 (DE_HubInteractLib + Character InputAction)")


bootstrap()
'''
    try:
        open(path, "w", encoding="utf-8").write(code)
        log("wrote " + path)
    except Exception as e:
        log("write runtime " + str(e))
        return False
    # Force reload
    if PY_DIR not in sys.path:
        sys.path.insert(0, PY_DIR)
    if "shop_interact_runtime" in sys.modules:
        old = sys.modules["shop_interact_runtime"]
        try:
            h = getattr(old, "_TICK", [None])[0] or getattr(old, "_TICK_HANDLE", [None])[0]
            if h is not None:
                try:
                    unreal.unregister_slate_post_tick_callback(h)
                except Exception:
                    pass
        except Exception:
            pass
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as sir
    log("reloaded runtime lib=" + str(getattr(sir, "DE_HubInteractLib", None)))
    return True


def clear_old_interact_nodes(graph):
    removed = 0
    nodes = []
    try:
        nodes = list(graph.nodes)
    except Exception:
        try:
            nodes = list(graph.get_editor_property("nodes"))
        except Exception:
            nodes = []
    for n in list(nodes):
        try:
            cn = n.get_class().get_name()
            drop = False
            if cn == "K2Node_InputAction":
                try:
                    an = str(n.get_editor_property("input_action_name"))
                except Exception:
                    an = ""
                if an == "Interact" or "Interact" in an:
                    drop = True
            if cn == "K2Node_CallFunction":
                try:
                    mr = n.get_editor_property("function_reference")
                    mn = str(mr.get_editor_property("member_name"))
                    if mn in ("try_hub_interact", "TryHubInteract", "close_hub_shop"):
                        drop = True
                except Exception:
                    pass
            # our marker comment nodes
            try:
                if "DE_HubInteract" in str(n.get_editor_property("node_comment")):
                    drop = True
            except Exception:
                pass
            if drop:
                try:
                    graph.remove_node(n)
                    removed += 1
                except Exception:
                    try:
                        n.destroy_node()
                        removed += 1
                    except Exception:
                        pass
        except Exception:
            continue
    log("cleared old interact nodes=%d" % removed)


def wire_character_interact():
    log("--- wire BP_KayKitKnight InputAction Interact ---")
    if not unreal.EditorAssetLibrary.does_asset_exist(BP_CHAR):
        log("missing character BP")
        return False
    bp = unreal.EditorAssetLibrary.load_asset(BP_CHAR)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception as e:
        log("precompile " + str(e))
    pages = []
    try:
        pages = list(bp.ubergraph_pages)
    except Exception:
        pages = []
    if not pages:
        log("no ubergraph")
        return False
    graph = pages[0]
    clear_old_interact_nodes(graph)

    # InputAction Interact
    ia = unreal.new_object(unreal.K2Node_InputAction, graph)
    try:
        ia.set_editor_property("input_action_name", "Interact")
    except Exception as e:
        log("set action name " + str(e))
        try:
            ia.input_action_name = "Interact"
        except Exception:
            pass
    try:
        ia.node_pos_x = -1200
        ia.node_pos_y = 3200
    except Exception:
        pass
    try:
        ia.set_editor_property("node_comment", "DE_HubInteract InputAction")
        ia.set_editor_property("b_comment_bubble_visible", True)
    except Exception:
        pass
    graph.add_node(ia, False, False)

    # Call DE_HubInteractLib.try_hub_interact
    lib_cls = None
    try:
        import shop_interact_runtime as sir
        lib_cls = sir.DE_HubInteractLib.static_class()
    except Exception as e:
        log("lib class " + str(e))
    call = unreal.new_object(unreal.K2Node_CallFunction, graph)
    if lib_cls:
        set_call_func(call, lib_cls, "try_hub_interact")
    else:
        # fallback path name
        try:
            py_cls = unreal.load_class(None, "/Engine/PythonTypes.DE_HubInteractLib")
            if py_cls:
                set_call_func(call, py_cls, "try_hub_interact")
                lib_cls = py_cls
        except Exception as e:
            log("load lib " + str(e))
    try:
        call.node_pos_x = -800
        call.node_pos_y = 3200
    except Exception:
        pass
    try:
        call.set_editor_property("node_comment", "DE_HubInteract call")
    except Exception:
        pass
    graph.add_node(call, False, False)

    # Self → world_context_object pin
    self_node = unreal.new_object(unreal.K2Node_Self, graph)
    try:
        self_node.node_pos_x = -1000
        self_node.node_pos_y = 3350
    except Exception:
        pass
    graph.add_node(self_node, False, False)

    pressed = pin_named(ia, "Pressed") or pin_exec_out(ia, "Pressed")
    call_in = pin_exec_in(call)
    ok1 = try_link(pressed, call_in)
    log("link Pressed->call %s" % ok1)

    self_out = pin_named(self_node, "self") or pin_exec_out(self_node)
    # find world context pin on call
    ctx = pin_named(call, "world_context_object", "WorldContextObject", "World Context Object", "__WorldContext")
    if ctx is None:
        # first object input pin that's not exec
        for p in find_pins(call):
            try:
                if p.get_editor_property("direction") != unreal.EdGraphPinDirection.EGPD_INPUT:
                    continue
                pn = str(p.get_editor_property("pin_name")).lower()
                if pn in ("execute", "then"):
                    continue
                ctx = p
                break
            except Exception:
                pass
    self_data = None
    for p in find_pins(self_node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                self_data = p
                break
        except Exception:
            pass
    ok2 = try_link(self_data, ctx)
    log("link self->ctx %s ctx=%s" % (ok2, ctx))

    # Allocate node guides / reconstruct
    for n in (ia, call, self_node):
        try:
            n.reconstruct_node()
        except Exception:
            pass
    # Re-link after reconstruct
    pressed = pin_named(ia, "Pressed") or pin_exec_out(ia, "Pressed")
    call_in = pin_exec_in(call)
    try_link(pressed, call_in)
    self_data = None
    for p in find_pins(self_node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                self_data = p
                break
        except Exception:
            pass
    ctx = pin_named(call, "world_context_object", "WorldContextObject", "World Context Object", "__WorldContext")
    if ctx is None:
        for p in find_pins(call):
            try:
                if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_INPUT:
                    pn = str(p.get_editor_property("pin_name")).lower()
                    if pn not in ("execute", "then"):
                        ctx = p
                        break
            except Exception:
                pass
    try_link(self_data, ctx)

    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
    except Exception as e:
        log("save bp " + str(e))
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log("compiled BP_KayKitKnight")
    except Exception as e:
        log("compile " + str(e))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
    except Exception:
        pass

    # Dump pins for debug
    log("IA pins: " + ", ".join([str(p.get_editor_property("pin_name")) for p in find_pins(ia)]))
    log("Call pins: " + ", ".join([str(p.get_editor_property("pin_name")) for p in find_pins(call)]))
    log("lib_cls=" + str(lib_cls))
    return True


def main():
    log("=== fix_interact_and_view START ===")
    fix_viewports()
    before = {}
    try:
        # load map first for snapshot
        ensure_map_gm_hub()
        before = snapshot_buildings()
        log("snapshot n=%d" % len(before))
        ensure_triggers_and_hints(before)
    except Exception:
        log("map/triggers FATAL\n" + traceback.format_exc())

    write_runtime_bfl()
    wire_character_interact()

    try:
        unreal.EditorLevelLibrary.save_current_level()
        log("level saved")
    except Exception as e:
        log("save level " + str(e))
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("dirty saved")
    except Exception as e:
        log("dirty " + str(e))

    # Final viewport nudge after map load
    fix_viewports()
    log("=== fix_interact_and_view DONE ===")
    log("TEST: stop PIE if running, press G if still see editor icons, Alt+P, walk to yellow 按E, press E")


try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
flush()
