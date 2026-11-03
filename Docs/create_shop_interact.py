# -*- coding: utf-8 -*-
"""Shop interact v5: WBP_Shop + native TriggerBox triggers (savable) + Python tick runtime."""
from __future__ import print_function
import unreal
import traceback
import sys

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
SHOP_DIR = "/Game/UI/Shop"
CORE_DIR = "/Game/Core/Interact"
WBP_PATH = SHOP_DIR + "/WBP_Shop"
MENU_WBP = "/Game/UI/Menus/WBP_MainMenu"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_shop_interact.log"
SETUP_MD = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\SHOP_SETUP.md"
PY_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"

SHOP_TITLES = {
    "HubShop_Weapon": "\u6b66\u5668\u5e97",
    "HubShop_Armor": "\u9632\u5177\u5e97",
    "HubShop_Health": "\u56de\u8840\u5e97",
}
SHOP_TYPES = {
    "HubShop_Weapon": "Weapon",
    "HubShop_Armor": "Armor",
    "HubShop_Health": "Health",
}

_log = []


def log(m):
    s = str(m)
    _log.append(s)
    try:
        unreal.log("SHOP: " + s)
    except Exception:
        print("SHOP: " + s)


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


def create_wbp_shop():
    ensure_dir(SHOP_DIR)
    for p in (
        WBP_PATH,
        SHOP_DIR + "/WBP_ShopProbe",
        SHOP_DIR + "/WBP_ShopProbeCmd",
        SHOP_DIR + "/WBP_EmptyProbe",
        SHOP_DIR + "/WBP_ShopFromMenu",
        SHOP_DIR + "/WBP_ShopFromMenu2",
        SHOP_DIR + "/WBP_Shop_Weapon",
        SHOP_DIR + "/WBP_Shop_Armor",
        SHOP_DIR + "/WBP_Shop_Health",
    ):
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            try:
                unreal.EditorAssetLibrary.delete_asset(p)
                log("deleted " + p)
            except Exception as e:
                log("del " + p + " " + str(e))

    if not unreal.EditorAssetLibrary.does_asset_exist(MENU_WBP):
        raise RuntimeError("WBP_MainMenu missing")

    # Keep existing WBP_Shop if present and healthy? Always recreate clean from MainMenu.
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    src = unreal.EditorAssetLibrary.load_asset(MENU_WBP)
    wbp = tools.duplicate_asset("WBP_Shop", SHOP_DIR, src)
    if not wbp:
        raise RuntimeError("duplicate WBP_Shop failed")
    save(wbp)
    wbp = unreal.EditorAssetLibrary.load_asset(WBP_PATH)
    log("duplicated WBP_Shop")

    renames = {
        "Txt_Title": "\u5546\u5e97",
        "Txt_Sub": "\u6682\u65e0\u5546\u54c1",
        "Txt_Hint": "E / Esc \u5173\u95ed",
        "Btn_Start_Txt": "\u5173\u95ed",
        "Btn_Quit_Txt": "",
    }
    n_txt = 0
    for o in iter_under(WBP_PATH):
        try:
            name = o.get_name()
            cn = o.get_class().get_name()
            if cn == "TextBlock" and name in renames:
                o.set_editor_property("text", unreal.Text(renames[name]))
                n_txt += 1
                log("text " + name)
            if name == "Btn_Quit" and "Button" in cn:
                try:
                    o.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
                    log("collapsed Btn_Quit")
                except Exception as e:
                    log("collapse " + str(e))
        except Exception:
            pass
    log("retargeted texts=%d" % n_txt)

    # Break old menu K2 links so Start does not OpenLevel
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
    log("WBP_Shop ready")
    return wbp


def create_stub_bp():
    ensure_dir(CORE_DIR)
    for p in (
        CORE_DIR + "/BP_ShopProbe",
        CORE_DIR + "/BP_GateInteract",
        CORE_DIR + "/BP_ShopInteract_Weapon",
        CORE_DIR + "/BP_ShopInteract_Armor",
        CORE_DIR + "/BP_ShopInteract_Health",
    ):
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            try:
                unreal.EditorAssetLibrary.delete_asset(p)
                log("deleted " + p)
            except Exception:
                pass
    full = CORE_DIR + "/BP_ShopInteract"
    if not unreal.EditorAssetLibrary.does_asset_exist(full):
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", unreal.TriggerBox.static_class())
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "BP_ShopInteract", CORE_DIR, None, factory
        )
        save(bp)
        log("created stub BP_ShopInteract")
    else:
        log("reuse stub BP_ShopInteract")
    return unreal.EditorAssetLibrary.load_asset(full)


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
    for prop, val in (("generate_overlap_events", True),):
        try:
            box.set_editor_property(prop, val)
        except Exception:
            pass
    try:
        actor.set_actor_hidden_in_game(True)
    except Exception:
        pass
    try:
        # keep visible in editor wireframe optionally
        actor.set_actor_scale3d(unreal.Vector(1, 1, 1))
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


