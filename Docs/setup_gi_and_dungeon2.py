# -*- coding: utf-8 -*-
"""T309: GI Gold/Inventory + blank Map_Dungeon2 with Playable pawn. Does NOT edit Map_Hub buildings."""
from __future__ import print_function
import os
import traceback
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_gi_and_dungeon2.txt"
GI_PATH = "/Game/Core/GameFlow/GI_DungeonGame"
GM_DUNGEON = "/Game/Core/GameFlow/GM_Dungeon"
BP_CHAR = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
DUNGEON_DIR = "/Game/Maps/Dungeon"
DUNGEON2 = DUNGEON_DIR + "/Map_Dungeon2"
DUNGEON1 = DUNGEON_DIR + "/Map_Dungeon1"
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T309: " + s)
    except Exception:
        print("T309:", s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)
        log("mkdir " + path)


def get_bel():
    bel = getattr(unreal, "BlueprintEditorLibrary", None)
    if bel is not None:
        return bel
    # UE4.27 sometimes needs explicit load
    for path in (
        "/Script/BlueprintEditorLibrary.BlueprintEditorLibrary",
        "/Script/EditorScriptingUtilities.EditorAssetLibrary",
    ):
        try:
            cls = unreal.load_class(None, path)
            log("load_class %s -> %s" % (path, cls))
        except Exception as e:
            log("load_class fail %s: %s" % (path, e))
    return getattr(unreal, "BlueprintEditorLibrary", None)


def try_add_gi_vars():
    log("=== GI vars ===")
    if not unreal.EditorAssetLibrary.does_asset_exist(GI_PATH):
        # recreate like create_gameflow_assets
        ensure_dir("/Game/Core/GameFlow")
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", unreal.GameInstance.static_class())
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "GI_DungeonGame", "/Game/Core/GameFlow", None, factory
        )
        if bp:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            log("created GI_DungeonGame")
        else:
            log("FAIL create GI")
            return False
    bp = unreal.EditorAssetLibrary.load_asset(GI_PATH)
    log("bp=%s" % bp)
    bel = get_bel()
    log("BEL=%s" % bel)
    added = []
    if bel is not None and hasattr(bel, "add_member_variable"):
        # Gold int
        try:
            pin = unreal.EdGraphPinType()
            for cat in ("int", "int64", "integer"):
                try:
                    pin.set_editor_property("pin_category", cat)
                    break
                except Exception:
                    pass
            ok = bel.add_member_variable(bp, "Gold", pin)
            log("add Gold -> %s" % ok)
            added.append("Gold")
        except Exception as e:
            log("add Gold EXC %s" % e)
        # Inventory string array
        try:
            pin = unreal.EdGraphPinType()
            try:
                pin.set_editor_property("pin_category", "string")
            except Exception:
                pin.set_editor_property("pin_category", "name")
            # container array
            for prop, val in (
                ("container_type", getattr(unreal, "EdGraphPinContainerType", None)),
                ("ContainerType", getattr(unreal, "EdGraphPinContainerType", None)),
            ):
                enum = val
                if enum is None:
                    continue
                for attr in ("ARRAY", "Array", "PC_Array"):
                    if hasattr(enum, attr):
                        try:
                            pin.set_editor_property(prop, getattr(enum, attr))
                            log("set %s=%s" % (prop, attr))
                            break
                        except Exception as e:
                            log("set container %s" % e)
            ok = bel.add_member_variable(bp, "Inventory", pin)
            log("add Inventory -> %s" % ok)
            added.append("Inventory")
        except Exception as e:
            log("add Inventory EXC %s" % e)
    else:
        log("NOTE: BlueprintEditorLibrary.add_member_variable unavailable in this UE4.27 Python.")
        log("Python player_meta (shop_interact_runtime) will store Gold/Inventory.")
        log("Optional manual: open GI_DungeonGame, add Int Gold=100 and String[] Inventory.")

    # Compile + set defaults on CDO if props exist
    try:
        if bel is not None and hasattr(bel, "compile_blueprint"):
            bel.compile_blueprint(bp)
            log("compiled GI via BEL")
        else:
            try:
                unreal.KismetEditorUtilities.compile_blueprint(bp)
                log("compiled GI via KismetEditorUtilities")
            except Exception as e:
                log("compile GI skip %s" % e)
    except Exception as e:
        log("compile EXC %s" % e)

    cls = None
    try:
        cls = unreal.EditorAssetLibrary.load_blueprint_class(GI_PATH)
    except Exception:
        cls = None
    if cls is None:
        try:
            cls = unreal.load_class(None, GI_PATH + ".GI_DungeonGame_C")
        except Exception:
            cls = None
    cdo = unreal.get_default_object(cls) if cls else None
    log("cls=%s cdo=%s" % (cls, cdo))
    if cdo:
        try:
            cdo.set_editor_property("Gold", 100)
            log("CDO Gold=100")
        except Exception as e:
            log("CDO Gold set fail: %s" % e)
        try:
            cdo.set_editor_property("Inventory", [])
            log("CDO Inventory=[]")
        except Exception as e:
            log("CDO Inventory set fail: %s" % e)
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved GI")
    except Exception as e:
        log("save GI %s" % e)
    # Confirm project setting already points here
    log("DefaultEngine.ini should have GameInstanceClass=/Game/Core/GameFlow/GI_DungeonGame.GI_DungeonGame_C")
    return True


