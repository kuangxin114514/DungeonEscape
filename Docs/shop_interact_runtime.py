# -*- coding: utf-8 -*-
# Shop / gate / dungeon-exit / LMB attack SPLIT_WBP_V15e_T231 for DungeonEscape UE4.27 PIE.
# Priority: near GateTrigger/HubGate -> OpenLevel Map_Dungeon1 FIRST; else shop WBP.
# Map_Dungeon1: near DungeonExit -> OpenLevel Map_Hub; LMB plays 1H Chop.
# V15e: Prefer DefaultSlot dynamic montage WITHOUT clearing AnimBP (upper-body overlay once
# ABP wires Slot+LayeredBlendPerBone on spine). Fall back to single-node only if slot fails.
# Shops use smaller SHOP_RANGE so they do not overlap the red gate.
# Key detect: UE is_input_key_down + was_just_pressed + Win GetAsyncKeyState.
# V15e_HP: screen HUD WBP_PlayerHealthBar top-left; sync Health/MaxHealth each tick.
# T285: enemy HP = TRUE screen overlay (ProjectWorldToScreen + AddToViewport).
#       NO WidgetComponent World/Screen 3D plane (that still tilted / perspective).
#       Each tick: head world loc -> project -> set_position_in_viewport; purge dead actors.
# T288: ENEMY_HP_BAR_Z_OFFSET (file top) or BP HealthBarHeightOffset = simple height knob.
# T290: distance scale like world nameplate — near=big far=small (still flat screen HUD).
#       ENEMY_HP_BAR_REF_DISTANCE / MIN_SCALE / MAX_SCALE at file top.
# T295: ENEMY_HP_BAR_X_OFFSET at file top = simple left/right knob (screen px; +right / -left).
# T297_NO_ENEMY_HP: enemy screen HP bars DISABLED (no create/project/AddToViewport).
#       Player WBP_PlayerHealthBar + shop/gate/travel kept. Damage still works via actor scan.
# T299_HP50: skeleton MaxHealth/Health=50; LMB wait 1.0s then -10 if in range; 0 -> DestroyActor.
#       No enemy HP bar UI. Once-per-swing via pending timer + attack cooldown.
# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud.
# T309: GI_DungeonGame Gold/Inventory via player_meta helpers (OpenLevel-safe); dungeon exit E -> Map_Dungeon2.
#       ClearProgress for new-save later. Map_Hub buildings untouched.
# T311_GOLD_HUD: screen Gold text top-RIGHT (WBP_PlayerGold / fallback health WBP); sync get_gold each tick; survive OpenLevel.
# T312_GOLD5: fix gold TextBlock canvas size (point-anchor Right/Bottom = width/height); DEFAULT_GOLD=5; meta JSON source-of-truth.
# T313_GOLD_RIGHT: pin WBP_PlayerGold UserWidget to true viewport TOP-RIGHT (was under HP on left).
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
EXIT_RANGE = 380.0
_OPEN_WIDGET = [None]
_HEALTH_WIDGET = [None]
_HEALTH_BAR = [None]
_HEALTH_TXT = [None]
_GOLD_WIDGET = [None]
_GOLD_TXT = [None]
HEALTH_WBP_PATHS = (
    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",
    "/Game/UI/HUD/WBP_PlayerHealthBar_C",
)
GOLD_WBP_PATHS = (
    "/Game/UI/HUD/WBP_PlayerGold.WBP_PlayerGold_C",
    "/Game/UI/HUD/WBP_PlayerGold_C",
    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",
    "/Game/UI/HUD/WBP_PlayerHealthBar_C",
)
ENEMY_HEALTH_WBP_PATHS = (
    "/Game/UI/HUD/WBP_EnemyHealthBar.WBP_EnemyHealthBar_C",
    "/Game/UI/HUD/WBP_EnemyHealthBar_C",
    "/Game/UI/HUD/WBP_PlayerHealthBar.WBP_PlayerHealthBar_C",
)
_ENEMY_BARS = {}  # actor path -> {wc, widget, pb, health, max_health}
_ENEMY_HP_DEFAULT = 50.0
# ============================================================
# 改这个数字调骷髅血条高低（世界单位 cm，越大越高 / 越小越低）
# Change THIS number to raise/lower the enemy HP bar above the head.
# Also prefers BP_Enemy_Skeleton.HealthBarHeightOffset if that float exists.
# ============================================================
ENEMY_HP_BAR_Z_OFFSET = 50
# ============================================================
# 改这个数字调骷髅血条左右：正数往右，负数往左（屏幕像素）
# Change THIS number to nudge the enemy HP bar left/right on screen.
# ============================================================
ENEMY_HP_BAR_X_OFFSET = 0
_ENEMY_BODY_FALLBACK_Z = 120.0  # only if no head bone/bounds (from mesh/actor root)
_ENEMY_BAR_Z = ENEMY_HP_BAR_Z_OFFSET  # alias for older call sites
_ENEMY_DRAW = (140.0, 16.0)
# ============================================================
# 距离缩放（像头顶铭牌）：近大远小，仍是贴屏平面不透视歪斜
# REF_DISTANCE = 参考距离(cm)，大约在这个距离时血条≈当前默认大小
# MIN/MAX_SCALE = 缩放上下限，拉开走近/走远的视觉差
# ============================================================
ENEMY_HP_BAR_REF_DISTANCE = 500.0  # cm; mid-range fight look ~ current size
ENEMY_HP_BAR_MIN_SCALE = 0.30
ENEMY_HP_BAR_MAX_SCALE = 2.50
# T297: set True to bring skeleton HP bars back; False = never spawn overlays.
ENEMY_HP_BARS_ENABLED = False
_ENEMY_CLS_PATHS = (
    "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton.BP_Enemy_Skeleton_C",
)
_ENEMY_WC_NAME = "EnemyHealthBar"
_ENEMY_PURGE_ACC = [0.0]
_LAST_WORLD_KEY = [None]  # T278: detect OpenLevel / map travel
_NEAR_SHOP = [None]  # ("Weapon"|"Armor"|"Health", title) or None
_NEAR_GATE = [False]
_NEAR_EXIT = [False]
_PREV_E = [False]
_PREV_ESC = [False]
_PREV_LMB = [False]
_LAST_ATTACK_T = [0.0]
# T299: Python-side HP when BP has no Health var; key=actor path
_ENEMY_HP_CACHE = {}  # path -> {"health": float, "max_health": float}
# Pending delayed hit from one LMB swing: {"due": t, "pawn_name": str} or None
_PENDING_ATTACK_HIT = [None]
_LAST_HINT_KEY = [None]
_TICK = [None]
_VIEW_FIXED = [False]
_MY_GEN = [0]
_STATUS_ACC = [0.0]
_STATUS_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_tick_status.txt"
_VK_E = 0x45
_VK_ESC = 0x1B
_VK_LBUTTON = 0x01
ATTACK_COOLDOWN = 0.55
# T299: simple melee numbers (course)
ATTACK_DAMAGE = 10.0          # HP removed per successful delayed hit
ATTACK_DAMAGE_DELAY = 0.5     # seconds after LMB before distance check + damage
ATTACK_HIT_RANGE = 220.0      # cm from player to skeleton
ATTACK_ANIM_PATHS = (
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig",
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop",
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Slice_Diagonal_Rig",
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Slice_Horizontal_Rig",
)
ATTACK_MONTAGE_PATH = "/Game/Characters/Player/KayKit/Animations/AM_KayKit_1H_Chop"

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



def _find_textblock_under(widget, prefer_names=("Txt_Gold", "TextBlock_0", "Txt_HP")):
    """Shop-style TextBlock bind: ObjectIterator scoped by UserWidget path. T311_GOLD_HUD."""
    if widget is None:
        return None
    try:
        base = widget.get_path_name()
    except Exception:
        return None
    if not base:
        return None
    preferred = None
    any_tb = None
    try:
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
            if any_tb is None:
                any_tb = o
            if name in prefer_names:
                preferred = o
                break
            if preferred is None and (name.startswith("Txt_") or "Gold" in name or "Title" in name):
                preferred = o
    except Exception:
        return None
    return preferred if preferred is not None else any_tb


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
    """Return (shop_key, title, gate, hub_exit).
    Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs -> Map_Dungeon2.
    """
    best = None
    best_d = 1e18
    gate = False
    best_gate_d = 1e18
    hub_exit = False
    best_exit_d = 1e18
    try:
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception:
        return None, None, False, False
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
        is_exit = (
            ("HubReturn" in tags)
            or ("DungeonExit" in tags)
            or ("HubExit" in tags)
            or lab.startswith("DungeonExit_")
            or lab.startswith("HubReturn_")
            or ("DungeonExit" in lab)
        )
        if is_shop and d < SHOP_RANGE and d < best_d:
            meta = _meta_for_actor(lab, tags)
            if meta:
                best_d = d
                best = meta
        if is_gate and d < GATE_RANGE and d < best_gate_d:
            best_gate_d = d
            gate = True
        if is_exit and d < EXIT_RANGE and d < best_exit_d:
            best_exit_d = d
            hub_exit = True
    if best:
        return best[0], best[1], gate, hub_exit
    return None, None, gate, hub_exit


DUNGEON_LEVEL_CANDIDATES = (
    "/Game/Maps/Dungeon/Map_Dungeon1",
    "/Game/Maps/Dungeon/Map_Dungeon",
)
DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon1"
DUNGEON2_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon2"
HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"
# T309 player meta (Gold + Inventory). Prefers live GI_DungeonGame props; else module+JSON.
DEFAULT_GOLD = 5
_PLAYER_META = {"gold": DEFAULT_GOLD, "inventory": [], "ready": False}
_PLAYER_META_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Saved\PlayerMeta.json"


def resolve_dungeon_level():
    """Prefer Map_Dungeon1 when Map_Dungeon package is missing."""
    global DUNGEON_LEVEL
    chosen = DUNGEON_LEVEL_CANDIDATES[0]
    try:
        eal = unreal.EditorAssetLibrary
        found = False
        for path in DUNGEON_LEVEL_CANDIDATES:
            try:
                if eal.does_asset_exist(path):
                    chosen = path
                    found = True
                    break
            except Exception:
                continue
        if not found:
            chosen = DUNGEON_LEVEL_CANDIDATES[0]
    except Exception:
        chosen = DUNGEON_LEVEL_CANDIDATES[0]
    DUNGEON_LEVEL = chosen
    return chosen



def _gi_from_world(world_ctx):
    """Return live GameInstance (GI_DungeonGame) or None."""
    if world_ctx is None:
        return None
    try:
        return unreal.GameplayStatics.get_game_instance(world_ctx)
    except Exception:
        return None