def destroy_old_triggers():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label() or ""
        cn = a.get_class().get_name()
        if (
            lab.startswith("ShopTrigger_")
            or lab.startswith("GateTrigger_")
            or lab.startswith("ShopHelper")
            or cn in ("ShopInteractVolume", "GateInteractVolume", "ShopHelper")
        ):
            try:
                unreal.EditorLevelLibrary.destroy_actor(a)
                log("removed " + lab + " (" + cn + ")")
            except Exception as e:
                log("remove fail " + lab + " " + str(e))


def set_tags(actor, tags):
    try:
        actor.set_editor_property("tags", tags)
    except Exception as e:
        log("tags fail " + str(e))


def spawn_triggers():
    destroy_old_triggers()
    shops = {}
    gate = None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab in SHOP_TITLES:
            shops[lab] = a
        if lab == "HubGate_DungeonEntrance":
            gate = a
    log("found shops=" + str(list(shops.keys())) + " gate=" + (gate.get_actor_label() if gate else "None"))
    spawned = []
    for lab, title in SHOP_TITLES.items():
        src = shops.get(lab)
        if not src:
            log("MISSING " + lab)
            continue
        loc = src.get_actor_location()
        tloc = unreal.Vector(loc.x, loc.y, loc.z + 100.0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.TriggerBox.static_class(), tloc, unreal.Rotator(0, 0, 0)
        )
        if not actor:
            log("spawn fail " + lab)
            continue
        tlabel = "ShopTrigger_" + SHOP_TYPES[lab]
        actor.set_actor_label(tlabel)
        try:
            actor.set_folder_path("Interact")
        except Exception:
            pass
        set_tags(actor, ["ShopInteract", "ShopTitle:" + title, "ShopKind:" + SHOP_TYPES[lab]])
        configure_native_box(actor, (150.0, 150.0, 150.0))
        spawned.append(tlabel)
        log("spawned native %s @ %s" % (tlabel, lab))

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
            log("spawned native GateTrigger_DungeonEntrance")
    return spawned


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


def write_setup_md(spawned, verify_ok):
    lines = [
        "# Shop Interact Setup",
        "",
        "## Assets",
        "- `/Game/UI/Shop/WBP_Shop`",
        "- `/Game/Core/Interact/BP_ShopInteract` (stub)",
        "- `Content/Python/shop_interact_runtime.py` (PIE tick; E near tagged TriggerBox)",
        "- `Content/Python/init_unreal.py`",
        "",
        "## Spawned native TriggerBox on Map_Hub",
    ]
    for s in spawned:
        lines.append("- " + s)
    lines.extend([
        "",
        "## Buildings untouched: **" + str(verify_ok) + "**",
        "",
        "## How to test",
        "1. Restart editor once (loads init_unreal.py) OR open Map_Hub after this Cmd",
        "2. PIE (Alt+P)",
        "3. Walk to a shop cube, press **E**",
        "4. Click **\u5173\u95ed** or press E/Esc to close",
        "5. At gate, E shows \u5730\u4e0b\u57ce\u5165\u53e3\uff08\u5f85\u63a5\u5165\uff09",
        "",
    ])
    try:
        with open(SETUP_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        log("wrote SHOP_SETUP.md")
    except Exception as e:
        log("setup md " + str(e))


def ensure_runtime_import():
    if PY_DIR not in sys.path:
        sys.path.insert(0, PY_DIR)
    if "shop_interact_runtime" in sys.modules:
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as sir
    log("runtime imported tick=" + str(sir._TICK_HANDLE[0]))
    return sir


def main():
    log("=== shop interact v5 START ===")
    ensure_dir(SHOP_DIR)
    ensure_dir(CORE_DIR)

    create_wbp_shop()
    create_stub_bp()
    ensure_runtime_import()

    try:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("loaded Map_Hub")
    except Exception as e:
        log("load_map " + str(e))
        raise

    before = snapshot_buildings()
    log("snapshot before n=%d" % len(before))
    spawned = spawn_triggers()
    after = snapshot_buildings()
    ok = verify(before, after)

    try:
        unreal.EditorLevelLibrary.save_current_level()
        log("level saved")
    except Exception as e:
        log("save level " + str(e))
        raise
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        log("dirty saved")
    except Exception as e:
        log("save dirty " + str(e))
    for d in (SHOP_DIR, CORE_DIR):
        try:
            unreal.EditorAssetLibrary.save_directory(d)
        except Exception as e:
            log("save dir " + str(e))

    write_setup_md(spawned, ok)
    log("spawned=" + str(spawned))
    log("=== shop interact v5 DONE ===")
    flush()


try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc())
    flush()
    raise
