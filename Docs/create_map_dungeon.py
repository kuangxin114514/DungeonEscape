# -*- coding: utf-8 -*-
"""Create/finish Map_Dungeon with PlayerStart + GM_Dungeon(BP_KayKitKnight). Does NOT edit Map_Hub buildings."""
from __future__ import print_function
import traceback
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\create_map_dungeon.txt"
DUNGEON_DIR = "/Game/Maps/Dungeon"
DUNGEON_MAP = DUNGEON_DIR + "/Map_Dungeon"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GM_DUNGEON = "/Game/Core/GameFlow/GM_Dungeon"
BP_CHAR = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
_lines = []


def log(msg):
    s = str(msg)
    _lines.append(s)
    try:
        unreal.log("CreateMapDungeon: " + s)
    except Exception:
        print("CreateMapDungeon:", s)


def flush():
    try:
        open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")
    except Exception:
        pass


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)
        log("mkdir " + path)


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


def configure_gm_dungeon():
    pawn = unreal.load_class(None, BP_CHAR + ".BP_KayKitKnight_C")
    if not pawn:
        log("FAIL load BP_KayKitKnight_C")
        return False
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        # try compile via KismetEditorUtilities then reload
        try:
            gm_bp = unreal.EditorAssetLibrary.load_asset(GM_DUNGEON)
            unreal.KismetEditorUtilities.compile_blueprint(gm_bp)
            log("compiled GM_Dungeon via KismetEditorUtilities")
        except Exception as e:
            log("compile GM_Dungeon " + str(e))
        gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        log("FAIL GM_Dungeon_C still missing")
        return False
    cdo = unreal.get_default_object(gm_cls)
    ok = False
    for prop in ("default_pawn_class", "DefaultPawnClass"):
        try:
            cdo.set_editor_property(prop, pawn)
            log("GM_Dungeon CDO %s -> BP_KayKitKnight" % prop)
            ok = True
            break
        except Exception as e:
            log("set %s fail %s" % (prop, e))
    try:
        cdo.set_editor_property("player_controller_class", unreal.PlayerController.static_class())
    except Exception:
        try:
            cdo.set_editor_property("PlayerControllerClass", unreal.PlayerController.static_class())
        except Exception:
            pass
    try:
        unreal.EditorAssetLibrary.save_asset(GM_DUNGEON)
        log("saved GM_Dungeon")
    except Exception as e:
        log("save GM_Dungeon " + str(e))
    return ok


def set_world_gm():
    world = unreal.EditorLevelLibrary.get_editor_world()
    ws = world.get_world_settings()
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        log("FAIL GM_Dungeon_C for WorldSettings")
        return False
    for prop in ("default_game_mode", "DefaultGameMode"):
        try:
            ws.set_editor_property(prop, gm_cls)
            log("WorldSettings %s -> GM_Dungeon" % prop)
            return True
        except Exception as e:
            log("set %s fail %s" % (prop, e))
    return False


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


def ensure_current_is_dungeon():
    ensure_dir(DUNGEON_DIR)
    world = unreal.EditorLevelLibrary.get_editor_world()
    path = ""
    try:
        path = world.get_path_name()
    except Exception:
        pass
    log("current_world=" + str(path))
    if "Map_Dungeon" in str(path) and unreal.EditorAssetLibrary.does_asset_exist(DUNGEON_MAP):
        return True
    if unreal.EditorAssetLibrary.does_asset_exist(DUNGEON_MAP):
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON_MAP)
        log("loaded existing Map_Dungeon")
        return True
    try:
        unreal.EditorLevelLibrary.new_level(DUNGEON_MAP)
        log("Created Map_Dungeon via new_level")
        return True
    except Exception as e:
        log("new_level failed: " + str(e))
        factory = unreal.WorldFactory()
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        world_asset = asset_tools.create_asset("Map_Dungeon", DUNGEON_DIR, unreal.World, factory)
        if not world_asset:
            log("FAIL create Map_Dungeon")
            return False
        unreal.EditorAssetLibrary.save_loaded_asset(world_asset)
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON_MAP)
        log("Created Map_Dungeon via WorldFactory")
        return True


def build_dungeon_level():
    if not ensure_current_is_dungeon():
        return False
    ensure_label(unreal.StaticMeshActor, "Dungeon_Floor", unreal.Vector(0.0, 0.0, 0.0), setup=paint_floor)
    ensure_label(
        unreal.DirectionalLight,
        "Dungeon_Sun",
        unreal.Vector(0.0, 0.0, 500.0),
        unreal.Rotator(-45.0, -30.0, 0.0),
    )
    ensure_label(unreal.SkyLight, "Dungeon_SkyLight", unreal.Vector(0.0, 0.0, 600.0))
    try:
        ensure_label(unreal.SkyAtmosphere, "Dungeon_SkyAtmosphere", unreal.Vector(0.0, 0.0, 0.0))
    except Exception:
        pass
    ensure_label(unreal.PlayerStart, "Dungeon_PlayerStart", unreal.Vector(0.0, 0.0, 120.0))
    ensure_label(unreal.StaticMeshActor, "Dungeon_Marker", unreal.Vector(400.0, 0.0, 150.0), setup=paint_marker)

    configure_gm_dungeon()
    set_world_gm()

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_asset(DUNGEON_MAP)
    log("Map_Dungeon saved")
    # verify labels
    labs = sorted(actors_by_label().keys())
    log("actors=" + ",".join([x for x in labs if x.startswith("Dungeon_")]))
    return True


def return_to_hub():
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("reloaded Map_Hub (buildings untouched)")
        return True
    except Exception as e:
        log("reload hub fail " + str(e))
        return False


def main():
    log("=== create_map_dungeon fix2 ===")
    try:
        ok = build_dungeon_level()
        log("build_ok=" + str(ok))
        return_to_hub()
        log("DONE path=" + DUNGEON_MAP)
        log("exists=" + str(unreal.EditorAssetLibrary.does_asset_exist(DUNGEON_MAP)))
    except Exception as e:
        log("FATAL " + str(e))
        log(traceback.format_exc())
        try:
            return_to_hub()
        except Exception:
            pass
    flush()


main()
