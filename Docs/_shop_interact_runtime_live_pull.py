# -*- coding: utf-8 -*-
# Shop / gate / dungeon-exit / LMB attack SPLIT_WBP_V15e_T231 for DungeonEscape UE4.27 PIE.
# Priority: near GateTrigger/HubGate -> OpenLevel Map_Dungeon1 FIRST; else shop WBP.
# Map_Dungeon1: near DungeonExit -> OpenLevel Map_Hub; LMB plays 1H Chop.
# V15e: Prefer DefaultSlot dynamic montage WITHOUT clearing AnimBP (upper-body overlay once
# ABP wires Slot+LayeredBlendPerBone on spine). Fall back to single-node only if slot fails.
# Shops use smaller SHOP_RANGE so they do not overlap the red gate.
# Key detect: UE is_input_key_down + was_just_pressed + Win GetAsyncKeyState.
# V15e_HP: screen HUD WBP_PlayerHealthBar top-left; sync Health/MaxHealth each tick.
# T275: enemy HP = WidgetComponent Screen billboard above skull; NEVER AddToViewport.
# T277: never RemoveFromParent on WidgetComponent-owned enemy HP widgets (no UMG parent).
# Force DrawAtDesiredSize=False so HUD-layout WBP cannot pin to screen corner.
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
HEALTH_WBP_PATHS = (
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
_ENEMY_BAR_Z = 110.0
_ENEMY_DRAW = (160.0, 18.0)
_ENEMY_CLS_PATHS = (
    "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton.BP_Enemy_Skeleton_C",
)
_ENEMY_WC_NAME = "EnemyHealthBar"
_ENEMY_PURGE_ACC = [0.0]
_NEAR_SHOP = [None]  # ("Weapon"|"Armor"|"Health", title) or None
_NEAR_GATE = [False]
_NEAR_EXIT = [False]
_PREV_E = [False]
_PREV_ESC = [False]
_PREV_LMB = [False]
_LAST_ATTACK_T = [0.0]
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
    Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs -> Map_Hub.
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
HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"


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


def enter_dungeon(world_ctx):
    """OpenLevel to Map_Dungeon1 (fallback Map_Dungeon) when E near red gate."""
    if world_ctx is None:
        return False
    level = resolve_dungeon_level()
    close_shop(world_ctx)
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


def return_to_hub(world_ctx):
    """OpenLevel to Map_Hub when E near dungeon stairs exit."""
    if world_ctx is None:
        return False
    close_shop(world_ctx)
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
        _log("E near dungeon exit -> return_to_hub")
        return return_to_hub(world)
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


def _clear_health_hud():
    w = _HEALTH_WIDGET[0]
    _HEALTH_WIDGET[0] = None
    _HEALTH_BAR[0] = None
    _HEALTH_TXT[0] = None
    if w is None:
        return
    try:
        w.remove_from_parent()
    except Exception:
        try:
            w.remove_from_viewport()
        except Exception:
            pass


def ensure_health_hud(world, pc, pawn):
    """Screen-space HUD: ProgressBar fixed top-left. Creates once, updates percent."""
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
    """Force ProgressBar to fill WidgetComponent DrawSize (HUD canvas offsets would clip / pin wrong)."""
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
            slot.set_anchors(unreal.Anchors(0.0, 0.0, 1.0, 1.0))
        except Exception:
            pass
        try:
            slot.set_offsets(unreal.Margin(0.0, 0.0, 0.0, 0.0))
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
        # Shrink desired size so Screen-space WC cannot expand to full HUD canvas
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
    """RemoveFromParent/Viewport ONLY when widget is actually in the game viewport.
    WidgetComponent-owned UserWidgets have no UMG parent; calling RemoveFromParent
    floods Message Log on Hub<->Dungeon transitions.
    """
    if w is None:
        return False
    if not _widget_in_viewport(w):
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


def _release_enemy_widget(st):
    """Detach enemy HP from WidgetComponent without RemoveFromParent spam."""
    if not st:
        return
    wc = st.get("wc")
    if wc is not None:
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
    # Only if an older patch parked it in the viewport
    _safe_remove_viewport_only(st.get("widget"))


def _purge_enemy_viewport_widgets():
    """Yank leftover enemy HP widgets that were wrongly AddToViewport'd by older runtimes.
    Skip WidgetComponent-owned instances (not in viewport / no UMG parent).
    """
    try:
        wcls, _ = _load_enemy_health_wbp_class()
    except Exception:
        wcls = None
    removed = 0
    # Never touch the player HUD widget
    player_hud = _HEALTH_WIDGET[0]
    # Also skip widgets currently owned by live enemy bars
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
                if not is_enemy:
                    continue
                # Critical: only remove widgets actually in the viewport
                if not _widget_in_viewport(o):
                    continue
                if _safe_remove_viewport_only(o):
                    removed += 1
            except Exception:
                continue
    except Exception as e:
        _log("purge enemy viewport " + str(e))
        return
    if removed:
        _log("purged %d enemy HP widgets from viewport" % removed)


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
        except Exception:
            c = None
        if c is not None:
            return c
    return None


def _set_wc_screen_space(wc):
    # UE4: EWidgetSpace World=0, Screen=1 — never write 0 here.
    for attempt in (
        lambda: wc.set_widget_space(unreal.WidgetSpace.SCREEN),
        lambda: wc.set_editor_property("space", unreal.WidgetSpace.SCREEN),
        lambda: wc.set_editor_property("space", 1),
    ):
        try:
            attempt()
            return True
        except Exception:
            continue
    return False



def _create_enemy_user_widget(world, pc, wcls):
    """Create enemy HP UserWidget WITHOUT adding it to the viewport."""
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
    # Do NOT RemoveFromParent here — fresh widgets and WC-owned ones have no UMG parent.
    _safe_remove_viewport_only(widget)
    return widget


def _configure_widget_component(wc, wcls=None, world=None, pc=None, existing_widget=None):
    """UE4.27: Screen-space billboard via set_widget (no set_widget_class)."""
    if wc is None:
        return None, None
    try:
        wc.set_relative_location(unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z)), False, False)
    except Exception:
        try:
            wc.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z)))
        except Exception:
            pass
    try:
        wc.set_draw_size(unreal.Vector2D(float(_ENEMY_DRAW[0]), float(_ENEMY_DRAW[1])))
    except Exception:
        try:
            wc.set_editor_property("draw_size", unreal.IntPoint(int(_ENEMY_DRAW[0]), int(_ENEMY_DRAW[1])))
        except Exception:
            pass
    try:
        wc.set_draw_at_desired_size(False)
    except Exception:
        try:
            wc.set_editor_property("draw_at_desired_size", False)
        except Exception:
            pass
    if not _set_wc_screen_space(wc):
        try:
            wc.set_widget_space(unreal.WidgetSpace.WORLD)
        except Exception:
            pass
    try:
        wc.set_pivot(unreal.Vector2D(0.5, 1.0))
    except Exception:
        try:
            wc.set_editor_property("pivot", unreal.Vector2D(0.5, 1.0))
        except Exception:
            pass
    try:
        wc.set_two_sided(True)
    except Exception:
        pass
    try:
        wc.set_visibility(True, True)
    except Exception:
        try:
            wc.set_hidden_in_game(False)
        except Exception:
            pass
    try:
        wc.set_editor_property("collision_enabled", unreal.CollisionEnabled.NO_COLLISION)
    except Exception:
        pass
    try:
        wc.set_editor_property("receive_hardware_input", False)
    except Exception:
        pass

    widget = existing_widget
    if widget is None:
        try:
            widget = wc.get_user_widget_object()
        except Exception:
            widget = None
    if widget is None:
        try:
            widget = wc.get_widget()
        except Exception:
            widget = None
    if widget is None and wcls is not None:
        widget = _create_enemy_user_widget(world, pc, wcls)

    pb = None
    if widget is not None:
        # WC-owned widgets must not call RemoveFromParent
        _safe_remove_viewport_only(widget)
        pb = _find_named_widget(widget, "PB_Health")
        if pb is None:
            # Last resort: ProgressBar whose Outer chain is THIS enemy widget only
            try:
                for o in unreal.ObjectIterator(unreal.ProgressBar):
                    try:
                        if _outer_chain_contains(o, widget):
                            pb = o
                            break
                    except Exception:
                        continue
            except Exception:
                pass
        # Refuse cross-binding to player HUD ProgressBar
        if pb is not None:
            try:
                pp = pb.get_path_name()
                if ("PlayerHealth" in pp) and ("EnemyHealth" not in pp):
                    _log("enemy pb refused player HUD bind: " + pp)
                    pb = None
            except Exception:
                pass
        _fit_enemy_bar_layout(widget, pb)
        # UE4.27 WidgetComponent API: set_widget (NOT set_widget_class)
        try:
            wc.set_widget(widget)
        except Exception as e:
            _log("enemy wc set_widget " + str(e))
            try:
                wc.set_editor_property("widget", widget)
            except Exception as e2:
                _log("enemy wc widget prop " + str(e2))
                return None, None
    try:
        wc.set_active(True, True)
    except Exception:
        pass
    try:
        wc.request_redraw()
    except Exception:
        pass
    return widget, pb



