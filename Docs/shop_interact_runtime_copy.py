# -*- coding: utf-8 -*-
# Shop / gate interact SPLIT_WBP_V14_GATE_FIRST for DungeonEscape UE4.27 PIE.
# Priority: near GateTrigger/HubGate -> OpenLevel Map_Dungeon FIRST; else shop WBP.
# Shops use smaller SHOP_RANGE so they do not overlap the red gate.
# Key detect: UE is_input_key_down + was_just_pressed + Win GetAsyncKeyState(E).
from __future__ import print_function
import unreal
import time

try:
    import ctypes
    _user32 = ctypes.windll.user32
except Exception:
    _user32 = None

# Per-shop widget paths (created as WBP_Shop_Weapon / Armor / Health)
SHOP_WBP = {
    "Weapon": (
        "/Game/UI/Shop/WBP_Shop_Weapon.WBP_Shop_Weapon_C",
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    ),
    "Armor": (
        "/Game/UI/Shop/WBP_Shop_Armor.WBP_Shop_Armor_C",
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    ),
    "Health": (
        "/Game/UI/Shop/WBP_Shop_Health.WBP_Shop_Health_C",
        "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    ),
}
WBP_FALLBACK = (
    "/Game/UI/Shop/WBP_Shop.WBP_Shop_C",
    "/Game/UI/Shop/WBP_Shop2.WBP_Shop2_C",
    "/Game/UI/Shop/WBP_ShopSimple.WBP_ShopSimple_C",
)
SHOP_RANGE = 320.0
GATE_RANGE = 280.0
_OPEN_WIDGET = [None]
_NEAR_SHOP = [None]  # ("Weapon"|"Armor"|"Health", title) or None
_NEAR_GATE = [False]
_PREV_E = [False]
_PREV_ESC = [False]
_LAST_HINT_KEY = [None]
_TICK = [None]
_VIEW_FIXED = [False]
_MY_GEN = [0]
_STATUS_ACC = [0.0]
_STATUS_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_tick_status.txt"
_VK_E = 0x45
_VK_ESC = 0x1B

SHOP_META = {
    "HubShop_Weapon": ("Weapon", u"武器店"),
    "HubShop_Armor": ("Armor", u"防具店"),
    "HubShop_Health": ("Health", u"回血店"),
    "ShopTrigger_Weapon": ("Weapon", u"武器店"),
    "ShopTrigger_Armor": ("Armor", u"防具店"),
    "ShopTrigger_Health": ("Health", u"回血店"),
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


def _shop_key_from_tags(tags):
    for t in tags:
        tl = t.lower()
        if "weapon" in tl:
            return "Weapon"
        if "armor" in tl or "armour" in tl:
            return "Armor"
        if "health" in tl or "heal" in tl or "potion" in tl:
            return "Health"
    return None


def _print(world, msg, color=(1.0, 0.95, 0.2, 1.0), sec=2.0):
    try:
        unreal.KismetSystemLibrary.print_string(
            world, msg, True, False,
            unreal.LinearColor(color[0], color[1], color[2], color[3]), sec
        )
    except Exception:
        try:
            cls = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
            cdo = unreal.get_default_object(cls)
            cdo.print_string(
                world, msg, True, False,
                unreal.LinearColor(color[0], color[1], color[2], color[3]), sec
            )
        except Exception:
            _log(msg)


def _load_shop_class(shop_key):
    paths = list(SHOP_WBP.get(shop_key) or ()) + list(WBP_FALLBACK)
    seen = set()
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        c = unreal.load_class(None, p)
        if c:
            return c, p
    return None, None


def _pie_world():
    try:
        ws = unreal.EditorLevelLibrary.get_pie_worlds(False)
        if ws:
            return ws[0]
    except Exception:
        pass
    try:
        ws = unreal.EditorLevelLibrary.get_pie_worlds(True)
        if ws:
            return ws[0]
    except Exception:
        pass
    try:
        return unreal.EditorLevelLibrary.get_game_world()
    except Exception:
        return None


def _paint_shop_texts(widget, title_text):
    if widget is None:
        return
    base = widget.get_path_name()
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if base not in pn:
            continue
        try:
            name = o.get_name()
        except Exception:
            name = ""
        try:
            if name == "TextBlock_0" or "Title" in name or name.startswith("Txt_"):
                o.set_text(unreal.Text(str(title_text)))
            o.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass


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


def open_shop(world_ctx, shop_key, title_text):
    if _OPEN_WIDGET[0] is not None:
        close_shop(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if not pc:
        _log("open_shop FAIL no PC")
        return False
    wcls, wpath = _load_shop_class(shop_key)
    if not wcls:
        _log("open_shop FAIL no WBP class key=%s" % shop_key)
        return False
    _log("open_shop key=%s class=%s" % (shop_key, wpath))
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
            _log("new_object err " + str(e))
    if not widget:
        _log("open_shop FAIL create null")
        return False
    _paint_shop_texts(widget, title_text)
    try:
        widget.set_visibility(unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    try:
        widget.add_to_viewport(200)
    except Exception as e:
        _log("viewport err " + str(e))
        return False
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(900, 600))
    except Exception:
        pass
    _OPEN_WIDGET[0] = widget
    try:
        pc.set_show_mouse_cursor(True)
    except Exception:
        pass
    if wbl:
        try:
            wbl.set_input_mode_game_and_ui_ex(
                pc, widget, unreal.MouseLockMode.DO_NOT_LOCK, False
            )
        except Exception:
            try:
                wbl.set_input_mode_ui_only_ex(pc, widget)
            except Exception as e:
                _log("input mode " + str(e))
    _print(world_ctx, u"已打开：" + str(title_text), (0.2, 1.0, 0.3, 1.0), 2.0)
    _log("open_shop SUCCESS key=%s title=%s" % (shop_key, title_text))
    return True


def _meta_for_actor(lab, tags):
    if lab in SHOP_META:
        return SHOP_META[lab]
    key = _shop_key_from_tags(tags)
    title = _title_from_tags(tags)
    if key:
        default_title = {
            "Weapon": u"武器店",
            "Armor": u"防具店",
            "Health": u"回血店",
        }.get(key, u"商店")
        return key, title or default_title
    if title:
        # Title-only: try map Chinese/English
        if u"武器" in title or "Weapon" in title:
            return "Weapon", title
        if u"防具" in title or "Armor" in title:
            return "Armor", title
        if u"回血" in title or "Health" in title or u"药水" in title:
            return "Health", title
        return "Weapon", title  # generic fallback key
    return None


def scan_near(world, pawn_loc):
    """Return (shop_key, title, gate). shop_key is Weapon/Armor/Health or None.
    Gate is True when within GATE_RANGE of GateTrigger/HubGate/DungeonEntrance.
    Caller must prefer gate over shop when both are True.
    """
    best = None
    best_d = 1e18
    gate = False
    best_gate_d = 1e18
    try:
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception:
        return None, None, False
    for actor in actors:
        try:
            loc = actor.get_actor_location()
        except Exception:
            continue
        d = _dist(pawn_loc, loc)
        tags = _tags(actor)
        lab = _label(actor)
        is_shop = ("ShopInteract" in tags) or lab.startswith("HubShop_") or lab.startswith("ShopTrigger_")
        is_gate = (
            ("DungeonGate" in tags)
            or ("GateInteract" in tags)
            or ("HubGate" in lab)
            or ("GateTrigger" in lab)
            or ("DungeonEntrance" in lab)
            or lab.startswith("GateTrigger_")
        )
        if is_shop and d < SHOP_RANGE and d < best_d:
            meta = _meta_for_actor(lab, tags)
            if meta:
                best_d = d
                best = meta
        if is_gate and d < GATE_RANGE and d < best_gate_d:
            best_gate_d = d
            gate = True
    if best:
        return best[0], best[1], gate
    return None, None, gate


DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon"


def enter_dungeon(world_ctx):
    """OpenLevel to Map_Dungeon when E near red gate."""
    if world_ctx is None:
        return False
    close_shop(world_ctx)
    _print(world_ctx, u"进入地下城…", (1.0, 0.85, 0.2, 1.0), 2.0)
    try:
        unreal.GameplayStatics.open_level(world_ctx, DUNGEON_LEVEL, True, "")
        _log("OpenLevel " + DUNGEON_LEVEL)
        return True
    except Exception as e:
        _log("OpenLevel fail " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + DUNGEON_LEVEL)
        _log("console Open " + DUNGEON_LEVEL)
        return True
    except Exception as e2:
        _log("console Open fail " + str(e2))
        _print(world_ctx, u"进关失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)
        return False



def handle_interact(world_ctx):
    if world_ctx is None:
        return False
    world = world_ctx
    try:
        maybe = world_ctx.get_world()
        if maybe is not None:
            world = maybe
    except Exception:
        pass
    if _OPEN_WIDGET[0] is not None:
        close_shop(world)
        return True
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = None
    if pc:
        try:
            pawn = pc.get_controlled_pawn()
        except Exception:
            pawn = None
    if not pawn:
        _log("no pawn — ignore E")
        return False
    shop_key, title, gate = scan_near(world, pawn.get_actor_location())
    if shop_key and title:
        _NEAR_SHOP[0] = (shop_key, title)
    else:
        _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = gate
    # Gate wins over shop whenever both are in range.
    if gate:
        _log("E near gate -> enter_dungeon (shop_key=%s)" % (shop_key,))
        return enter_dungeon(world)
    if shop_key and title:
        return open_shop(world, shop_key, title)
    _log("E ignored — not near shop/gate")
    return False


def _ue_key_down(pc, name):
    if not pc:
        return False
    for factory in (
        lambda: unreal.Key(key_name=name),
        lambda: unreal.Key(name),
    ):
        try:
            key = factory()
        except Exception:
            continue
        try:
            if bool(pc.is_input_key_down(key)):
                return True
        except Exception:
            pass
        try:
            if bool(pc.was_input_key_just_pressed(key)):
                return True
        except Exception:
            pass
    return False


def _win_key_down(vk):
    if _user32 is None:
        return False
    try:
        return bool(_user32.GetAsyncKeyState(vk) & 0x8000)
    except Exception:
        return False


def _key_down(pc, name):
    if name == "E":
        return _ue_key_down(pc, "E") or _win_key_down(_VK_E)
    if name == "Escape":
        return _ue_key_down(pc, "Escape") or _win_key_down(_VK_ESC)
    return _ue_key_down(pc, name)


def _write_status(world, pc, down_e, pressed_e, near_shop, gate):
    try:
        wid = _OPEN_WIDGET[0]
        invp = False
        if wid is not None:
            try:
                invp = bool(wid.is_in_viewport())
            except Exception:
                pass
        pawn = None
        try:
            pawn = pc.get_controlled_pawn() if pc else None
        except Exception:
            pass
        loc = None
        if pawn:
            try:
                l = pawn.get_actor_location()
                loc = (round(l.x, 1), round(l.y, 1), round(l.z, 1))
            except Exception:
                pass
        near_s = None
        if near_shop:
            near_s = "%s/%s" % (near_shop[0], near_shop[1])
        txt = (
            "t=%s gen=%s pie=%s e=%s pe=%s near=%s gate=%s open=%s invp=%s loc=%s\n"
            % (
                time.strftime("%H:%M:%S"),
                _MY_GEN[0],
                bool(world),
                down_e,
                pressed_e,
                near_s,
                gate,
                wid is not None,
                invp,
                loc,
            )
        )
        open(_STATUS_PATH, "w", encoding="utf-8").write(txt)
    except Exception:
        pass


def _fix_view_once(world):
    if _VIEW_FIXED[0]:
        return
    _VIEW_FIXED[0] = True
    try:
        unreal.SystemLibrary.execute_console_command(world, "viewmode lit")
    except Exception:
        try:
            cls = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
            unreal.get_default_object(cls).execute_console_command(world, "viewmode lit", None)
        except Exception:
            pass



# --- T218b dungeon pawn ensure (after OpenLevel PIE often skips RestartPlayer) ---
_DUNGEON_PAWN_TRIED = [False]
_BP_KNIGHT = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C"

def _world_is_dungeon(world):
    try:
        p = str(world.get_path_name())
        return ("Map_Dungeon" in p) or ("UEDPIE_" in p and "Dungeon" in p)
    except Exception:
        return False

def ensure_dungeon_pawn(world):
    """If Map_Dungeon PIE has PC but no pawn, spawn+possess KayKit."""
    if world is None or not _world_is_dungeon(world):
        _DUNGEON_PAWN_TRIED[0] = False
        return False
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        return False
    try:
        if pc.get_controlled_pawn() is not None:
            return True
    except Exception:
        pass
    if _DUNGEON_PAWN_TRIED[0]:
        return False
    _DUNGEON_PAWN_TRIED[0] = True
    # Prefer RestartPlayer: OpenLevel PIE often skips it even when GM/PlayerStart are set.
    try:
        gm = unreal.GameplayStatics.get_game_mode(world)
        if gm is not None:
            gm.restart_player(pc)
            try:
                if pc.get_controlled_pawn() is not None:
                    _log("ensure_dungeon_pawn: RestartPlayer ok")
                    _print(world, u"地下城角色已就绪", (0.3, 1.0, 0.5, 1.0), 2.0)
                    return True
            except Exception:
                pass
    except Exception as e:
        _log("ensure_dungeon_pawn RestartPlayer " + str(e))
    # Fallback: possess already-placed Dungeon_PlayerPawn if present
    try:
        knight_cls = unreal.load_class(None, _BP_KNIGHT)
        if knight_cls:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, knight_cls):
                try:
                    pc.possess(a)
                    _log("ensure_dungeon_pawn: possessed placed " + str(a))
                    _print(world, u"地下城角色已就绪", (0.3, 1.0, 0.5, 1.0), 2.0)
                    return True
                except Exception:
                    continue
    except Exception as e:
        _log("ensure_dungeon_pawn placed possess " + str(e))
    cls = unreal.load_class(None, _BP_KNIGHT)
    if not cls:
        _log("ensure_dungeon_pawn: no BP_KayKitKnight_C")
        return False
    loc = unreal.Vector(0.0, 0.0, 150.0)
    try:
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PlayerStart.static_class()):
            loc = a.get_actor_location()
            loc = unreal.Vector(loc.x, loc.y, max(float(loc.z), 150.0))
            break
    except Exception:
        pass
    pawn = None
    try:
        pawn = world.spawn_actor(cls, loc, unreal.Rotator(0.0, 0.0, 0.0))
    except Exception:
        pawn = None
    if pawn is None:
        try:
            pawn = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, unreal.Rotator(0.0, 0.0, 0.0))
        except Exception as e:
            _log("ensure_dungeon_pawn spawn fail " + str(e))
            return False
    if not pawn:
        _log("ensure_dungeon_pawn: spawn returned None")
        return False
    try:
        pc.possess(pawn)
        _log("ensure_dungeon_pawn: possessed " + str(pawn))
        _print(world, u"地下城角色已就绪", (0.3, 1.0, 0.5, 1.0), 2.0)
        return True
    except Exception as e:
        _log("ensure_dungeon_pawn possess fail " + str(e))
        return False


def _on_tick(dt):
    try:
        if _MY_GEN[0] != int(getattr(unreal, "_de_shop_tick_gen", 0)):
            return
    except Exception:
        pass
    world = _pie_world()
    if world is None:
        _PREV_E[0] = False
        _PREV_ESC[0] = False
        _LAST_HINT_KEY[0] = None
        return
    ensure_dungeon_pawn(world)
    _fix_view_once(world)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        return

    down_e = _key_down(pc, "E")
    down_esc = _key_down(pc, "Escape")
    pressed_e = down_e and (not _PREV_E[0])
    pressed_esc = down_esc and (not _PREV_ESC[0])
    _PREV_E[0] = down_e
    _PREV_ESC[0] = down_esc

    pawn = None
    try:
        pawn = pc.get_controlled_pawn()
    except Exception:
        pawn = None

    shop_key = None
    title = None
    gate = False
    if pawn is not None and _OPEN_WIDGET[0] is None:
        shop_key, title, gate = scan_near(world, pawn.get_actor_location())
        if shop_key and title:
            _NEAR_SHOP[0] = (shop_key, title)
        else:
            _NEAR_SHOP[0] = None
        _NEAR_GATE[0] = gate
        # Gate hint wins when both near.
        if gate:
            key = ("gate",)
        elif shop_key and title:
            key = ("shop", shop_key)
        else:
            key = None
        if key is not None and key != _LAST_HINT_KEY[0]:
            if key[0] == "gate":
                _print(world, u"按 E 进入地下城", (1.0, 0.85, 0.2, 1.0), 2.0)
            else:
                _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 2.0)
        _LAST_HINT_KEY[0] = key

    _STATUS_ACC[0] += float(dt) if dt else 0.016
    if _STATUS_ACC[0] >= 0.5 or pressed_e:
        _STATUS_ACC[0] = 0.0
        _write_status(world, pc, down_e, pressed_e, _NEAR_SHOP[0], gate or _NEAR_GATE[0])

    if pressed_esc and _OPEN_WIDGET[0] is not None:
        close_shop(world)
        return
    if pressed_e:
        _log("E pressed -> handle_interact")
        try:
            handle_interact(world)
        except Exception as e:
            _log("E handle " + str(e))


