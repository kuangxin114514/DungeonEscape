# -*- coding: utf-8 -*-
"""Verify/repair Map_Hub shop+gate E-interact. Never move Hub buildings."""
from __future__ import print_function
import unreal
import traceback
import sys

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
SHOP_DIR = "/Game/UI/Shop"
CORE_DIR = "/Game/Core/Interact"
WBP_PATH = SHOP_DIR + "/WBP_Shop"
MENU_WBP = "/Game/UI/Menus/WBP_MainMenu"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_shop_verify.log"
SETUP_MD = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\SHOP_SETUP.md"
PY_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"

SHOP_TITLES = {
    "HubShop_Weapon": "武器店",
    "HubShop_Armor": "防具店",
    "HubShop_Health": "回血店",
}
SHOP_TYPES = {
    "HubShop_Weapon": "Weapon",
    "HubShop_Armor": "Armor",
    "HubShop_Health": "Health",
}
EXPECTED_TRIGGERS = [
    "ShopTrigger_Weapon",
    "ShopTrigger_Armor",
    "ShopTrigger_Health",
    "GateTrigger_DungeonEntrance",
]

_log = []

def log(m):
    s = str(m)
    _log.append(s)
    try:
        unreal.log("SHOPV: " + s)
    except Exception:
        print("SHOPV: " + s)

def flush():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(_log) + "\n")
    except Exception as e:
        print("flush", e)

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def save(a):
    if a:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e:
            log("save " + str(e))

def iter_under(asset_path):
    for o in unreal.ObjectIterator():
        try:
            if asset_path in o.get_path_name():
                yield o
        except Exception:
            pass

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
                round(rot.roll, 2), round(rot.pitch, 2), round(rot.yaw, 2),
                round(scl.x, 4), round(scl.y, 4), round(scl.z, 4),
            )
    return snap

def verify(before, after):
    ok = True
    for lab, b in before.items():
        a = after.get(lab)
        if a is None:
            log("VERIFY missing " + lab)
            ok = False
        elif a != b:
            log("VERIFY changed %s %s -> %s" % (lab, b, a))
            ok = False
    log("VERIFY buildings_unchanged=%s count=%d" % (ok, len(before)))
    return ok

def ensure_wbp_shop():
    ensure_dir(SHOP_DIR)
    if unreal.EditorAssetLibrary.does_asset_exist(WBP_PATH):
        log("reuse WBP_Shop")
        return unreal.EditorAssetLibrary.load_asset(WBP_PATH)
    if not unreal.EditorAssetLibrary.does_asset_exist(MENU_WBP):
        raise RuntimeError("WBP_MainMenu missing and no WBP_Shop")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    src = unreal.EditorAssetLibrary.load_asset(MENU_WBP)
    wbp = tools.duplicate_asset("WBP_Shop", SHOP_DIR, src)
    if not wbp:
        raise RuntimeError("duplicate WBP_Shop failed")
    save(wbp)
    # break menu OpenLevel links
    for o in iter_under(WBP_PATH):
        try:
            if not o.get_class().get_name().startswith("K2Node"):
                continue
            try:
                pins = list(o.get_editor_property("pins"))
            except Exception:
                pins = []
            for p in pins:
                try:
                    p.break_all_pin_links()
                except Exception:
                    try:
                        p.break_all_pin_links(True)
                    except Exception:
                        pass
        except Exception:
            pass
    save(wbp)
    log("created WBP_Shop from MainMenu")
    return unreal.EditorAssetLibrary.load_asset(WBP_PATH)

def ensure_stub_bp():
    ensure_dir(CORE_DIR)
    full = CORE_DIR + "/BP_ShopInteract"
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("reuse BP_ShopInteract")
        return unreal.EditorAssetLibrary.load_asset(full)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", unreal.TriggerBox.static_class())
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "BP_ShopInteract", CORE_DIR, None, factory
    )
    save(bp)
    log("created BP_ShopInteract stub")
    return bp

def configure_native_box(actor, extent=(150.0, 150.0, 150.0)):
    box = None
    try:
        box = actor.get_component_by_class(unreal.BoxComponent)
    except Exception:
        box = None
    if not box:
        try:
            box = actor.root_component
        except Exception:
            box = None
    if not box:
        log("no box on " + actor.get_actor_label())
        return
    try:
        box.set_box_extent(unreal.Vector(extent[0], extent[1], extent[2]), True)
    except Exception as e:
        log("extent " + str(e))
    try:
        box.set_collision_profile_name("OverlapAllDynamic")
    except Exception as e:
        log("profile " + str(e))
    try:
        box.set_editor_property("generate_overlap_events", True)
    except Exception:
        pass
    try:
        actor.set_actor_hidden_in_game(True)
    except Exception:
        pass

def set_tags(actor, tags):
    try:
        actor.set_editor_property("tags", tags)
    except Exception as e:
        log("tags fail " + str(e))

def find_actors_by_label():
    by_lab = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        by_lab[lab] = a
    return by_lab