def _find_enemy_wc(actor):
    try:
        for c in actor.get_components_by_class(unreal.WidgetComponent):
            try:
                nm = c.get_name() or ""
            except Exception:
                nm = ""
            if nm.startswith(_ENEMY_WC_NAME) or "EnemyHealth" in nm:
                return c
    except Exception:
        pass
    return None


def _attach_widget_component(actor, wcls, world=None, pc=None):
    """Create/register Screen-space WidgetComponent billboard above the enemy head."""
    wc = _find_enemy_wc(actor)
    root = _enemy_root_component(actor)
    if wc is None:
        try:
            xf = unreal.Transform(
                unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z)),
                unreal.Rotator(0.0, 0.0, 0.0),
                unreal.Vector(1.0, 1.0, 1.0),
            )
        except Exception:
            xf = unreal.Transform()
            try:
                xf.translation = unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z))
            except Exception:
                pass
        try:
            wc = actor.add_component_by_class(unreal.WidgetComponent, False, xf, False)
            _log("enemy wc add_component_by_class -> " + str(wc))
        except Exception as e:
            _log("enemy wc add_component_by_class " + str(e))
            wc = None
        if wc is None:
            try:
                wc = unreal.new_object(unreal.WidgetComponent, actor, _ENEMY_WC_NAME)
                _log("enemy wc new_object -> " + str(wc))
            except Exception as e:
                _log("enemy wc new_object " + str(e))
                return None, None, None
            if root is not None:
                try:
                    wc.attach_to_component(
                        root,
                        unreal.AttachmentTransformRules.KEEP_RELATIVE_TRANSFORM,
                        "",
                    )
                except Exception as e:
                    _log("enemy wc attach " + str(e))
                    try:
                        wc.attach_to_component(
                            root,
                            "",
                            unreal.AttachmentRule.KEEP_RELATIVE,
                            unreal.AttachmentRule.KEEP_RELATIVE,
                            unreal.AttachmentRule.KEEP_RELATIVE,
                            False,
                        )
                    except Exception as e2:
                        _log("enemy wc attach2 " + str(e2))
            try:
                wc.register_component()
            except Exception as e:
                _log("enemy wc register " + str(e))
            try:
                actor.add_instance_component(wc)
            except Exception:
                pass
        # If add_component_by_class worked, still ensure attach to mesh/capsule
        elif root is not None:
            try:
                parent = None
                try:
                    parent = wc.get_attach_parent()
                except Exception:
                    parent = None
                if parent is None:
                    try:
                        wc.attach_to_component(
                            root,
                            unreal.AttachmentTransformRules.KEEP_RELATIVE_TRANSFORM,
                            "",
                        )
                    except Exception:
                        pass
            except Exception:
                pass

    owned, pb = _configure_widget_component(wc, wcls, world=world, pc=pc)
    return wc, owned, pb