def _meta_load_file():
    import json
    import os
    try:
        if os.path.isfile(_PLAYER_META_PATH):
            data = json.load(open(_PLAYER_META_PATH, "r", encoding="utf-8"))
            _PLAYER_META["gold"] = int(data.get("gold", DEFAULT_GOLD))
            inv = data.get("inventory", [])
            if not isinstance(inv, list):
                inv = []
            _PLAYER_META["inventory"] = [str(x) for x in inv]
            return True
    except Exception as e:
        _log("meta load file " + str(e))
    return False


def _meta_save_file():
    import json
    import os
    try:
        d = os.path.dirname(_PLAYER_META_PATH)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        json.dump(
            {"gold": int(_PLAYER_META["gold"]), "inventory": list(_PLAYER_META["inventory"])},
            open(_PLAYER_META_PATH, "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2,
        )
        return True
    except Exception as e:
        _log("meta save file " + str(e))
        return False


def _meta_pull_gi(gi):
    if gi is None:
        return False
    ok = False
    try:
        g = gi.get_editor_property("Gold")
        _PLAYER_META["gold"] = int(g)
        ok = True
    except Exception:
        pass
    try:
        inv = gi.get_editor_property("Inventory")
        _PLAYER_META["inventory"] = [str(x) for x in list(inv or [])]
        ok = True
    except Exception:
        pass
    return ok


def _meta_push_gi(gi):
    if gi is None:
        return False
    ok = False
    try:
        gi.set_editor_property("Gold", int(_PLAYER_META["gold"]))
        ok = True
    except Exception:
        pass
    try:
        gi.set_editor_property("Inventory", list(_PLAYER_META["inventory"]))
        ok = True
    except Exception:
        pass
    return ok


def ensure_player_meta(world_ctx=None):
    """Init Gold/Inventory once per session. Module+JSON is source of truth; push into GI."""
    if not _PLAYER_META["ready"]:
        if not _meta_load_file():
            _PLAYER_META["gold"] = int(DEFAULT_GOLD)
            _PLAYER_META["inventory"] = []
        _PLAYER_META["ready"] = True
        # Do NOT pull GI here — GI CDO default (often 100) would wipe DEFAULT_GOLD/file.
        gi = _gi_from_world(world_ctx)
        _meta_push_gi(gi)
        _meta_save_file()
    else:
        gi = _gi_from_world(world_ctx)
        _meta_push_gi(gi)
    return _PLAYER_META


def get_gold(world_ctx=None):
    ensure_player_meta(world_ctx)
    return int(_PLAYER_META["gold"])


def set_gold(amount, world_ctx=None):
    ensure_player_meta(world_ctx)
    _PLAYER_META["gold"] = int(amount)
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    return _PLAYER_META["gold"]


def add_gold(delta, world_ctx=None):
    return set_gold(get_gold(world_ctx) + int(delta), world_ctx)


def spend_gold(cost, world_ctx=None):
    """Return True if spent; False if not enough."""
    cost = int(cost)
    g = get_gold(world_ctx)
    if g < cost:
        return False
    set_gold(g - cost, world_ctx)
    return True


def get_inventory(world_ctx=None):
    ensure_player_meta(world_ctx)
    return list(_PLAYER_META["inventory"])


def add_item(item_name, world_ctx=None):
    ensure_player_meta(world_ctx)
    _PLAYER_META["inventory"].append(str(item_name))
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    return list(_PLAYER_META["inventory"])


def clear_progress(world_ctx=None):
    """New-save wipe: gold back to DEFAULT_GOLD, inventory empty."""
    _PLAYER_META["gold"] = int(DEFAULT_GOLD)
    _PLAYER_META["inventory"] = []
    _PLAYER_META["ready"] = True
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    _log("clear_progress gold=%s inv=0" % _PLAYER_META["gold"])
    return True


def enter_dungeon(world_ctx):
    """OpenLevel to Map_Dungeon1 (fallback Map_Dungeon) when E near red gate."""
    if world_ctx is None:
        return False
    level = resolve_dungeon_level()
    close_shop(world_ctx)
    _reset_ui_after_travel("enter_dungeon")
    _LAST_WORLD_KEY[0] = None  # force tick to rebind on next world
    _print(world_ctx, u"进入地下城…", (1.0, 0.85, 0.2, 1.0), 2.0)
    try:
        unreal.GameplayStatics.open_level(world_ctx, level, True, "")
        _log("OpenLevel " + level)
        return True
    except Exception as e:
        _log("OpenLevel fail " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + level)
        _log("console Open " + level)
        return True
    except Exception as e2:
        _log("console Open fail " + str(e2))
        _print(world_ctx, u"进关失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)
        return False


def enter_dungeon2(world_ctx):
    """OpenLevel to Map_Dungeon2 when E near Map_Dungeon1 stairs / exit behind skeleton."""
    if world_ctx is None:
        return False
    close_shop(world_ctx)
    _reset_ui_after_travel("enter_dungeon2")
    _LAST_WORLD_KEY[0] = None
    _print(world_ctx, u"进入地下城2层", (1.0, 0.85, 0.2, 1.0), 2.0)
    level = DUNGEON2_LEVEL
    try:
        unreal.GameplayStatics.open_level(world_ctx, level, True, "")
        _log("OpenLevel " + level)
        return True
    except Exception as e:
        _log("OpenLevel dungeon2 fail " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + level)
        _log("console Open " + level)
        return True
    except Exception as e2:
        _log("console Open dungeon2 fail " + str(e2))
        _print(world_ctx, u"进2层失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)
        return False


def return_to_hub(world_ctx):
    """OpenLevel to Map_Hub (true hub return — not the Map_Dungeon1 skeleton exit)."""
    if world_ctx is None:
        return False
    close_shop(world_ctx)
    _reset_ui_after_travel("return_to_hub")
    _LAST_WORLD_KEY[0] = None
    _print(world_ctx, u"返回主城…", (0.4, 0.9, 1.0, 1.0), 2.0)
    try:
        unreal.GameplayStatics.open_level(world_ctx, HUB_LEVEL, True, "")
        _log("OpenLevel " + HUB_LEVEL)
        return True
    except Exception as e:
        _log("OpenLevel hub fail " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + HUB_LEVEL)
        _log("console Open " + HUB_LEVEL)
        return True
    except Exception as e2:
        _log("console Open hub fail " + str(e2))
        _print(world_ctx, u"回城失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)
        return False


def _load_attack_anim():
    for p in ATTACK_ANIM_PATHS:
        a = None
        try:
            a = unreal.load_asset(p)
        except Exception:
            a = None
        if a is None:
            try:
                a = unreal.EditorAssetLibrary.load_asset(p)
            except Exception:
                a = None
        if a is not None:
            return a, p
    return None, None


def _load_attack_montage():
    try:
        m = unreal.load_asset(ATTACK_MONTAGE_PATH)
        if m is not None:
            return m
    except Exception:
        pass
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(ATTACK_MONTAGE_PATH):
            return unreal.EditorAssetLibrary.load_asset(ATTACK_MONTAGE_PATH)
    except Exception:
        pass
    return None


def _get_pawn_mesh(pawn):
    if pawn is None:
        return None
    mesh = None
    try:
        mesh = pawn.get_editor_property("mesh")
    except Exception:
        mesh = None
    if mesh is None:
        try:
            mesh = pawn.mesh
        except Exception:
            mesh = None
    if mesh is None:
        try:
            for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent):
                mesh = c
                break
        except Exception:
            pass
    return mesh


# Attack restore: [until_time, mesh, anim_class]
_ATTACK_RESTORE = [0.0, None, None]


def _restore_attack_anim_if_due():
    until, mesh, anim_cls = _ATTACK_RESTORE
    if mesh is None or until <= 0.0:
        return
    if time.time() < until:
        return
    try:
        if anim_cls is not None:
            try:
                mesh.set_editor_property("anim_class", anim_cls)
            except Exception:
                pass
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
        # Nudge AnimBP to resume
        try:
            mesh.init_anim(True)
        except Exception:
            pass
        _log("attack: restored AnimBP cls=%s" % (anim_cls,))
    except Exception as e:
        _log("attack restore " + str(e))
    _ATTACK_RESTORE[0] = 0.0
    _ATTACK_RESTORE[1] = None
    _ATTACK_RESTORE[2] = None


def _mesh_skeleton_name(mesh):
    try:
        skm = mesh.get_editor_property("skeletal_mesh")
        if skm is None:
            skm = mesh.skeletal_mesh
        if skm is None:
            return ""
        sk = skm.get_editor_property("skeleton")
        return sk.get_name() if sk else ""
    except Exception:
        return ""


def _anim_skeleton_name(seq):
    try:
        sk = seq.get_editor_property("skeleton")
        return sk.get_name() if sk else ""
    except Exception:
        return ""


def _pick_attack_anim_matching(mesh):
    """Prefer Chop_Rig whose skeleton matches the pawn mesh."""
    want = _mesh_skeleton_name(mesh)
    first = None
    first_p = None
    for p in ATTACK_ANIM_PATHS:
        a = None
        try:
            a = unreal.load_asset(p)
        except Exception:
            a = None
        if a is None:
            try:
                a = unreal.EditorAssetLibrary.load_asset(p)
            except Exception:
                a = None
        if a is None:
            continue
        if first is None:
            first, first_p = a, p
        if want and _anim_skeleton_name(a) == want:
            return a, p, want
    return first, first_p, want


def try_attack(world, pawn):
    """Play 1H Chop. V15e: keep AnimBP; prefer DefaultSlot dynamic montage (upper-body
    overlay once ABP has Slot+LayeredBlendPerBone on spine). Fall back to single-node
    only if slot/montage path fails so attack still works before the graph is wired.
    """
    if pawn is None or world is None:
        return False
    if _OPEN_WIDGET[0] is not None:
        return False
    now = time.time()
    if (now - _LAST_ATTACK_T[0]) < ATTACK_COOLDOWN:
        return False
    # If previous single-node attack still playing, ignore
    if _ATTACK_RESTORE[1] is not None and now < _ATTACK_RESTORE[0]:
        return False
    mesh = _get_pawn_mesh(pawn)
    if mesh is None:
        _log("attack: no mesh")
        return False
    seq, sp, mesh_sk = _pick_attack_anim_matching(mesh)
    if seq is None:
        _log("attack: no chop anim asset")
        return False
    anim_sk = _anim_skeleton_name(seq)
    _log("attack: mesh_sk=%s anim_sk=%s path=%s" % (mesh_sk, anim_sk, sp))
    duration = 0.7
    try:
        duration = float(seq.get_editor_property("sequence_length") or 0.7)
    except Exception:
        try:
            duration = float(seq.sequence_length)
        except Exception:
            duration = 0.7
    if duration < 0.25:
        duration = 0.55
    played = False
    via = ""
    anim_inst = None
    try:
        anim_inst = mesh.get_anim_instance()
    except Exception:
        anim_inst = None
    # Ensure Animation Blueprint mode so Slot/loco keep running
    if anim_inst is not None:
        try:
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
        except Exception:
            pass
    # 1) DefaultSlot dynamic montage — keeps loco ABP; upper body chops after graph wire
    if (not played) and anim_inst is not None:
        for slot_name in ("DefaultSlot", "UpperBody", "FullBody"):
            try:
                dyn = anim_inst.play_slot_animation_as_dynamic_montage(
                    seq, slot_name, 0.1, 0.15, 1.0, 1, -1.0, 0.0
                )
                # UE may return a montage even when Slot is not wired into AnimGraph
                # (silent no-op). Only accept if the slot/montage is actually playing.
                ok = False
                if dyn is not None:
                    try:
                        ok = bool(anim_inst.is_playing_slot_animation(seq, slot_name))
                    except Exception:
                        ok = False
                    if not ok:
                        try:
                            ok = bool(anim_inst.montage_is_playing(dyn))
                        except Exception:
                            ok = False
                    if not ok:
                        try:
                            ok = bool(anim_inst.is_any_montage_playing())
                        except Exception:
                            ok = False
                if ok:
                    played = True
                    via = "slot_dyn:%s" % slot_name
                    try:
                        duration = float(dyn.get_editor_property("sequence_length") or duration)
                    except Exception:
                        pass
                    _log("attack: slot_dyn OK slot=%s mont=%s" % (slot_name, dyn))
                    break
                else:
                    _log("attack: slot_dyn %s inert (Slot not in graph?) dyn=%s" % (slot_name, dyn))
            except Exception as e:
                _log("attack slot_dyn %s %s" % (slot_name, e))
            if played:
                break
            try:
                length = anim_inst.play_slot_animation(seq, slot_name, 0.1, 0.15, 1.0, 1)
                ok = False
                if length and float(length) > 0.01:
                    try:
                        ok = bool(anim_inst.is_playing_slot_animation(seq, slot_name))
                    except Exception:
                        ok = True  # length>0 is weak signal; prefer is_playing when available
                if ok:
                    played = True
                    via = "slot_play:%s" % slot_name
                    duration = float(length)
                    _log("attack: slot_play OK slot=%s len=%.2f" % (slot_name, float(length)))
                    break
                else:
                    _log("attack: slot_play %s inert len=%s" % (slot_name, length))
            except Exception as e:
                _log("attack slot_play %s %s" % (slot_name, e))
    # 2) Real AnimMontage asset if present
    if (not played) and anim_inst is not None:
        mont = _load_attack_montage()
        if mont is not None:
            try:
                length = anim_inst.montage_play(mont, 1.0)
                if length and float(length) > 0.01:
                    played = True
                    via = "montage_play"
                    duration = float(length)
                    _log("attack: montage_play len=%.2f" % float(length))
                else:
                    _log("attack: montage_play returned 0 — ignore")
            except Exception as e:
                _log("attack montage_play " + str(e))
    # 3) Last resort: single-node (full-body; feet slide if moving) — until Slot is wired
    if not played:
        anim_cls = None
        try:
            anim_cls = mesh.get_editor_property("anim_class")
        except Exception:
            anim_cls = None
        try:
            try:
                mesh.set_editor_property("anim_class", None)
            except Exception:
                pass
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            used = ""
            try:
                mesh.override_animation_data(seq, False, False, 0.0, 1.0)
                used = "override_animation_data"
            except Exception as e_ov:
                _log("attack override_animation_data " + str(e_ov))
                try:
                    mesh.set_editor_property("animation", seq)
                except Exception:
                    try:
                        mesh.set_animation(seq)
                    except Exception:
                        pass
                try:
                    mesh.play_animation(seq, False)
                    used = "play_animation"
                except Exception:
                    mesh.play(False)
                    used = "play"
            _ATTACK_RESTORE[0] = now + duration + 0.08
            _ATTACK_RESTORE[1] = mesh
            _ATTACK_RESTORE[2] = anim_cls
            played = True
            via = "single-node:" + used
            _log("attack: single-node fallback %s via=%s dur=%.2f (wire Slot+Layered for no foot-slide)" % (sp, used, duration))
        except Exception as e:
            _log("attack single-node " + str(e))
            try:
                mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
                if anim_cls is not None:
                    mesh.set_editor_property("anim_class", anim_cls)
            except Exception:
                pass
    if played:
        _LAST_ATTACK_T[0] = now
        _print(world, u"挥砍！", (1.0, 0.7, 0.2, 1.0), 0.5)
        _log("attack OK via=%s dur=%.2f" % (via, duration))
        return True
    _log("attack FAIL")
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
    shop_key, title, gate, hub_exit = scan_near(world, pawn.get_actor_location())
    if shop_key and title:
        _NEAR_SHOP[0] = (shop_key, title)
    else:
        _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = gate
    _NEAR_EXIT[0] = hub_exit
    # Dungeon stairs exit wins in Map_Dungeon1; hub gate wins over shop in Map_Hub.
    if hub_exit and _world_is_dungeon(world):
        _log("E near dungeon exit -> enter_dungeon2")
        return enter_dungeon2(world)
    if gate:
        _log("E near gate -> enter_dungeon (shop_key=%s)" % (shop_key,))
        return enter_dungeon(world)
    if shop_key and title:
        return open_shop(world, shop_key, title)
    _log("E ignored — not near shop/gate/exit")
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
    if name in ("LeftMouseButton", "LMB"):
        return (
            _ue_key_down(pc, "LeftMouseButton")
            or _win_key_down(_VK_LBUTTON)
        )
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


def _load_health_wbp_class():
    for p in HEALTH_WBP_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                return cls, p
        except Exception:
            pass
    # Fallback load via asset generated class
    try:
        wbp = unreal.EditorAssetLibrary.load_asset("/Game/UI/HUD/WBP_PlayerHealthBar")
        if wbp:
            try:
                unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
            except Exception:
                pass
            gc = wbp.generated_class()
            if gc:
                return gc, gc.get_path_name()
    except Exception as e:
        _log("health wbp load " + str(e))
    return None, None


def _float_prop(obj, names, default):
    for n in names:
        try:
            v = obj.get_editor_property(n)
            if v is not None:
                return float(v)
        except Exception:
            pass
        try:
            v = getattr(obj, n)
            if v is not None and not callable(v):
                return float(v)
        except Exception:
            pass
    if default is None:
        return None
    return float(default)


def _outer_chain_contains(obj, root):
    """True if root appears in obj's Outer chain (same widget tree ownership)."""
    if obj is None or root is None:
        return False
    try:
        cur = obj
        for _ in range(24):
            if cur is None:
                return False
            if cur == root:
                return True
            try:
                cur = cur.get_outer()
            except Exception:
                return False
    except Exception:
        return False
    return False


def _find_named_widget(root, name):
    """Find named child under THIS user widget only (never steal player HUD PB_Health)."""
    if root is None or not name:
        return None
    try:
        if hasattr(root, "get_name") and root.get_name() == name:
            return root
    except Exception:
        pass
    try:
        w = root.get_widget_from_name(name)
        if w and _outer_chain_contains(w, root):
            return w
    except Exception:
        pass
    # Walk WidgetTree.root_widget + panel children
    try:
        stack = []
        try:
            wt = root.get_editor_property("widget_tree")
            if wt is not None:
                rw = wt.get_editor_property("root_widget")
                if rw is not None:
                    stack.append(rw)
        except Exception:
            pass
        try:
            n = int(root.get_children_count())
            for i in range(n):
                ch = root.get_child_at(i)
                if ch is not None:
                    stack.append(ch)
        except Exception:
            pass
        seen = set()
        while stack:
            cur = stack.pop()
            try:
                cid = int(cur.get_unique_id())
            except Exception:
                cid = id(cur)
            if cid in seen:
                continue
            seen.add(cid)
            try:
                if cur.get_name() == name:
                    return cur
            except Exception:
                pass
            try:
                kids = cur.get_all_children()
                if kids:
                    for k in kids:
                        if k is not None:
                            stack.append(k)
            except Exception:
                pass
            try:
                n = int(cur.get_children_count())
                for i in range(n):
                    ch = cur.get_child_at(i)
                    if ch is not None:
                        stack.append(ch)
            except Exception:
                pass
    except Exception:
        pass
    # Scoped ObjectIterator: Outer chain MUST reach root (no map-prefix match).
    try:
        base = root.get_path_name()
    except Exception:
        base = None
    if base:
        try:
            for o in unreal.ObjectIterator(unreal.Widget):
                try:
                    if o.get_name() != name:
                        continue
                except Exception:
                    continue
                if not _outer_chain_contains(o, root):
                    # Path prefix fallback only with FULL userwidget path, never map-only.
                    try:
                        op = o.get_path_name()
                    except Exception:
                        continue
                    if not (op.startswith(base + ".") or op.startswith(base + ":") or op.startswith(base + "/")):
                        continue
                return o
        except Exception:
            pass
        try:
            for o in unreal.ObjectIterator(unreal.ProgressBar):
                try:
                    if o.get_name() != name:
                        continue
                except Exception:
                    continue
                if _outer_chain_contains(o, root):
                    return o
                try:
                    op = o.get_path_name()
                except Exception:
                    continue
                if op.startswith(base + ".") or op.startswith(base + ":") or op.startswith(base + "/"):
                    return o
        except Exception:
            pass
    return None



def _uobj_alive(obj):
    """True if UObject ref is still valid (not pending-kill after OpenLevel)."""
    if obj is None:
        return False
    try:
        if hasattr(unreal, "is_valid") and (not unreal.is_valid(obj)):
            return False
    except Exception:
        pass
    try:
        # Touching path_name throws / returns junk on dead objects in some builds
        _ = obj.get_path_name()
        if not _:
            return False
    except Exception:
        return False
    return True


def _world_key(world):
    if world is None:
        return None
    try:
        return str(world.get_path_name())
    except Exception:
        try:
            return str(world)
        except Exception:
            return "world"


def _reset_ui_after_travel(reason="travel"):
    """Clear HUD / enemy bar caches so ensure_* recreates on Hub and Map_Dungeon1."""
    try:
        close_shop(None)
    except Exception:
        pass
    try:
        _clear_health_hud()
    except Exception:
        pass
    try:
        _clear_gold_hud()
    except Exception:
        pass
    try:
        _clear_enemy_bars()
    except Exception:
        pass
    try:
        _ENEMY_HP_CACHE.clear()
    except Exception:
        pass
    _PENDING_ATTACK_HIT[0] = None
    _DUNGEON_PAWN_TRIED[0] = False
    _VIEW_FIXED[0] = False
    _LAST_HINT_KEY[0] = None
    _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = False
    _NEAR_EXIT[0] = False
    _PREV_E[0] = False
    _PREV_ESC[0] = False
    _PREV_LMB[0] = False
    _log("T278 reset UI after " + str(reason))


def _clear_health_hud():
    w = _HEALTH_WIDGET[0]
    _HEALTH_WIDGET[0] = None
    _HEALTH_BAR[0] = None
    _HEALTH_TXT[0] = None
    if w is None:
        return
    if not _uobj_alive(w):
        return
    # Player HUD was AddToViewport — never treat like WidgetComponent child
    try:
        w.remove_from_viewport()
    except Exception:
        try:
            w.remove_from_parent()
        except Exception:
            pass



def _clear_gold_hud():
    w = _GOLD_WIDGET[0]
    _GOLD_WIDGET[0] = None
    _GOLD_TXT[0] = None
    if w is None:
        return
    if not _uobj_alive(w):
        return
    try:
        w.remove_from_viewport()
    except Exception:
        try:
            w.remove_from_parent()
        except Exception:
            pass


def ensure_health_hud(world, pc, pawn):
    """Screen-space HUD: ProgressBar fixed top-left. Recreates after OpenLevel travel."""
    if world is None or pc is None or pawn is None:
        return
    # Only for player knight-ish pawn
    try:
        pname = pawn.get_name() or ""
        clsname = pawn.get_class().get_name() if pawn.get_class() else ""
    except Exception:
        pname, clsname = "", ""
    if ("KayKit" not in pname) and ("KayKit" not in clsname) and ("Knight" not in clsname):
        # Still allow if Health var exists
        try:
            pawn.get_editor_property("Health")
        except Exception:
            return

    # T278: stale refs after Hub<->Dungeon OpenLevel block re-init — drop them
    w_existing = _HEALTH_WIDGET[0]
    if w_existing is not None:
        alive = _uobj_alive(w_existing)
        if not alive:
            _log("ensure_health_hud: dead HUD ref -> recreate")
            _HEALTH_WIDGET[0] = None
            _HEALTH_BAR[0] = None
            _HEALTH_TXT[0] = None
        else:
            # Survived travel object-wise but may have left viewport — reattach
            in_vp = True
            try:
                in_vp = bool(w_existing.is_in_viewport())
            except Exception:
                in_vp = True
            if not in_vp:
                try:
                    w_existing.add_to_viewport(50)
                    _log("ensure_health_hud: re-AddToViewport")
                except Exception as e:
                    _log("ensure_health_hud: reattach fail " + str(e) + " -> recreate")
                    try:
                        w_existing.remove_from_viewport()
                    except Exception:
                        pass
                    _HEALTH_WIDGET[0] = None
                    _HEALTH_BAR[0] = None
                    _HEALTH_TXT[0] = None

    if _HEALTH_WIDGET[0] is None:
        wcls, wpath = _load_health_wbp_class()
        if not wcls:
            _log("ensure_health_hud: no WBP class")
            return
        widget = None
        wbl = _wbl()
        if wbl:
            for attempt in (
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": world, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": pc, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method("create", (world, wcls, pc)),
                lambda: wbl.call_method("create", (pc, wcls, pc)),
            ):
                try:
                    widget = attempt()
                    if widget:
                        break
                except Exception as e:
                    _log("health create " + str(e))
        if not widget:
            try:
                widget = unreal.new_object(wcls, pc)
            except Exception as e:
                _log("health new_object " + str(e))
                return
        if not widget:
            _log("ensure_health_hud create null")
            return
        try:
            widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        try:
            # Below shop (200) but above world; screen HUD
            widget.add_to_viewport(50)
        except Exception as e:
            _log("health viewport " + str(e))
            return
        # Keep default layout (top-left canvas anchors). Do NOT set desired size full-screen.
        _HEALTH_WIDGET[0] = widget
        pb = None
        try:
            pb = widget.get_widget_from_name("PB_Health")
        except Exception:
            pb = None
        if pb is None:
            try:
                pb = _find_named_widget(widget, "PB_Health")
            except Exception:
                pb = None
        _HEALTH_BAR[0] = pb
        # Force top-left screen HUD even if Designer offsets drifted off-screen
        try:
            if pb is not None and getattr(pb, "slot", None) is not None:
                try:
                    anc = unreal.Anchors(); anc.minimum = unreal.Vector2D(0.0, 0.0); anc.maximum = unreal.Vector2D(0.0, 0.0); pb.slot.set_anchors(anc)
                except Exception:
                    pass
                try:
                    pb.slot.set_alignment(unreal.Vector2D(0.0, 0.0))
                except Exception:
                    pass
                try:
                    pb.slot.set_offsets(unreal.Margin(48.0, 36.0, 300.0, 24.0))
                except Exception:
                    try:
                        pb.slot.set_position(unreal.Vector2D(48.0, 36.0))
                        pb.slot.set_size(unreal.Vector2D(300.0, 24.0))
                    except Exception:
                        pass
                try:
                    pb.set_visibility(unreal.SlateVisibility.VISIBLE)
                except Exception:
                    pass
        except Exception as e:
            _log("health slot force " + str(e))
        try:
            _HEALTH_TXT[0] = widget.get_widget_from_name("Txt_HP")
        except Exception:
            _HEALTH_TXT[0] = None
        _log("ensure_health_hud created %s pb=%s" % (wpath, pb))

    # Update percent from pawn Health / MaxHealth
    health = _float_prop(pawn, ("Health", "health", "HP", "Hp"), 100.0)
    maxh = _float_prop(pawn, ("MaxHealth", "max_health", "MaxHP", "MaxHp"), 100.0)
    if maxh <= 0.0001:
        maxh = 100.0
    pct = health / maxh
    if pct < 0.0:
        pct = 0.0
    if pct > 1.0:
        pct = 1.0
    pb = _HEALTH_BAR[0]
    if pb is not None:
        try:
            pb.set_percent(pct)
        except Exception:
            try:
                pb.set_editor_property("percent", pct)
            except Exception:
                pass
    txt = _HEALTH_TXT[0]
    if txt is not None:
        label = "HP %d/%d" % (int(round(health)), int(round(maxh)))
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass






def _load_gold_wbp_class():
    for p in GOLD_WBP_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                return cls, p
        except Exception:
            pass
    for asset_path in (
        "/Game/UI/HUD/WBP_PlayerGold",
        "/Game/UI/HUD/WBP_PlayerHealthBar",
    ):
        try:
            wbp = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not wbp:
                continue
            try:
                unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
            except Exception:
                pass
            gc = None
            try:
                gc = wbp.generated_class()
            except Exception:
                gc = None
            if gc:
                return gc, gc.get_path_name()
        except Exception as e:
            _log("gold wbp load " + str(e))
    return None, None



def _viewport_size_xy(world_ctx):
    """DPI-aware viewport size for HUD pinning. T313_GOLD_RIGHT."""
    try:
        sz = unreal.WidgetLayoutLibrary.get_viewport_size(world_ctx)
        x = float(sz.x)
        y = float(sz.y)
        if x > 32.0 and y > 32.0:
            return x, y
    except Exception:
        pass
    try:
        # Some builds expose get_viewport_widget_geometry
        geo = unreal.WidgetLayoutLibrary.get_viewport_widget_geometry(world_ctx)
        sz = geo.get_local_size()
        x = float(sz.x)
        y = float(sz.y)
        if x > 32.0 and y > 32.0:
            return x, y
    except Exception:
        pass
    return 1920.0, 1080.0


def _pin_gold_widget_top_right(widget, world_ctx):
    """Pin entire gold UserWidget to true viewport TOP-RIGHT (not left canvas). T313_GOLD_RIGHT."""
    if widget is None:
        return
    vx, vy = _viewport_size_xy(world_ctx if world_ctx is not None else widget)
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(280.0, 56.0))
    except Exception:
        pass
    try:
        # Pivot = top-right corner of the widget
        widget.set_alignment_in_viewport(unreal.Vector2D(1.0, 0.0))
    except Exception:
        pass
    px = float(vx) - 24.0
    if px < 120.0:
        px = float(vx) * 0.98
    py = 36.0
    try:
        widget.set_position_in_viewport(unreal.Vector2D(px, py), True)
    except Exception:
        try:
            widget.set_position_in_viewport(unreal.Vector2D(px, py))
        except Exception:
            pass


def _layout_gold_text_in_small_widget(txt):
    """Text sits top-left inside the small gold widget (widget itself is top-right)."""
    if txt is None or getattr(txt, "slot", None) is None:
        return
    slot = None
    try:
        slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(txt)
    except Exception:
        slot = txt.slot
    if slot is None:
        return
    try:
        anc = unreal.Anchors()
        anc.minimum = unreal.Vector2D(0.0, 0.0)
        anc.maximum = unreal.Vector2D(0.0, 0.0)
        slot.set_anchors(anc)
    except Exception:
        try:
            anc = unreal.Anchors()
            anc.minimum = unreal.Vector2D(0.0, 0.0)
            anc.maximum = unreal.Vector2D(0.0, 0.0)
            slot.set_editor_property("anchors", anc)
        except Exception:
            pass
    try:
        slot.set_alignment(unreal.Vector2D(0.0, 0.0))
    except Exception:
        pass
    try:
        # Point-anchor: Right/Bottom = width/height
        slot.set_offsets(unreal.Margin(0.0, 0.0, 280.0, 48.0))
    except Exception:
        try:
            slot.set_position(unreal.Vector2D(0.0, 0.0))
            slot.set_size(unreal.Vector2D(280.0, 48.0))
        except Exception:
            pass
    try:
        slot.set_auto_size(True)
    except Exception:
        pass


def ensure_gold_hud(world, pc, pawn=None):
    """Screen-space Gold text fixed top-RIGHT. Recreates after OpenLevel travel. T313_GOLD_RIGHT."""
    if world is None or pc is None:
        return
    try:
        ensure_player_meta(world)
    except Exception:
        pass

    w_existing = _GOLD_WIDGET[0]
    if w_existing is not None:
        alive = _uobj_alive(w_existing)
        if not alive:
            _log("ensure_gold_hud: dead HUD ref -> recreate")
            _GOLD_WIDGET[0] = None
            _GOLD_TXT[0] = None
        else:
            in_vp = True
            try:
                in_vp = bool(w_existing.is_in_viewport())
            except Exception:
                in_vp = True
            if not in_vp:
                try:
                    w_existing.add_to_viewport(51)
                    _log("ensure_gold_hud: re-AddToViewport")
                except Exception as e:
                    _log("ensure_gold_hud: reattach fail " + str(e) + " -> recreate")
                    try:
                        w_existing.remove_from_viewport()
                    except Exception:
                        pass
                    _GOLD_WIDGET[0] = None
                    _GOLD_TXT[0] = None

    if _GOLD_WIDGET[0] is None:
        wcls, wpath = _load_gold_wbp_class()
        if not wcls:
            _log("ensure_gold_hud: no WBP class")
            return
        widget = None
        wbl = _wbl()
        if wbl:
            for attempt in (
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": world, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method(
                    "create", (),
                    {"world_context_object": pc, "widget_type": wcls, "owning_player": pc},
                ),
                lambda: wbl.call_method("create", (world, wcls, pc)),
                lambda: wbl.call_method("create", (pc, wcls, pc)),
            ):
                try:
                    widget = attempt()
                    if widget:
                        break
                except Exception as e:
                    _log("gold create " + str(e))
        if not widget:
            try:
                widget = unreal.new_object(wcls, pc)
            except Exception as e:
                _log("gold new_object " + str(e))
                return
        if not widget:
            _log("ensure_gold_hud create null")
            return
        try:
            widget.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        try:
            widget.add_to_viewport(51)
        except Exception as e:
            _log("gold viewport " + str(e))
            return
        _GOLD_WIDGET[0] = widget

        # Prefer Txt_Gold; else TextBlock_0 (WBP_PlayerGold from Shop2); else Txt_HP
        txt = None
        for nm in ("Txt_Gold", "TextBlock_0", "Txt_HP"):
            try:
                txt = widget.get_widget_from_name(nm)
            except Exception:
                txt = None
            if txt is None:
                try:
                    txt = _find_named_widget(widget, nm)
                except Exception:
                    txt = None
            if txt is not None:
                break
        if txt is None:
            # Last resort: first TextBlock under this UserWidget
            try:
                stack = []
                try:
                    wt = widget.get_editor_property("widget_tree")
                    if wt is not None:
                        rw = wt.get_editor_property("root_widget")
                        if rw is not None:
                            stack.append(rw)
                except Exception:
                    pass
                try:
                    n = int(widget.get_children_count())
                    for i in range(n):
                        ch = widget.get_child_at(i)
                        if ch is not None:
                            stack.append(ch)
                except Exception:
                    pass
                seen = set()
                while stack and txt is None:
                    cur = stack.pop()
                    try:
                        cid = int(cur.get_unique_id())
                    except Exception:
                        cid = id(cur)
                    if cid in seen:
                        continue
                    seen.add(cid)
                    try:
                        if cur.get_class() and cur.get_class().get_name() == "TextBlock":
                            txt = cur
                            break
                    except Exception:
                        pass
                    try:
                        kids = cur.get_all_children()
                        if kids:
                            for k in kids:
                                if k is not None:
                                    stack.append(k)
                    except Exception:
                        try:
                            cn = int(cur.get_children_count())
                            for i in range(cn):
                                k = cur.get_child_at(i)
                                if k is not None:
                                    stack.append(k)
                        except Exception:
                            pass
            except Exception as e:
                _log("gold txt scan " + str(e))
        if txt is None:
            try:
                txt = _find_textblock_under(widget)
            except Exception:
                txt = None
        _GOLD_TXT[0] = txt

        # Hide progress bar if we fell back to health WBP instance
        pb = None
        try:
            pb = widget.get_widget_from_name("PB_Health")
        except Exception:
            pb = None
        if pb is None:
            try:
                pb = _find_named_widget(widget, "PB_Health")
            except Exception:
                pb = None
        if pb is not None:
            try:
                pb.set_visibility(unreal.SlateVisibility.COLLAPSED)
            except Exception:
                try:
                    pb.set_visibility(unreal.SlateVisibility.HIDDEN)
                except Exception:
                    pass

        # T313_GOLD_RIGHT: pin WHOLE widget to viewport top-RIGHT.
        # (Previously widget sat at 0,0 left; text "right" anchor only meant right of a left-sized box.)
        try:
            _pin_gold_widget_top_right(widget, world)
        except Exception as e:
            _log("gold pin create " + str(e))
        try:
            _layout_gold_text_in_small_widget(txt)
        except Exception as e:
            _log("gold txt layout " + str(e))
        if txt is not None:
            try:
                txt.set_visibility(unreal.SlateVisibility.VISIBLE)
            except Exception:
                pass
            # High-contrast gold text in case Designer color was transparent
            try:
                txt.set_editor_property(
                    "color_and_opacity",
                    unreal.SlateColor(unreal.LinearColor(1.0, 0.9, 0.2, 1.0)),
                )
            except Exception:
                pass
            try:
                font = txt.get_editor_property("font")
                font.set_editor_property("size", 28)
                txt.set_editor_property("font", font)
            except Exception:
                pass
        _log("ensure_gold_hud created %s txt=%s T313_GOLD_RIGHT" % (wpath, txt))

    # Refresh gold number every tick (rebind TextBlock via ObjectIterator if needed)
    try:
        gold = int(get_gold(world))
    except Exception:
        gold = int(DEFAULT_GOLD)
    label = u"金币: %d" % gold
    try:
        wforce = _GOLD_WIDGET[0]
        if wforce is not None and _uobj_alive(wforce):
            wforce.set_visibility(unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    txt = _GOLD_TXT[0]
    if txt is None or (not _uobj_alive(txt)):
        try:
            txt = _find_textblock_under(_GOLD_WIDGET[0])
            _GOLD_TXT[0] = txt
        except Exception:
            txt = None
    if txt is not None:
        try:
            txt.set_visibility(unreal.SlateVisibility.VISIBLE)
        except Exception:
            pass
        # Keep widget pinned top-RIGHT every tick (resize / layout regress)
        try:
            wpin = _GOLD_WIDGET[0]
            if wpin is not None and _uobj_alive(wpin):
                _pin_gold_widget_top_right(wpin, world)
        except Exception:
            pass
        try:
            _layout_gold_text_in_small_widget(txt)
        except Exception:
            pass
        try:
            txt.set_text(unreal.Text(label))
        except Exception:
            try:
                txt.set_editor_property("text", unreal.Text(label))
            except Exception:
                pass
    else:
        # Path-scoped paint fallback (same as shop titles)
        w = _GOLD_WIDGET[0]
        if w is not None and _uobj_alive(w):
            try:
                base = w.get_path_name()
                for o in unreal.ObjectIterator(unreal.TextBlock):
                    try:
                        pn = o.get_path_name()
                    except Exception:
                        continue
                    if base not in pn:
                        continue
                    try:
                        o.set_visibility(unreal.SlateVisibility.VISIBLE)
                        o.set_text(unreal.Text(label))
                        _GOLD_TXT[0] = o
                        break
                    except Exception:
                        pass
            except Exception:
                pass



def _load_enemy_health_wbp_class():
    for p in ENEMY_HEALTH_WBP_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                return cls, p
        except Exception:
            pass
    for asset_path in (
        "/Game/UI/HUD/WBP_EnemyHealthBar",
        "/Game/UI/HUD/WBP_PlayerHealthBar",
    ):
        try:
            wbp = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not wbp:
                continue
            try:
                unreal.BlueprintEditorLibrary.compile_blueprint(wbp)
            except Exception:
                pass
            gc = None
            try:
                gc = wbp.generated_class()
            except Exception:
                try:
                    gc = unreal.EditorAssetLibrary.load_blueprint_class(asset_path)
                except Exception:
                    gc = None
            if gc:
                return gc, gc.get_path_name()
        except Exception as e:
            _log("enemy health wbp load " + str(e))
    return None, None


def _is_enemy_skeleton(actor):
    if actor is None:
        return False
    try:
        cn = actor.get_class().get_name() if actor.get_class() else ""
    except Exception:
        cn = ""
    if "BP_Enemy_Skeleton" in cn or "Enemy_Skeleton" in cn:
        return True
    try:
        n = actor.get_name() or ""
        if n.startswith("Preview_Skeleton") or "BP_Enemy_Skeleton" in n:
            return True
    except Exception:
        pass
    return False


def _enemy_key(actor):
    try:
        return actor.get_path_name()
    except Exception:
        return str(id(actor))


def _read_enemy_hp(actor, state):
    """Prefer actor Health/MaxHealth properties; else keep Python state."""
    health = _float_prop(actor, ("Health", "health", "HP", "Hp"), None)
    maxh = _float_prop(actor, ("MaxHealth", "max_health", "MaxHP", "MaxHp"), None)
    if maxh is None:
        maxh = state.get("max_health", _ENEMY_HP_DEFAULT)
    else:
        state["max_health"] = float(maxh)
    if health is None:
        health = state.get("health", state.get("max_health", _ENEMY_HP_DEFAULT))
    else:
        state["health"] = float(health)
    maxh = float(state.get("max_health", _ENEMY_HP_DEFAULT))
    health = float(state.get("health", maxh))
    if maxh <= 0.0001:
        maxh = _ENEMY_HP_DEFAULT
    if health < 0.0:
        health = 0.0
    if health > maxh:
        health = maxh
    state["health"] = health
    state["max_health"] = maxh
    return health, maxh


def _write_enemy_hp(actor, health, maxh):
    state_health = float(health)
    state_max = float(maxh)
    for name, val in (
        ("Health", state_health),
        ("MaxHealth", state_max),
        ("health", state_health),
        ("max_health", state_max),
    ):
        try:
            actor.set_editor_property(name, val)
        except Exception:
            try:
                setattr(actor, name, val)
            except Exception:
                pass
    return state_health, state_max


def _fit_enemy_bar_layout(widget, pb):
    """Force ProgressBar to fill a small fixed HUD rect (viewport overlay, not WC draw size)."""
    if pb is None:
        return
    if widget is not None and not _outer_chain_contains(pb, widget):
        try:
            pp = pb.get_path_name()
        except Exception:
            pp = "?"
        _log("fit skip: pb not under enemy widget " + pp)
        return
    slot = None
    try:
        slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb)
    except Exception:
        slot = None
    if slot is None:
        try:
            slot = pb.get_editor_property("slot")
        except Exception:
            slot = None
    if slot is not None:
        try:
            slot.set_anchors(unreal.Anchors(0.0, 0.0, 0.0, 0.0))
        except Exception:
            try:
                anc = unreal.Anchors()
                anc.minimum = unreal.Vector2D(0.0, 0.0)
                anc.maximum = unreal.Vector2D(0.0, 0.0)
                slot.set_anchors(anc)
            except Exception:
                pass
        try:
            slot.set_alignment(unreal.Vector2D(0.0, 0.0))
        except Exception:
            pass
        try:
            slot.set_auto_size(False)
        except Exception:
            pass
        try:
            slot.set_position(unreal.Vector2D(0.0, 0.0))
        except Exception:
            pass
        try:
            slot.set_size(unreal.Vector2D(float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])))
        except Exception:
            try:
                slot.set_offsets(unreal.Margin(0.0, 0.0, float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])))
            except Exception:
                pass
    try:
        pb.set_percent(1.0)
    except Exception:
        try:
            pb.set_editor_property("percent", 1.0)
        except Exception:
            pass
    try:
        pb.set_visibility(unreal.SlateVisibility.VISIBLE)
    except Exception:
        pass
    if widget is not None:
        for nm in ("Txt_HP", "Txt_Health", "TextBlock_0", "Img_HealthBg"):
            try:
                t = widget.get_widget_from_name(nm)
                if t:
                    t.set_visibility(unreal.SlateVisibility.COLLAPSED)
            except Exception:
                pass
        try:
            widget.set_desired_size_in_viewport(unreal.Vector2D(float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])))
        except Exception:
            pass