def ensure_triggers():
    by_lab = find_actors_by_label()
    shops = {k: by_lab[k] for k in SHOP_TITLES if k in by_lab}
    gate = by_lab.get("HubGate_DungeonEntrance")
    log("found shops=" + str(list(shops.keys())) + " gate=" + (gate.get_actor_label() if gate else "None"))

    existing = []
    missing = []
    for t in EXPECTED_TRIGGERS:
        if t in by_lab:
            existing.append(t)
            # refresh tags/extent on existing
            actor = by_lab[t]
            if t.startswith("ShopTrigger_"):
                kind = t.replace("ShopTrigger_", "")
                title = None
                for lab, k in SHOP_TYPES.items():
                    if k == kind:
                        title = SHOP_TITLES[lab]
                        break
                set_tags(actor, ["ShopInteract", "ShopTitle:" + (title or "商店"), "ShopKind:" + kind])
                configure_native_box(actor, (150.0, 150.0, 150.0))
            else:
                set_tags(actor, ["GateInteract"])
                configure_native_box(actor, (180.0, 180.0, 160.0))
            log("refreshed " + t)
        else:
            missing.append(t)
    log("existing=" + str(existing) + " missing=" + str(missing))

    spawned = list(existing)
    for lab, title in SHOP_TITLES.items():
        tlabel = "ShopTrigger_" + SHOP_TYPES[lab]
        if tlabel not in missing:
            continue
        src = shops.get(lab)
        if not src:
            log("MISSING shop actor " + lab)
            continue
        loc = src.get_actor_location()
        tloc = unreal.Vector(loc.x, loc.y, loc.z + 100.0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.TriggerBox.static_class(), tloc, unreal.Rotator(0, 0, 0)
        )
        if not actor:
            log("spawn fail " + tlabel)
            continue
        actor.set_actor_label(tlabel)
        try:
            actor.set_folder_path("Interact")
        except Exception:
            pass
        set_tags(actor, ["ShopInteract", "ShopTitle:" + title, "ShopKind:" + SHOP_TYPES[lab]])
        configure_native_box(actor, (150.0, 150.0, 150.0))
        spawned.append(tlabel)
        log("spawned " + tlabel)

    if "GateTrigger_DungeonEntrance" in missing:
        if gate:
            gloc = gate.get_actor_location()
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.TriggerBox.static_class(),
                unreal.Vector(gloc.x, gloc.y, gloc.z + 100.0),
                unreal.Rotator(0, 0, 0),
            )
            if actor:
                actor.set_actor_label("GateTrigger_DungeonEntrance")
                try:
                    actor.set_folder_path("Interact")
                except Exception:
                    pass
                set_tags(actor, ["GateInteract"])
                configure_native_box(actor, (180.0, 180.0, 160.0))
                spawned.append("GateTrigger_DungeonEntrance")
                log("spawned GateTrigger_DungeonEntrance")
        else:
            log("MISSING HubGate_DungeonEntrance")
    return spawned

def ensure_runtime():
    if PY_DIR not in sys.path:
        sys.path.insert(0, PY_DIR)
    if "shop_interact_runtime" in sys.modules:
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as sir
    log("runtime tick=" + str(sir._TICK_HANDLE[0]))
    return sir

def write_setup(spawned, verify_ok):
    lines = [
        "# Shop Interact Setup",
        "",
        "## Assets",
        "- `/Game/UI/Shop/WBP_Shop` (empty shell)",
        "- `/Game/Core/Interact/BP_ShopInteract` (stub)",
        "- `Content/Python/shop_interact_runtime.py` (PIE: near TriggerBox + press E)",
        "- `Content/Python/init_unreal.py`",
        "",
        "## Actors on Map_Hub (Interact folder)",
    ]
    for s in spawned:
        lines.append("- `" + s + "`")
    lines.extend([
        "",
        "## Anchor actors (untouched)",
        "- `HubShop_Weapon` / `HubShop_Armor` / `HubShop_Health`",
        "- `HubGate_DungeonEntrance`",
        "",
        "## Buildings untouched: **" + str(verify_ok) + "**",
        "",
        "## How to test",
        "1. Open `Map_Hub`, PIE (Alt+P)",
        "2. Walk near a shop cube, press **E** → empty shop WBP (title = 武器店/防具店/回血店)",
        "3. Press **E** or **Esc** or click 关闭 to close",
        "4. Walk to dungeon gate, press **E** → on-screen: 地下城入口（待接入）",
        "",
        "## Note",
        "Only interaction + empty shell. Full shop UI is for you to build next.",
        "",
    ])
    try:
        with open(SETUP_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log("wrote SHOP_SETUP.md")
    except Exception as e:
        log("setup md " + str(e))

def main():
    log("=== shop verify/repair START ===")
    ensure_wbp_shop()
    ensure_stub_bp()
    ensure_runtime()

    # Prefer current level if already Map_Hub; else load
    try:
        cur = unreal.EditorLevelLibrary.get_editor_world()
        cur_name = cur.get_name() if cur else ""
        log("current world=" + str(cur_name))
    except Exception as e:
        log("cur world " + str(e))
        cur_name = ""
    if "Map_Hub" not in str(cur_name):
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("loaded Map_Hub")
    else:
        log("already on Map_Hub")

    before = snapshot_buildings()
    log("snapshot before n=%d" % len(before))
    spawned = ensure_triggers()
    after = snapshot_buildings()
    ok = verify(before, after)

    try:
        unreal.EditorLevelLibrary.save_current_level()
        log("level saved")
    except Exception as e:
        log("save level " + str(e))
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("dirty saved")
    except Exception as e:
        log("save dirty " + str(e))

    write_setup(spawned, ok)
    log("final_triggers=" + str(spawned))
    log("=== shop verify/repair DONE ===")
    flush()

try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc())
    flush()
    raise