def _clear_enemy_bars():
    for key, st in list(_ENEMY_BARS.items()):
        try:
            _release_enemy_widget(st)
        except Exception:
            pass
    _ENEMY_BARS.clear()
    _purge_enemy_viewport_widgets()


def _sync_enemy_wc_world_pos(actor, wc):
    """Keep WC on skull: relative when attached, world location if attach missing."""
    if actor is None or wc is None:
        return
    attached = False
    try:
        attached = wc.get_attach_parent() is not None
    except Exception:
        attached = False
    try:
        wc.set_relative_location(unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z)), False, False)
    except Exception:
        try:
            wc.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, float(_ENEMY_BAR_Z)))
        except Exception:
            pass
    if attached:
        return
    try:
        loc = actor.get_actor_location()
        target = unreal.Vector(float(loc.x), float(loc.y), float(loc.z) + float(_ENEMY_BAR_Z))
        wc.set_world_location(target, False, False)
    except Exception:
        pass


def ensure_enemy_health_bars(world, pc, pawn=None):
    """WidgetComponent HP bars above BP_Enemy_Skeleton heads. Never AddToViewport."""
    if world is None:
        return
    # Kill leftover screen-HUD enemy bars from older patches (throttled)
    try:
        _ENEMY_PURGE_ACC[0] += 0.016
        if _ENEMY_PURGE_ACC[0] >= 1.0 or not _ENEMY_BARS:
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
                enemies.append(a)
        except Exception as e:
            _log("enemy list class " + str(e))
    if not enemies:
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
                if _is_enemy_skeleton(a):
                    enemies.append(a)
        except Exception as e:
            _log("enemy list scan " + str(e))

    wcls, wpath = _load_enemy_health_wbp_class()
    live = set()
    for actor in enemies:
        if actor is None:
            continue
        key = _enemy_key(actor)
        live.add(key)
        st = _ENEMY_BARS.get(key)
        if st is not None:
            st["actor"] = actor
        if st is None:
            st = {
                "actor": actor,
                "health": _ENEMY_HP_DEFAULT,
                "max_health": _ENEMY_HP_DEFAULT,
                "wc": None,
                "widget": None,
                "pb": None,
            }
            _read_enemy_hp(actor, st)
            _write_enemy_hp(actor, st["health"], st["max_health"])
            if wcls is None:
                _log("enemy bar: no WBP class for " + key)
                continue
            wc, owned, pb = _attach_widget_component(actor, wcls, world=world, pc=pc)
            st["wc"] = wc
            st["widget"] = owned
            st["pb"] = pb
            if wc is None:
                _log("enemy WidgetComponent FAILED for " + key + " (no viewport fallback)")
            else:
                _log("enemy bar OK %s wbp=%s wc=%s pb=%s" % (key, wpath, wc, pb))
            _ENEMY_BARS[key] = st

        # Re-bind pb/widget if component recreated its user widget
        wc = st.get("wc")
        if wc is not None and (st.get("pb") is None or st.get("widget") is None):
            try:
                owned = wc.get_user_widget_object()
            except Exception:
                owned = None
            if owned is not None:
                st["widget"] = owned
                # Never RemoveFromParent on WC get_user_widget_object()
                st["pb"] = _find_named_widget(owned, "PB_Health")
                _fit_enemy_bar_layout(st.get("widget"), st.get("pb"))

        # Sync HP -> bar
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

        if wc is not None:
            _sync_enemy_wc_world_pos(actor, wc)
            try:
                wc.set_draw_at_desired_size(False)
            except Exception:
                try:
                    wc.set_editor_property("draw_at_desired_size", False)
                except Exception:
                    pass
            try:
                wc.set_visibility(True, False)
            except Exception:
                pass
            # If owned widget somehow entered viewport, yank it back onto the component
            widget = st.get("widget")
            if widget is not None:
                try:
                    if _safe_remove_viewport_only(widget):
                        try:
                            wc.set_widget(widget)
                        except Exception:
                            pass
                        _log("yanked enemy widget back from viewport " + key)
                except Exception:
                    pass

    for key in list(_ENEMY_BARS.keys()):
        if key not in live:
            st = _ENEMY_BARS.pop(key, None)
            if not st:
                continue
            try:
                _release_enemy_widget(st)
            except Exception:
                pass