def _widget_in_viewport(w):
    if w is None:
        return False
    try:
        return bool(w.is_in_viewport())
    except Exception:
        return False


def _safe_remove_viewport_only(w):
    """RemoveFromParent/Viewport when widget is in the game viewport."""
    if w is None:
        return False
    if not _widget_in_viewport(w):
        # Still try remove_from_parent once — T285 bars are viewport-owned
        try:
            w.remove_from_parent()
            return True
        except Exception:
            try:
                w.remove_from_viewport()
                return True
            except Exception:
                return False
    try:
        w.remove_from_parent()
        return True
    except Exception:
        try:
            w.remove_from_viewport()
            return True
        except Exception:
            return False


def _destroy_enemy_wcs(actor):
    """Hide/destroy leftover WidgetComponent HP bars so only viewport overlay remains."""
    if actor is None:
        return
    try:
        comps = list(actor.get_components_by_class(unreal.WidgetComponent))
    except Exception:
        comps = []
    for c in comps:
        if c is None:
            continue
        try:
            nm = c.get_name() or ""
        except Exception:
            nm = ""
        if not (nm.startswith(_ENEMY_WC_NAME) or "EnemyHealth" in nm):
            # Still kill unnamed WC that looks like HP billboard if only one
            pass
        try:
            c.set_widget(None)
        except Exception:
            pass
        try:
            c.set_visibility(False, True)
        except Exception:
            try:
                c.set_hidden_in_game(True)
            except Exception:
                pass
        try:
            c.destroy_component(False)
        except Exception:
            try:
                c.unregister_component()
            except Exception:
                pass