def spawn(cls, loc, rot=None):
    if rot is None:
        rot = unreal.Rotator(0.0, 0.0, 0.0)
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        return sub.spawn_actor_from_class(cls, loc, rot)
    except Exception:
        return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)


def actors_by_label():
    out = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            out[a.get_actor_label() or ""] = a
        except Exception:
            pass
    return out


def ensure_label(cls, label, loc, rot=None, setup=None):
    by = actors_by_label()
    if label in by:
        log("keep " + label)
        return by[label]
    a = spawn(cls, loc, rot)
    if a:
        try:
            a.set_actor_label(label)
        except Exception:
            pass
        if setup:
            setup(a)
        log("spawn " + label)
    else:
        log("FAIL spawn " + label)
    return a


def paint_floor(actor):
    sm = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    mesh = actor.static_mesh_component
    mesh.set_static_mesh(sm)
    actor.set_actor_scale3d(unreal.Vector(30.0, 30.0, 1.0))


def paint_marker(actor):
    sm = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    mesh = actor.static_mesh_component
    mesh.set_static_mesh(sm)
    actor.set_actor_scale3d(unreal.Vector(1.5, 1.5, 3.0))


def configure_gm_dungeon():
    pawn = unreal.load_class(None, BP_CHAR + ".BP_KayKitKnight_C")
    if not pawn:
        log("FAIL load BP_KayKitKnight_C")
        return False
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        try:
            gm_bp = unreal.EditorAssetLibrary.load_asset(GM_DUNGEON)
            try:
                unreal.KismetEditorUtilities.compile_blueprint(gm_bp)
            except Exception:
                bel = get_bel()
                if bel and hasattr(bel, "compile_blueprint"):
                    bel.compile_blueprint(gm_bp)
            gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
        except Exception as e:
            log("compile GM_Dungeon " + str(e))
    if not gm_cls:
        log("FAIL GM_Dungeon_C")
        return False
    cdo = unreal.get_default_object(gm_cls)
    ok = False
    for prop in ("default_pawn_class", "DefaultPawnClass"):
        try:
            cdo.set_editor_property(prop, pawn)
            log("GM_Dungeon %s -> KayKit" % prop)
            ok = True
            break
        except Exception as e:
            log("set %s fail %s" % (prop, e))
    try:
        unreal.EditorAssetLibrary.save_asset(GM_DUNGEON)
    except Exception as e:
        log("save GM %s" % e)
    return ok


