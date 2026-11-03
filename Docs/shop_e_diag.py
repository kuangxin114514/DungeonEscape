# -*- coding: utf-8 -*-
"""Diagnose shop E interact failure."""
from __future__ import print_function
import unreal
import traceback
import sys

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_e_diag.txt"
PY_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("E_DIAG: " + s)
    except Exception:
        print("E_DIAG: " + s)

def flush():
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

try:
    log("=== START ===")
    # init_unreal / runtime status
    if PY_DIR not in sys.path:
        sys.path.insert(0, PY_DIR)
    log("sys.path has PY_DIR=" + str(PY_DIR in sys.path))
    sir = None
    try:
        import shop_interact_runtime as sir
        log("runtime imported tick=" + str(sir._TICK_HANDLE[0]))
        log("OPEN_WIDGET=" + str(sir._OPEN_WIDGET[0]))
        log("NEAR_SHOP=" + str(sir._NEAR_SHOP_TITLE[0]))
        log("NEAR_GATE=" + str(sir._NEAR_GATE[0]))
    except Exception as e:
        log("runtime import FAIL " + str(e))

    # editor level actors
    by_lab = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        by_lab[lab] = a
    log("current_level_actors=" + str(len(by_lab)))
    for name in ("ShopTrigger_Weapon","ShopTrigger_Armor","ShopTrigger_Health","GateTrigger_DungeonEntrance",
                 "HubShop_Weapon","HubShop_Armor","HubShop_Health","HubGate_DungeonEntrance"):
        a = by_lab.get(name)
        if not a:
            log("MISSING " + name)
            continue
        loc = a.get_actor_location()
        tags = []
        try:
            tags = [str(t) for t in list(a.get_editor_property("tags"))]
        except Exception as e:
            tags = ["ERR:"+str(e)]
        cls = a.get_class().get_name()
        hidden = None
        try:
            hidden = a.is_hidden_ed() if False else a.get_editor_property("b_hidden")
        except Exception:
            try:
                hidden = a.b_hidden
            except Exception:
                hidden = "?"
        log("%s cls=%s loc=(%.1f,%.1f,%.1f) tags=%s hidden=%s" % (name, cls, loc.x, loc.y, loc.z, tags, hidden))
        # box
        try:
            box = a.get_component_by_class(unreal.BoxComponent)
            if box:
                ext = box.get_unscaled_box_extent()
                log("  box extent=(%.1f,%.1f,%.1f) profile=%s gen_overlap=%s" % (
                    ext.x, ext.y, ext.z,
                    str(box.get_collision_profile_name()),
                    str(box.get_editor_property("generate_overlap_events") if True else "?")))
        except Exception as e:
            log("  box err " + str(e))

    # asset existence
    for p in ("/Game/UI/Shop/WBP_Shop", "/Game/Core/Interact/BP_ShopInteract",
              "/Game/Core/GameFlow/GM_Hub", "/Game/Characters/Player/KayKit/BP_KayKitKnight"):
        log("asset %s exist=%s" % (p, unreal.EditorAssetLibrary.does_asset_exist(p)))

    # WBP class load
    wcls = unreal.load_class(None, "/Game/UI/Shop/WBP_Shop.WBP_Shop_C")
    log("WBP_Shop_C=" + str(wcls))

    # PIE world
    pie = None
    try:
        worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
        log("pie_worlds=" + str(worlds))
        if worlds:
            pie = worlds[0]
    except Exception as e:
        log("pie err " + str(e))
    try:
        gw = unreal.EditorLevelLibrary.get_game_world()
        log("game_world=" + str(gw))
        if pie is None:
            pie = gw
    except Exception as e:
        log("game_world err " + str(e))

    if pie:
        pc = unreal.GameplayStatics.get_player_controller(pie, 0)
        log("PC=" + str(pc))
        pawn = pc.get_controlled_pawn() if pc else None
        log("Pawn=" + str(pawn) + " cls=" + (pawn.get_class().get_name() if pawn else "None"))
        if pawn:
            pl = pawn.get_actor_location()
            log("pawn_loc=(%.1f,%.1f,%.1f)" % (pl.x, pl.y, pl.z))
            # distances to triggers via GameplayStatics
            try:
                tbs = unreal.GameplayStatics.get_all_actors_of_class(pie, unreal.TriggerBox.static_class())
                log("PIE TriggerBox count=" + str(len(list(tbs))))
                for a in tbs:
                    lab = a.get_actor_label() if hasattr(a, "get_actor_label") else "?"
                    try:
                        lab = a.get_actor_label()
                    except Exception:
                        lab = a.get_name()
                    tags = []
                    try:
                        tags = [str(t) for t in list(a.get_editor_property("tags"))]
                    except Exception:
                        try:
                            tags = [str(t) for t in list(a.tags)]
                        except Exception:
                            tags = []
                    loc = a.get_actor_location()
                    dx, dy, dz = loc.x-pl.x, loc.y-pl.y, loc.z-pl.z
                    dist = (dx*dx+dy*dy+dz*dz)**0.5
                    log("  TB %s dist=%.1f tags=%s loc=(%.1f,%.1f,%.1f)" % (lab, dist, tags, loc.x, loc.y, loc.z))
            except Exception as e:
                log("TB scan " + traceback.format_exc())
            # key state
            if pc:
                for kn in ("E", "Escape", "W"):
                    try:
                        just = pc.was_input_key_just_pressed(unreal.Key(key_name=kn))
                    except Exception as e:
                        just = "ERR:"+str(e)
                    try:
                        down = pc.is_input_key_down(unreal.Key(key_name=kn))
                    except Exception as e:
                        down = "ERR:"+str(e)
                    log("key %s just=%s down=%s" % (kn, just, down))
        # world settings / gamemode
        try:
            gm = unreal.GameplayStatics.get_game_mode(pie)
            log("GameMode=" + str(gm) + " " + (gm.get_class().get_name() if gm else ""))
        except Exception as e:
            log("gm err " + str(e))
    else:
        log("NO PIE - editor only diag")

    # DefaultInput Interact
    log("check DefaultInput has Interact=E (external)")

    # GM_Hub default pawn
    try:
        gm_asset = unreal.EditorAssetLibrary.load_asset("/Game/Core/GameFlow/GM_Hub")
        log("GM_Hub=" + str(gm_asset))
        cdo = unreal.get_default_object(unreal.load_class(None, "/Game/Core/GameFlow/GM_Hub.GM_Hub_C"))
        if cdo:
            for prop in ("default_pawn_class", "DefaultPawnClass", "hud_class"):
                try:
                    log("GM_Hub.%s=%s" % (prop, cdo.get_editor_property(prop)))
                except Exception as e:
                    log("GM_Hub.%s ERR %s" % (prop, e))
    except Exception as e:
        log("GM_Hub inspect " + str(e))

    log("=== DONE ===")
except Exception:
    log("FATAL\n" + traceback.format_exc())
flush()