def _release_enemy_widget(st, destroy_wc=False):
    """Remove viewport overlay and destroy any leftover WC."""
    if not st:
        return
    actor = st.get("actor")
    if actor is not None and _uobj_alive(actor):
        try:
            _destroy_enemy_wcs(actor)
        except Exception:
            pass
    wc = st.get("wc")
    if wc is not None and _uobj_alive(wc):
        try:
            wc.set_widget(None)
        except Exception:
            pass
        try:
            wc.destroy_component(False)
        except Exception:
            try:
                wc.unregister_component()
            except Exception:
                pass
    _safe_remove_viewport_only(st.get("widget"))
    st["wc"] = None
    st["widget"] = None
    st["pb"] = None
    st["in_viewport"] = False


def _purge_enemy_viewport_widgets():
    """Remove orphan enemy HP widgets not tracked in _ENEMY_BARS (stale door ghosts)."""
    try:
        wcls, _ = _load_enemy_health_wbp_class()
    except Exception:
        wcls = None
    removed = 0
    player_hud = _HEALTH_WIDGET[0]
    owned = set()
    try:
        for st in list(_ENEMY_BARS.values()):
            w = st.get("widget")
            if w is not None:
                owned.add(w)
    except Exception:
        owned = set()
    try:
        for o in unreal.ObjectIterator(unreal.UserWidget):
            try:
                if o is None:
                    continue
                if player_hud is not None and o == player_hud:
                    continue
                if o in owned:
                    continue
                cn = ""
                try:
                    cn = o.get_class().get_name() if o.get_class() else ""
                except Exception:
                    cn = ""
                is_enemy = ("EnemyHealth" in cn) or ("WBP_EnemyHealthBar" in cn)
                if not is_enemy and wcls is not None:
                    try:
                        is_enemy = bool(o.get_class() == wcls)
                    except Exception:
                        pass
                # Also catch player-class widgets that were wrongly used as enemy bars
                # only if they are in viewport AND not the player HUD
                if not is_enemy:
                    continue
                if _safe_remove_viewport_only(o):
                    removed += 1
            except Exception:
                continue
    except Exception as e:
        _log("purge enemy viewport " + str(e))
        return
    if removed:
        _log("purged %d stale enemy HP widgets" % removed)