def set_world_gm():
    world = unreal.EditorLevelLibrary.get_editor_world()
    ws = world.get_world_settings()
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        log("FAIL GM for WorldSettings")
        return False
    for prop in ("default_game_mode", "DefaultGameMode"):
        try:
            ws.set_editor_property(prop, gm_cls)
            log("WorldSettings %s -> GM_Dungeon" % prop)
            return True
        except Exception as e:
            log("set %s fail %s" % (prop, e))
    return False


def ensure_map_dungeon2():
    log("=== Map_Dungeon2 ===")
    ensure_dir(DUNGEON_DIR)
    # Remember previous map to restore (prefer Dungeon1, never force Hub edit)
    prev = None
    try:
        w = unreal.EditorLevelLibrary.get_editor_world()
        prev = w.get_path_name() if w else None
    except Exception:
        prev = None
    log("prev_world=" + str(prev))

    if unreal.EditorAssetLibrary.does_asset_exist(DUNGEON2):
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON2)
        log("loaded existing Map_Dungeon2")
    else:
        try:
            unreal.EditorLevelLibrary.new_level(DUNGEON2)
            log("Created Map_Dungeon2 via new_level")
        except Exception as e:
            log("new_level failed: " + str(e))
            factory = unreal.WorldFactory()
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            world_asset = asset_tools.create_asset("Map_Dungeon2", DUNGEON_DIR, unreal.World, factory)
            if not world_asset:
                log("FAIL create Map_Dungeon2")
                return False
            unreal.EditorAssetLibrary.save_loaded_asset(world_asset)
            unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON2)
            log("Created Map_Dungeon2 via WorldFactory")

    ensure_label(unreal.StaticMeshActor, "Dungeon2_Floor", unreal.Vector(0.0, 0.0, 0.0), setup=paint_floor)
    ensure_label(
        unreal.DirectionalLight,
        "Dungeon2_Sun",
        unreal.Vector(0.0, 0.0, 500.0),
        unreal.Rotator(-45.0, -30.0, 0.0),
    )
    ensure_label(unreal.SkyLight, "Dungeon2_SkyLight", unreal.Vector(0.0, 0.0, 600.0))
    try:
        ensure_label(unreal.SkyAtmosphere, "Dungeon2_SkyAtmosphere", unreal.Vector(0.0, 0.0, 0.0))
    except Exception:
        pass
    ensure_label(unreal.PlayerStart, "Dungeon2_PlayerStart", unreal.Vector(0.0, 0.0, 120.0))
    ensure_label(unreal.StaticMeshActor, "Dungeon2_Marker", unreal.Vector(400.0, 0.0, 150.0), setup=paint_marker)

    configure_gm_dungeon()
    set_world_gm()

    unreal.EditorLevelLibrary.save_current_level()
    try:
        unreal.EditorAssetLibrary.save_asset(DUNGEON2)
    except Exception as e:
        log("save asset %s" % e)
    labs = sorted(actors_by_label().keys())
    log("actors=" + ",".join([x for x in labs if x.startswith("Dungeon2_")]))
    log("exists=" + str(unreal.EditorAssetLibrary.does_asset_exist(DUNGEON2)))

    # Restore previous map if it was Dungeon1; else load Dungeon1 (do NOT open Hub to avoid any hub churn)
    restore = DUNGEON1
    if prev and ("Map_Dungeon1" in str(prev)):
        restore = DUNGEON1
    elif prev and ("Map_Dungeon2" in str(prev)):
        restore = DUNGEON2
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(restore):
            unreal.EditorLoadingAndSavingUtils.load_map(restore)
            log("restored map " + restore)
    except Exception as e:
        log("restore fail " + str(e))
    return True


def main():
    log("BEGIN T309 GI + Map_Dungeon2")
    try:
        try_add_gi_vars()
    except Exception as e:
        log("GI EXC " + str(e))
        log(traceback.format_exc())
    try:
        ensure_map_dungeon2()
    except Exception as e:
        log("D2 EXC " + str(e))
        log(traceback.format_exc())
    log("DONE")
    flush()
    print("WROTE", OUT)


main()
