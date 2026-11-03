# -*- coding: utf-8 -*-
"""Reload shop runtime, place E hint markers, ensure triggers visible-ish, save level."""
from __future__ import print_function
import unreal, sys, traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_e_fix.txt"
PY_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
HUB = "/Game/Maps/Hub/Map_Hub"
lines = []

def log(m):
    lines.append(str(m))
    try: unreal.log("SHOPFIX: " + str(m))
    except Exception: print("SHOPFIX:", m)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def snapshot_buildings():
    snap = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab.startswith(("HubShop_", "HubWall_", "HubCorner_", "HubGate_", "HubMed_", "HubKay_", "HubEnv_", "HubFloor", "HubGround")):
            loc = a.get_actor_location(); rot = a.get_actor_rotation(); scl = a.get_actor_scale3d()
            snap[lab] = (round(loc.x,2), round(loc.y,2), round(loc.z,2), round(rot.yaw,2), round(scl.x,4))
    return snap

def main():
    log("=== shop E fix START ===")
    if PY_DIR not in sys.path:
        sys.path.insert(0, PY_DIR)
    # Force reload runtime
    if "shop_interact_runtime" in sys.modules:
        old = sys.modules["shop_interact_runtime"]
        try:
            h = old._TICK_HANDLE[0]
            if h is not None:
                try: unreal.unregister_slate_post_tick_callback(h)
                except Exception:
                    try: unreal.unregister_slate_pre_tick_callback(h)
                    except Exception: pass
        except Exception as e:
            log("unreg old " + str(e))
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as sir
    log("runtime tick=" + str(sir._TICK_HANDLE[0]))

    # Ensure Map_Hub
    try:
        cw = unreal.EditorLevelLibrary.get_editor_world()
        log("world=" + (cw.get_name() if cw else "None"))
        if cw is None or "Map_Hub" not in cw.get_path_name():
            unreal.EditorLoadingAndSavingUtils.load_map(HUB)
            log("loaded Map_Hub")
    except Exception as e:
        log("load " + str(e))

    before = snapshot_buildings()
    by = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        by[a.get_actor_label() or ""] = a

    # Ensure triggers + make NOT hidden so user can see volume vaguely; keep collision
    shop_map = {
        "ShopTrigger_Weapon": ("HubShop_Weapon", "武器店", "Weapon"),
        "ShopTrigger_Armor": ("HubShop_Armor", "防具店", "Armor"),
        "ShopTrigger_Health": ("HubShop_Health", "回血店", "Health"),
    }
    for tlab, (hub, title, kind) in shop_map.items():
        hub_a = by.get(hub)
        trig = by.get(tlab)
        if hub_a is None:
            log("MISSING " + hub); continue
        loc = hub_a.get_actor_location()
        tloc = unreal.Vector(loc.x, loc.y, loc.z + 100.0)
        if trig is None:
            trig = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TriggerBox.static_class(), tloc, unreal.Rotator())
            trig.set_actor_label(tlab)
            try: trig.set_folder_path("Interact")
            except Exception: pass
            log("spawned " + tlab)
            by[tlab] = trig
        else:
            # Snap trigger back onto shop if drifted
            try: trig.set_actor_location(tloc, False, True)
            except Exception:
                try: trig.set_actor_location(tloc, False, False)
                except Exception as e: log("set loc " + str(e))
        try: trig.set_editor_property("tags", ["ShopInteract", "ShopTitle:" + title, "ShopKind:" + kind])
        except Exception as e: log("tags " + str(e))
        box = trig.get_component_by_class(unreal.BoxComponent)
        if box:
            try: box.set_box_extent(unreal.Vector(180.0, 180.0, 180.0), True)
            except Exception: pass
            try: box.set_collision_profile_name("OverlapAllDynamic")
            except Exception: pass
            try: box.set_editor_property("generate_overlap_events", True)
            except Exception: pass
        # Visible in game as wire? TriggerBox hidden by default - unhide actor but keep box hidden? 
        # Show a TextRender hint instead.
        try: trig.set_actor_hidden_in_game(True)
        except Exception: pass

    gate_hub = by.get("HubGate_DungeonEntrance")
    gate = by.get("GateTrigger_DungeonEntrance")
    if gate_hub:
        gloc = gate_hub.get_actor_location()
        tloc = unreal.Vector(gloc.x, gloc.y, gloc.z + 100.0)
        if gate is None:
            gate = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TriggerBox.static_class(), tloc, unreal.Rotator())
            gate.set_actor_label("GateTrigger_DungeonEntrance")
            try: gate.set_folder_path("Interact")
            except Exception: pass
            log("spawned gate trigger")
            by["GateTrigger_DungeonEntrance"] = gate
        else:
            try: gate.set_actor_location(tloc, False, True)
            except Exception:
                try: gate.set_actor_location(tloc, False, False)
                except Exception: pass
        try: gate.set_editor_property("tags", ["GateInteract"])
        except Exception: pass
        box = gate.get_component_by_class(unreal.BoxComponent)
        if box:
            try: box.set_box_extent(unreal.Vector(200.0, 200.0, 180.0), True)
            except Exception: pass
            try: box.set_collision_profile_name("OverlapAllDynamic")
            except Exception: pass
        try: gate.set_actor_hidden_in_game(True)
        except Exception: pass

    # Place / refresh TextRender markers "按E"
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
            m = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor.static_class(), mloc, unreal.Rotator(0, 0, 0))
            if m:
                m.set_actor_label(mlab)
                try: m.set_folder_path("Interact")
                except Exception: pass
                log("spawned hint " + mlab)
                by[mlab] = m
        if m:
            try: m.set_actor_location(mloc, False, True)
            except Exception:
                try: m.set_actor_location(mloc, False, False)
                except Exception: pass
            try:
                tr = m.get_component_by_class(unreal.TextRenderComponent)
                if tr:
                    tr.set_text(text)
                    try: tr.set_horizontal_alignment(unreal.HorizontalTextAligment.EHTA_CENTER)
                    except Exception: pass
                    try: tr.set_world_size(48.0)
                    except Exception:
                        try: tr.set_editor_property("world_size", 48.0)
                        except Exception: pass
                    try: tr.set_text_render_color(unreal.Color(255, 220, 64, 255))
                    except Exception: pass
            except Exception as e:
                log("text " + mlab + " " + str(e))

    after = snapshot_buildings()
    ok = before == after
    log("buildings_unchanged=%s count=%d" % (ok, len(before)))
    if not ok:
        for k in before:
            if before.get(k) != after.get(k):
                log("CHANGED " + k + " " + str(before.get(k)) + " -> " + str(after.get(k)))

    try:
        unreal.EditorLevelLibrary.save_current_level(); log("level saved")
    except Exception as e:
        log("save level " + str(e))
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True); log("dirty saved")
    except Exception as e:
        log("dirty " + str(e))

    # Final trigger list
    labs = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab.startswith(("ShopTrigger_", "GateTrigger_", "InteractHint_")):
            labs.append(lab)
    log("interact_actors=" + str(sorted(labs)))
    log("=== shop E fix DONE ===")

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
flush()