def _enemy_root_component(actor):
    for getter in (
        lambda: actor.get_editor_property("mesh"),
        lambda: actor.mesh,
        lambda: actor.get_editor_property("capsule_component"),
        lambda: actor.capsule_component,
        lambda: actor.get_editor_property("root_component"),
        lambda: actor.root_component,
    ):
        try:
            c = getter()
            if c is not None:
                return c
        except Exception:
            continue
    return None



def _enemy_bar_z_offset(actor=None):
    """Simple height knob: BP float if present, else ENEMY_HP_BAR_Z_OFFSET at file top."""
    names = (
        "HealthBarHeightOffset",
        "HealthBarWorldZOffset",
        "HealthBarZOffset",
        "HPBarHeightOffset",
    )
    if actor is not None:
        v = _float_prop(actor, names, None)
        if v is not None:
            return float(v)
    return float(ENEMY_HP_BAR_Z_OFFSET)


def _enemy_head_world_loc(actor):
    """World location above THIS skeleton actor — never a door marker / stale cache.
    Base = head bone / mesh top / capsule top; then + _enemy_bar_z_offset(actor).
    """
    if actor is None:
        return None
    z_extra = _enemy_bar_z_offset(actor)
    mesh = None
    for getter in (
        lambda: actor.get_editor_property("mesh"),
        lambda: actor.mesh,
    ):
        try:
            mesh = getter()
            if mesh is not None:
                break
        except Exception:
            mesh = None
    # Bone / socket first (KayKit / Mixamo variants)
    if mesh is not None:
        for bone in (
            "head", "Head", "HeadTop_End", "mixamorig:Head", "mixamorig_Head",
            "neck_01", "Neck", "neck", "spine_03", "spine_02", "spine",
        ):
            try:
                loc = mesh.get_socket_location(bone)
                if loc is not None:
                    return unreal.Vector(
                        float(loc.x), float(loc.y), float(loc.z) + z_extra
                    )
            except Exception:
                continue
        # Mesh world bounds top center + editable offset
        try:
            origin = None
            extent = None
            try:
                origin, extent = mesh.get_component_bounds()
            except Exception:
                try:
                    box = mesh.bounds
                    origin = getattr(box, "origin", None)
                    extent = getattr(box, "box_extent", None) or getattr(box, "box_extent", None)
                except Exception:
                    pass
            if origin is not None and extent is not None:
                return unreal.Vector(
                    float(origin.x),
                    float(origin.y),
                    float(origin.z) + float(getattr(extent, "z", 40.0)) + z_extra,
                )
        except Exception:
            pass
        try:
            ml = mesh.get_world_location()
            return unreal.Vector(
                float(ml.x), float(ml.y), float(ml.z) + float(_ENEMY_BODY_FALLBACK_Z) + z_extra
            )
        except Exception:
            pass
    try:
        loc = actor.get_actor_location()
    except Exception:
        return None
    z_off = float(_ENEMY_BODY_FALLBACK_Z) + z_extra
    cap = None
    for getter in (
        lambda: actor.get_editor_property("capsule_component"),
        lambda: actor.capsule_component,
    ):
        try:
            cap = getter()
            if cap is not None:
                break
        except Exception:
            cap = None
    if cap is not None:
        try:
            hh = float(cap.get_scaled_capsule_half_height())
            z_off = hh + z_extra
        except Exception:
            try:
                hh = float(cap.get_editor_property("capsule_half_height"))
                z_off = float(hh) + z_extra
            except Exception:
                pass
    return unreal.Vector(float(loc.x), float(loc.y), float(loc.z) + z_off)