def bootstrap():
    prev = getattr(unreal, "_de_shop_tick_handle", None)
    if prev is not None:
        for unreg in (
            getattr(unreal, "unregister_slate_post_tick_callback", None),
            getattr(unreal, "unregister_slate_pre_tick_callback", None),
        ):
            if unreg is None:
                continue
            try:
                unreg(prev)
            except Exception:
                pass
        try:
            unreal._de_shop_tick_handle = None
        except Exception:
            pass
    if _TICK[0] is not None:
        for unreg in (
            getattr(unreal, "unregister_slate_post_tick_callback", None),
            getattr(unreal, "unregister_slate_pre_tick_callback", None),
        ):
            if unreg is None:
                continue
            try:
                unreg(_TICK[0])
            except Exception:
                pass
        _TICK[0] = None
    try:
        unreal._de_shop_tick_gen = int(getattr(unreal, "_de_shop_tick_gen", 0)) + 1
    except Exception:
        unreal._de_shop_tick_gen = 1
    _MY_GEN[0] = int(unreal._de_shop_tick_gen)
    try:
        _TICK[0] = unreal.register_slate_post_tick_callback(_on_tick)
        unreal._de_shop_tick_handle = _TICK[0]
        _log("tick registered SPLIT_WBP_V14_GATE_FIRST gen=%s" % _MY_GEN[0])
    except Exception as e:
        _log("tick register fail " + str(e))
    _LAST_HINT_KEY[0] = None
    _PREV_E[0] = False
    _PREV_ESC[0] = False
    _VIEW_FIXED[0] = False
    _log("runtime ready SPLIT_WBP_V14_GATE_FIRST")


bootstrap()