def _damage_enemies_near_attack(world, pawn):
    """When player chops, lightly damage nearby skeletons so the bar visibly updates."""
    if world is None or pawn is None:
        return
    try:
        pl = pawn.get_actor_location()
    except Exception:
        return
    hit_any = False
    for key, st in list(_ENEMY_BARS.items()):
        actor = st.get("actor")
        if actor is None:
            continue
        try:
            loc = actor.get_actor_location()
        except Exception:
            continue
        if _dist(pl, loc) > 220.0:
            continue
        health, maxh = _read_enemy_hp(actor, st)
        health = max(0.0, health - 10.0)
        st["health"] = health
        _write_enemy_hp(actor, health, maxh)
        hit_any = True
        pct = 0.0 if maxh <= 0 else health / maxh
        pb = st.get("pb")
        if pb is not None:
            try:
                pb.set_percent(pct)
            except Exception:
                pass
        if health <= 0.0001:
            _print(world, u"骷髅倒下了", (1.0, 0.5, 0.4, 1.0), 1.5)
    if hit_any:
        _print(world, u"命中骷髅！", (1.0, 0.6, 0.2, 1.0), 0.6)


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
        if _HEALTH_WIDGET[0] is not None:
            _clear_health_hud()
        if _ENEMY_BARS:
            _clear_enemy_bars()
        return
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
    # Enemy world/screen HP bars above skeleton heads
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
                _print(world, u"按 E 返回主城", (0.4, 0.9, 1.0, 1.0), 2.0)
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
    if pressed_lmb and pawn is not None:
        try:
            if try_attack(world, pawn):
                try:
                    _damage_enemies_near_attack(world, pawn)
                except Exception as e:
                    _log("enemy dmg " + str(e))
        except Exception as e:
            _log("LMB attack " + str(e))
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
        _log("tick registered SPLIT_WBP_V15e_T231_HP gen=%s" % _MY_GEN[0])
    except Exception as e:
        _log("tick register fail " + str(e))
    _LAST_HINT_KEY[0] = None
    _PREV_E[0] = False
    _PREV_ESC[0] = False
    _PREV_LMB[0] = False
    _VIEW_FIXED[0] = False
    _clear_health_hud()
    _clear_enemy_bars()
    _log("runtime ready SPLIT_WBP_V15e_T277_NO_RFP_WC")


bootstrap()