def _pc_camera_world_loc(pc):
    """Player camera world location for distance scale (nameplate feel)."""
    if pc is None:
        return None
    try:
        pcm = pc.get_editor_property("player_camera_manager")
        if pcm is not None:
            loc = pcm.get_camera_location()
            if loc is not None:
                return loc
    except Exception:
        pass
    try:
        pcm = pc.player_camera_manager
        if pcm is not None:
            loc = pcm.get_camera_location()
            if loc is not None:
                return loc
    except Exception:
        pass
    try:
        out = pc.get_player_view_point()
        if isinstance(out, (tuple, list)) and out:
            return out[0]
        if out is not None and hasattr(out, "x"):
            return out
    except Exception:
        pass
    try:
        pawn = None
        try:
            pawn = pc.get_controlled_pawn()
        except Exception:
            pawn = None
        if pawn is None:
            try:
                pawn = pc.k2_get_pawn()
            except Exception:
                try:
                    pawn = pc.get_pawn()
                except Exception:
                    pawn = None
        if pawn is not None:
            return pawn.get_actor_location()
    except Exception:
        pass
    return None


def _enemy_bar_dist_scale(cam_loc, head_loc):
    """scale = clamp(REF / distance). Near -> large, far -> small (world nameplate feel)."""
    if cam_loc is None or head_loc is None:
        return 1.0
    try:
        d = float(_dist(cam_loc, head_loc))
    except Exception:
        return 1.0
    if d < 1.0:
        d = 1.0
    s = float(ENEMY_HP_BAR_REF_DISTANCE) / d
    if s < float(ENEMY_HP_BAR_MIN_SCALE):
        s = float(ENEMY_HP_BAR_MIN_SCALE)
    if s > float(ENEMY_HP_BAR_MAX_SCALE):
        s = float(ENEMY_HP_BAR_MAX_SCALE)
    return s


def _apply_enemy_bar_scale(widget, pb, scale):
    """Flat HUD: RenderTransform scale around bottom-center; fallback resize draw size."""
    if widget is None:
        return float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])
    s = float(scale)
    if s < 0.05:
        s = 0.05
    base_w = float(_ENEMY_DRAW[0])
    base_h = float(_ENEMY_DRAW[1])
    used_render = False
    try:
        widget.set_render_transform_pivot(unreal.Vector2D(0.5, 1.0))
        used_render = True
    except Exception:
        try:
            widget.set_editor_property("render_transform_pivot", unreal.Vector2D(0.5, 1.0))
            used_render = True
        except Exception:
            used_render = False
    if used_render:
        try:
            widget.set_render_scale(unreal.Vector2D(s, s))
        except Exception:
            try:
                rt = unreal.WidgetTransform()
                rt.scale = unreal.Vector2D(s, s)
                widget.set_editor_property("render_transform", rt)
            except Exception:
                used_render = False
    # Always keep layout size = base when using render scale; else scale layout size
    draw_w = base_w
    draw_h = base_h
    if not used_render:
        draw_w = base_w * s
        draw_h = base_h * s
        if pb is not None:
            slot = None
            try:
                slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb)
            except Exception:
                slot = None
            if slot is not None:
                try:
                    slot.set_size(unreal.Vector2D(draw_w, draw_h))
                except Exception:
                    pass
    try:
        widget.set_desired_size_in_viewport(unreal.Vector2D(draw_w, draw_h))
    except Exception:
        pass
    return draw_w, draw_h


def _project_head_to_screen(pc, world_loc):
    """Return (ok, screen_x, screen_y) in viewport pixels."""
    if pc is None or world_loc is None:
        return False, 0.0, 0.0
    # Prefer WidgetLayoutLibrary (DPI-aware)
    try:
        out = unreal.Vector2D(0.0, 0.0)
        ok = unreal.WidgetLayoutLibrary.project_world_location_to_widget_position(pc, world_loc, out)
        # UE4.27 may return bool or (bool, Vector2D)
        if isinstance(ok, (tuple, list)):
            success = bool(ok[0])
            if len(ok) > 1 and ok[1] is not None:
                out = ok[1]
        else:
            success = bool(ok)
        if success:
            return True, float(out.x), float(out.y)
    except Exception:
        pass
    try:
        ok, screen = unreal.GameplayStatics.project_world_to_screen(pc, world_loc, True)
        if ok and screen is not None:
            return True, float(screen.x), float(screen.y)
    except Exception:
        pass
    try:
        screen = unreal.GameplayStatics.project_world_to_screen(pc, world_loc)
        if screen is not None:
            return True, float(screen.x), float(screen.y)
    except Exception:
        pass
    return False, 0.0, 0.0


def _create_enemy_user_widget(world, pc, wcls):
    """Create enemy HP UserWidget for AddToViewport overlay."""
    if wcls is None:
        return None
    widget = None
    wbl = _wbl()
    owner = pc if pc else world
    if wbl and world is not None:
        for attempt in (
            lambda: wbl.call_method(
                "create", (),
                {"world_context_object": world, "widget_type": wcls, "owning_player": pc},
            ),
            lambda: wbl.call_method(
                "create", (),
                {"world_context_object": owner, "widget_type": wcls, "owning_player": pc},
            ),
            lambda: wbl.call_method("create", (world, wcls, pc)),
            lambda: wbl.call_method("create", (owner, wcls, None)),
        ):
            try:
                widget = attempt()
                if widget:
                    break
            except Exception:
                widget = None
    if widget is None:
        try:
            widget = unreal.new_object(wcls, owner if owner is not None else unreal.Object)
        except Exception as e:
            _log("enemy widget new_object " + str(e))
            return None
    return widget


def _clear_enemy_bars(destroy_wc=False):
    for key, st in list(_ENEMY_BARS.items()):
        try:
            _release_enemy_widget(st, destroy_wc=True)
        except Exception:
            pass
    _ENEMY_BARS.clear()
    _purge_enemy_viewport_widgets()


def ensure_enemy_health_bars(world, pc, pawn=None):
    """T285/T290: flat screen HUD bars above live skeleton heads via ProjectWorldToScreen.
    Distance-scaled (near=big far=small) like a world nameplate; no tilted WidgetComponent.
    Purge bars whose actors died / left level. Tag: T290_DIST_SCALE.
    """
    if world is None or pc is None:
        return

    # T297_NO_ENEMY_HP: do not create/project enemy bars; purge leftovers only.
    if not ENEMY_HP_BARS_ENABLED:
        try:
            if _ENEMY_BARS:
                _clear_enemy_bars(True)
            else:
                _ENEMY_PURGE_ACC[0] += 0.016
                if _ENEMY_PURGE_ACC[0] >= 0.75:
                    _ENEMY_PURGE_ACC[0] = 0.0
                    _purge_enemy_viewport_widgets()
        except Exception:
            pass
        return


    # Throttled orphan purge (door ghosts / travel leftovers)
    try:
        _ENEMY_PURGE_ACC[0] += 0.016
        if _ENEMY_PURGE_ACC[0] >= 0.75 or not _ENEMY_BARS:
            _ENEMY_PURGE_ACC[0] = 0.0
            _purge_enemy_viewport_widgets()
    except Exception:
        pass

    enemies = []
    cls = None
    for p in _ENEMY_CLS_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                break
        except Exception:
            cls = None
    if cls:
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
                if a is not None and _uobj_alive(a):
                    enemies.append(a)
        except Exception as e:
            _log("enemy list class " + str(e))
    if not enemies:
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
                if _is_enemy_skeleton(a) and _uobj_alive(a):
                    enemies.append(a)
        except Exception as e:
            _log("enemy list scan " + str(e))

    wcls, wpath = _load_enemy_health_wbp_class()
    live = set()
    for actor in enemies:
        if actor is None or (not _uobj_alive(actor)):
            continue
        key = _enemy_key(actor)
        live.add(key)
        st = _ENEMY_BARS.get(key)
        if st is not None:
            st["actor"] = actor

        # Always strip 3D WidgetComponent so it cannot show tilted bars
        try:
            _destroy_enemy_wcs(actor)
        except Exception:
            pass

        if st is None:
            st = {
                "actor": actor,
                "health": _ENEMY_HP_DEFAULT,
                "max_health": _ENEMY_HP_DEFAULT,
                "wc": None,
                "widget": None,
                "pb": None,
                "in_viewport": False,
            }
            _read_enemy_hp(actor, st)
            _write_enemy_hp(actor, st["health"], st["max_health"])
            _ENEMY_BARS[key] = st

        # Recreate dead widget refs
        if st.get("widget") is not None and (not _uobj_alive(st.get("widget"))):
            st["widget"] = None
            st["pb"] = None
            st["in_viewport"] = False

        if st.get("widget") is None:
            if wcls is None:
                _log("enemy bar: no WBP class for " + key)
                continue
            widget = _create_enemy_user_widget(world, pc, wcls)
            if widget is None:
                _log("enemy bar create failed " + key)
                continue
            pb = _find_named_widget(widget, "PB_Health")
            if pb is None:
                try:
                    for o in unreal.ObjectIterator(unreal.ProgressBar):
                        if _outer_chain_contains(o, widget):
                            pb = o
                            break
                except Exception:
                    pass
            # Refuse binding player HUD progress bar
            if pb is not None:
                try:
                    pp = pb.get_path_name()
                    if ("PlayerHealth" in pp) and ("EnemyHealth" not in pp):
                        _log("enemy pb refused player HUD bind: " + pp)
                        pb = None
                except Exception:
                    pass
            _fit_enemy_bar_layout(widget, pb)
            try:
                widget.set_visibility(unreal.SlateVisibility.VISIBLE)
            except Exception:
                pass
            try:
                widget.add_to_viewport(40)
                st["in_viewport"] = True
            except Exception as e:
                _log("enemy AddToViewport " + str(e))
                continue
            try:
                widget.set_desired_size_in_viewport(
                    unreal.Vector2D(float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1]))
                )
            except Exception:
                pass
            st["widget"] = widget
            st["pb"] = pb
            st["wc"] = None
            _log("enemy bar OK %s wbp=%s viewport=1 pb=%s" % (key, wpath, pb))

        # Sync HP percent
        health, maxh = _read_enemy_hp(actor, st)
        pct = 0.0 if maxh <= 0.0001 else (health / maxh)
        if pct < 0.0:
            pct = 0.0
        if pct > 1.0:
            pct = 1.0
        pb = st.get("pb")
        if pb is not None:
            try:
                pb.set_percent(pct)
            except Exception:
                try:
                    pb.set_editor_property("percent", pct)
                except Exception:
                    pass

        # Project THIS actor's head each tick — never reuse another actor's screen pos
        widget = st.get("widget")
        if widget is None or (not _uobj_alive(widget)):
            continue
        if not st.get("in_viewport"):
            try:
                widget.add_to_viewport(40)
                st["in_viewport"] = True
            except Exception:
                pass
        head = _enemy_head_world_loc(actor)
        ok, sx, sy = _project_head_to_screen(pc, head)
        if ok:
            cam = _pc_camera_world_loc(pc)
            scale = _enemy_bar_dist_scale(cam, head)
            draw_w, draw_h = _apply_enemy_bar_scale(widget, pb, scale)
            # Bottom-center of bar sits just above projected head (nameplate anchor)
            # T295_X_OFFSET: screen-pixel left/right nudge after ProjectWorldToScreen
            px = (sx + float(ENEMY_HP_BAR_X_OFFSET)) - float(draw_w) * 0.5
            py = sy - float(draw_h) - 4.0
            try:
                widget.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
            except Exception:
                try:
                    widget.set_visibility(unreal.SlateVisibility.VISIBLE)
                except Exception:
                    pass
            try:
                widget.set_position_in_viewport(unreal.Vector2D(px, py), False)
            except Exception as e:
                try:
                    widget.set_position_in_viewport(unreal.Vector2D(px, py), True)
                except Exception as e2:
                    _log("enemy screen pos " + str(e2))
        else:
            # Behind camera / off projection — hide so it does not stick by the door
            try:
                widget.set_visibility(unreal.SlateVisibility.COLLAPSED)
            except Exception:
                try:
                    widget.set_visibility(unreal.SlateVisibility.HIDDEN)
                except Exception:
                    pass

    # Drop bars for destroyed / missing enemies (stale door floaters)
    for key in list(_ENEMY_BARS.keys()):
        if key not in live:
            st = _ENEMY_BARS.pop(key, None)
            if not st:
                continue
            try:
                _release_enemy_widget(st, destroy_wc=True)
            except Exception:
                pass
            _log("enemy bar purged stale " + str(key))


def _list_live_enemy_actors(world):
    """Collect BP_Enemy_Skeleton actors (used when HP bars are off)."""
    enemies = []
    if world is None:
        return enemies
    cls = None
    for p in _ENEMY_CLS_PATHS:
        try:
            cls = unreal.load_class(None, p)
            if cls:
                break
        except Exception:
            cls = None
    if cls:
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
                if a is not None and _uobj_alive(a):
                    enemies.append(a)
        except Exception:
            pass
    if not enemies:
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
                if _is_enemy_skeleton(a) and _uobj_alive(a):
                    enemies.append(a)
        except Exception:
            pass
    return enemies



def _enemy_cache_key(actor):
    try:
        return actor.get_path_name()
    except Exception:
        return str(id(actor))


def _get_enemy_hp_state(actor):
    """Simple HP: prefer actor Health/MaxHealth, else Python cache, default 50."""
    key = _enemy_cache_key(actor)
    cached = _ENEMY_HP_CACHE.get(key)
    st = {
        "actor": actor,
        "health": _ENEMY_HP_DEFAULT,
        "max_health": _ENEMY_HP_DEFAULT,
        "pb": None,
    }
    if cached:
        st["health"] = float(cached.get("health", _ENEMY_HP_DEFAULT))
        st["max_health"] = float(cached.get("max_health", _ENEMY_HP_DEFAULT))
    try:
        _read_enemy_hp(actor, st)
    except Exception:
        pass
    # If actor had no props, keep cache/default
    if st.get("max_health", 0) <= 0.0001:
        st["max_health"] = _ENEMY_HP_DEFAULT
    if "health" not in st:
        st["health"] = st["max_health"]
    _ENEMY_HP_CACHE[key] = {
        "health": float(st["health"]),
        "max_health": float(st["max_health"]),
    }
    return st


def _set_enemy_hp_state(actor, health, maxh):
    health = max(0.0, float(health))
    maxh = float(maxh) if float(maxh) > 0.0001 else _ENEMY_HP_DEFAULT
    if health > maxh:
        health = maxh
    key = _enemy_cache_key(actor)
    _ENEMY_HP_CACHE[key] = {"health": health, "max_health": maxh}
    try:
        _write_enemy_hp(actor, health, maxh)
    except Exception:
        pass
    # also setattr so later getattr reads work even without UProperty
    for name, val in (("Health", health), ("MaxHealth", maxh), ("health", health), ("max_health", maxh)):
        try:
            setattr(actor, name, val)
        except Exception:
            pass
    return health, maxh


def _destroy_enemy_actor(actor):
    """Simple death: remove actor from level."""
    if actor is None:
        return False
    key = _enemy_cache_key(actor)
    try:
        _ENEMY_HP_CACHE.pop(key, None)
    except Exception:
        pass
    if key in _ENEMY_BARS:
        try:
            _release_enemy_widget(_ENEMY_BARS.pop(key), destroy_wc=True)
        except Exception:
            _ENEMY_BARS.pop(key, None)
    try:
        actor.destroy_actor()
        return True
    except Exception:
        pass
    try:
        actor.k2_destroy_actor()
        return True
    except Exception:
        pass
    return False


def _schedule_attack_hit(pawn):
    """LMB swing started: apply damage once after ATTACK_DAMAGE_DELAY seconds."""
    if pawn is None:
        return
    due = time.time() + float(ATTACK_DAMAGE_DELAY)
    _PENDING_ATTACK_HIT[0] = {"due": due, "pawn": pawn}
    _log("T299 schedule hit in %.2fs" % float(ATTACK_DAMAGE_DELAY))


def _process_pending_attack_hit(world, pawn_fallback=None):
    """If delayed hit is due, distance-check skeletons and apply damage once."""
    pending = _PENDING_ATTACK_HIT[0]
    if not pending:
        return
    if time.time() < float(pending.get("due", 0.0)):
        return
    _PENDING_ATTACK_HIT[0] = None
    pawn = pending.get("pawn") or pawn_fallback
    try:
        if pawn is None or (not _uobj_alive(pawn)):
            pawn = pawn_fallback
    except Exception:
        pawn = pawn_fallback
    try:
        _damage_enemies_near_attack(world, pawn)
    except Exception as e:
        _log("enemy dmg delayed " + str(e))


def _damage_enemies_near_attack(world, pawn):
    """Simple hit: nearby skeletons lose ATTACK_DAMAGE HP; at 0 DestroyActor. No HP bar."""
    if world is None or pawn is None:
        return
    try:
        pl = pawn.get_actor_location()
    except Exception:
        return
    hit_any = False
    for actor in _list_live_enemy_actors(world):
        if actor is None or (not _uobj_alive(actor)):
            continue
        try:
            loc = actor.get_actor_location()
        except Exception:
            continue
        if _dist(pl, loc) > float(ATTACK_HIT_RANGE):
            continue
        st = _get_enemy_hp_state(actor)
        health = float(st["health"])
        maxh = float(st["max_health"])
        health = max(0.0, health - float(ATTACK_DAMAGE))
        _set_enemy_hp_state(actor, health, maxh)
        hit_any = True
        _log("T299 hit %s HP=%.0f/%.0f" % (_enemy_cache_key(actor), health, maxh))
        _print(world, "Hit -%d  HP %.0f" % (int(ATTACK_DAMAGE), health), (1.0, 0.6, 0.2, 1.0), 0.8)
        if health <= 0.0001:
            ok = _destroy_enemy_actor(actor)
            _print(world, "Skeleton died", (1.0, 0.4, 0.3, 1.0), 1.5)
            _log("T299 destroy ok=%s" % ok)
    if not hit_any:
        _log("T299 miss (no skeleton in range)")



def ensure_dungeon_pawn(world):
    """If Map_Dungeon1 PIE has PC but no pawn, spawn+possess KayKit."""
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
        _PREV_LMB[0] = False
        _LAST_HINT_KEY[0] = None
        if _LAST_WORLD_KEY[0] is not None:
            _reset_ui_after_travel("pie_world_none")
            _LAST_WORLD_KEY[0] = None
        elif _HEALTH_WIDGET[0] is not None or _GOLD_WIDGET[0] is not None:
            _clear_health_hud()
            try:
                _clear_gold_hud()
            except Exception:
                pass
        if _ENEMY_BARS and _LAST_WORLD_KEY[0] is None:
            # already cleared by reset, or leftover
            try:
                _clear_enemy_bars()
            except Exception:
                pass
        return
    # T278: OpenLevel keeps a world object but path/name changes (Hub <-> Dungeon1)
    wkey = _world_key(world)
    if wkey != _LAST_WORLD_KEY[0]:
        prev = _LAST_WORLD_KEY[0]
        _LAST_WORLD_KEY[0] = wkey
        if prev is not None:
            _reset_ui_after_travel("world_change %s -> %s" % (prev, wkey))
        else:
            # First bind after travel prep (LAST cleared) or cold start:
            # always drop caches so Hub and Map_Dungeon1 both re-create bars.
            _clear_health_hud()
            try:
                _clear_gold_hud()
            except Exception:
                pass
            _clear_enemy_bars()
            _DUNGEON_PAWN_TRIED[0] = False
            _VIEW_FIXED[0] = False
            _log("T278 bind world " + str(wkey))
    ensure_dungeon_pawn(world)
    _restore_attack_anim_if_due()
    _fix_view_once(world)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    if not pc:
        return

    down_e = _key_down(pc, "E")
    down_esc = _key_down(pc, "Escape")
    down_lmb = _key_down(pc, "LeftMouseButton")
    pressed_e = down_e and (not _PREV_E[0])
    pressed_esc = down_esc and (not _PREV_ESC[0])
    pressed_lmb = down_lmb and (not _PREV_LMB[0])
    _PREV_E[0] = down_e
    _PREV_ESC[0] = down_esc
    _PREV_LMB[0] = down_lmb

    pawn = None
    try:
        pawn = pc.get_controlled_pawn()
    except Exception:
        pawn = None

    # Screen HUD health bar (top-left). Safe: uses existing WBP + PB_Health.
    if pawn is not None:
        try:
            ensure_health_hud(world, pc, pawn)
        except Exception as e:
            _log("ensure_health_hud " + str(e))
    # T311_GOLD_HUD: Gold top-right (independent of pawn Health vars)
    try:
        ensure_gold_hud(world, pc, pawn)
    except Exception as e:
        _log("ensure_gold_hud " + str(e))
    # Enemy flat screen HP bars (ProjectWorldToScreen) above skeleton heads
    try:
        ensure_enemy_health_bars(world, pc, pawn)
    except Exception as e:
        _log("ensure_enemy_health_bars " + str(e))

    shop_key = None
    title = None
    gate = False
    hub_exit = False
    if pawn is not None and _OPEN_WIDGET[0] is None:
        shop_key, title, gate, hub_exit = scan_near(world, pawn.get_actor_location())
        if shop_key and title:
            _NEAR_SHOP[0] = (shop_key, title)
        else:
            _NEAR_SHOP[0] = None
        _NEAR_GATE[0] = gate
        _NEAR_EXIT[0] = hub_exit
        # Hint priority: dungeon exit > hub gate > shop
        if hub_exit and _world_is_dungeon(world):
            key = ("exit",)
        elif gate:
            key = ("gate",)
        elif shop_key and title:
            key = ("shop", shop_key)
        else:
            key = None
        if key is not None and key != _LAST_HINT_KEY[0]:
            if key[0] == "exit":
                _print(world, u"按 E 进入2层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "gate":
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
    # T299: process delayed hit from a previous LMB swing (simple timer)
    try:
        _process_pending_attack_hit(world, pawn)
    except Exception as e:
        _log("pending hit " + str(e))

    if pressed_lmb and pawn is not None:
        try:
            if try_attack(world, pawn):
                # wait ATTACK_DAMAGE_DELAY then distance-check + damage (once per swing)
                try:
                    _schedule_attack_hit(pawn)
                except Exception as e:
                    _log("schedule hit " + str(e))
        except Exception as e:
            _log("LMB attack " + str(e))
    if pressed_e:
        _log("E pressed -> handle_interact")
        try:
            handle_interact(world)
        except Exception as e:
            _log("E handle " + str(e))


def bootstrap():
    try:
        ensure_player_meta(None)
    except Exception as e:
        _log("ensure_player_meta " + str(e))

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
        _log("tick registered SPLIT_WBP_V15e_T313_GOLD_RIGHT gen=%s" % _MY_GEN[0])
    except Exception as e:
        _log("tick register fail " + str(e))
    _LAST_HINT_KEY[0] = None
    _PREV_E[0] = False
    _PREV_ESC[0] = False
    _PREV_LMB[0] = False
    _VIEW_FIXED[0] = False
    _LAST_WORLD_KEY[0] = None
    _DUNGEON_PAWN_TRIED[0] = False
    _clear_health_hud()
    try:
        _clear_gold_hud()
    except Exception:
        pass
    _clear_enemy_bars()
    _PENDING_ATTACK_HIT[0] = None
    try:
        _ENEMY_HP_CACHE.clear()
    except Exception:
        pass
    _log("runtime ready SPLIT_WBP_V15e_T313_GOLD_RIGHT")


bootstrap()
