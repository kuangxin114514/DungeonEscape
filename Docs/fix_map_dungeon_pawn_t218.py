# -*- coding: utf-8 -*-
"""Fix Map_Dungeon: GM_Dungeon DefaultPawn=BP_KayKitKnight, PlayerStart, WorldSettings GM.
Also shrink GATE_RANGE. Does NOT edit Map_Hub buildings."""
from __future__ import print_function
import traceback
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_map_dungeon_pawn_t218.txt"
DUNGEON_MAP = "/Game/Maps/Dungeon/Map_Dungeon"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GM_DUNGEON = "/Game/Core/GameFlow/GM_Dungeon"
BP_CHAR = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
RUNTIME_DOCS = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
RUNTIME_CONTENT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
_lines = []


def log(msg):
    s = str(msg)
    _lines.append(s)
    try:
        unreal.log("FixDungeonPawnT218: " + s)
    except Exception:
        print(s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


def load_pawn_class():
    for path in (
        BP_CHAR + ".BP_KayKitKnight_C",
        BP_CHAR + "_C",
        BP_CHAR,
    ):
        try:
            cls = unreal.load_class(None, path)
            if cls:
                log("pawn_class ok path=" + path + " -> " + str(cls))
                return cls
        except Exception as e:
            log("load_class fail " + path + " " + str(e))
    # asset then generated
    try:
        bp = unreal.EditorAssetLibrary.load_asset(BP_CHAR)
        if bp:
            gen = None
            try:
                gen = bp.generated_class()
            except Exception:
                try:
                    gen = bp.get_editor_property("generated_class")
                except Exception:
                    pass
            if gen:
                log("pawn via generated_class " + str(gen))
                return gen
    except Exception as e:
        log("pawn asset fail " + str(e))
    return None


def configure_gm(pawn):
    gm_bp = unreal.EditorAssetLibrary.load_asset(GM_DUNGEON)
    if not gm_bp:
        log("FAIL load GM_Dungeon asset")
        return False
    try:
        unreal.KismetEditorUtilities.compile_blueprint(gm_bp)
        log("pre-compile GM_Dungeon")
    except Exception as e:
        log("pre-compile " + str(e))
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        try:
            gm_cls = gm_bp.generated_class()
        except Exception:
            gm_cls = None
    if not gm_cls:
        log("FAIL GM_Dungeon_C")
        return False
    cdo = unreal.get_default_object(gm_cls)
    before = None
    try:
        before = cdo.get_editor_property("default_pawn_class")
    except Exception:
        try:
            before = cdo.get_editor_property("DefaultPawnClass")
        except Exception:
            pass
    log("GM_Dungeon DefaultPawn BEFORE=" + str(before))
    ok = False
    for prop in ("default_pawn_class", "DefaultPawnClass"):
        try:
            cdo.set_editor_property(prop, pawn)
            log("set CDO %s ok" % prop)
            ok = True
            break
        except Exception as e:
            log("set CDO %s fail %s" % (prop, e))
    # also try on BP asset itself
    for prop in ("default_pawn_class", "DefaultPawnClass"):
        try:
            gm_bp.set_editor_property(prop, pawn)
            log("set BP asset %s ok" % prop)
        except Exception:
            pass
    try:
        cdo.set_editor_property("player_controller_class", unreal.PlayerController.static_class())
    except Exception:
        try:
            cdo.set_editor_property("PlayerControllerClass", unreal.PlayerController.static_class())
        except Exception:
            pass
    try:
        unreal.KismetEditorUtilities.compile_blueprint(gm_bp)
        log("post-compile GM_Dungeon")
    except Exception as e:
        log("post-compile " + str(e))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(gm_bp)
        unreal.EditorAssetLibrary.save_asset(GM_DUNGEON)
        log("saved GM_Dungeon")
    except Exception as e:
        log("save GM_Dungeon " + str(e))
    # reload and verify
    gm_cls2 = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    cdo2 = unreal.get_default_object(gm_cls2) if gm_cls2 else None
    after = None
    if cdo2:
        try:
            after = cdo2.get_editor_property("default_pawn_class")
        except Exception:
            try:
                after = cdo2.get_editor_property("DefaultPawnClass")
            except Exception:
                pass
    log("GM_Dungeon DefaultPawn AFTER=" + str(after))
    return ok and after is not None


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


def ensure_player_start():
    by = actors_by_label()
    ps = by.get("Dungeon_PlayerStart")
    # also any PlayerStart
    if not ps:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if isinstance(a, unreal.PlayerStart):
                ps = a
                try:
                    a.set_actor_label("Dungeon_PlayerStart")
                except Exception:
                    pass
                break
    if ps:
        try:
            ps.set_actor_location(unreal.Vector(0.0, 0.0, 150.0), False, False)
        except Exception:
            try:
                ps.set_actor_location(unreal.Vector(0.0, 0.0, 150.0), False, True)
            except Exception as e:
                log("move PlayerStart fail " + str(e))
        log("PlayerStart present loc=" + str(ps.get_actor_location()))
        return True
    a = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 150.0))
    if a:
        try:
            a.set_actor_label("Dungeon_PlayerStart")
        except Exception:
            pass
        log("spawned Dungeon_PlayerStart")
        return True
    log("FAIL PlayerStart")
    return False


def ensure_floor_collision():
    by = actors_by_label()
    floor = by.get("Dungeon_Floor")
    if not floor:
        log("no Dungeon_Floor")
        return
    try:
        mesh = floor.static_mesh_component
        try:
            mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        except Exception:
            try:
                mesh.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            except Exception as e:
                log("collision set fail " + str(e))
        try:
            mesh.set_collision_profile_name("BlockAll")
        except Exception:
            pass
        log("Dungeon_Floor collision enabled")
    except Exception as e:
        log("floor fix " + str(e))


def set_world_gm():
    world = unreal.EditorLevelLibrary.get_editor_world()
    ws = world.get_world_settings()
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if not gm_cls:
        log("FAIL GM_Dungeon_C for WorldSettings")
        return False
    before = None
    try:
        before = ws.get_editor_property("default_game_mode")
    except Exception:
        try:
            before = ws.get_editor_property("DefaultGameMode")
        except Exception:
            pass
    log("WorldSettings DefaultGameMode BEFORE=" + str(before))
    ok = False
    for prop in ("default_game_mode", "DefaultGameMode"):
        try:
            ws.set_editor_property(prop, gm_cls)
            log("WorldSettings %s -> GM_Dungeon" % prop)
            ok = True
            break
        except Exception as e:
            log("set %s fail %s" % (prop, e))
    after = None
    try:
        after = ws.get_editor_property("default_game_mode")
    except Exception:
        try:
            after = ws.get_editor_property("DefaultGameMode")
        except Exception:
            pass
    log("WorldSettings DefaultGameMode AFTER=" + str(after))
    return ok


def shrink_gate_range():
    """Shrink GATE_RANGE to 280 (tighter than shops 320)."""
    import re as _re
    import shutil
    import os
    new_val = "GATE_RANGE = 280.0"
    for path in (RUNTIME_DOCS, RUNTIME_CONTENT):
        if not os.path.exists(path):
            log("missing " + path)
            continue
        raw = open(path, "r", encoding="utf-8").read()
        if "GATE_RANGE" not in raw:
            log("no GATE_RANGE in " + path)
            continue
        new = _re.sub(r"GATE_RANGE\s*=\s*[0-9.]+", new_val, raw, count=1)
        if new == raw:
            log("GATE_RANGE pattern unchanged in " + path)
        else:
            open(path, "w", encoding="utf-8").write(new)
            log("patched " + path + " -> " + new_val)
    # reload module
    import sys
    import importlib
    try:
        # ensure Content/Python on path
        py_dir = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
        if py_dir not in sys.path:
            sys.path.insert(0, py_dir)
        docs = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
        if docs not in sys.path:
            sys.path.insert(0, docs)
        if "shop_interact_runtime" in sys.modules:
            importlib.reload(sys.modules["shop_interact_runtime"])
            log("reloaded shop_interact_runtime GATE_RANGE=" + str(getattr(sys.modules["shop_interact_runtime"], "GATE_RANGE", None)))
        else:
            m = __import__("shop_interact_runtime")
            log("imported shop_interact_runtime GATE_RANGE=" + str(getattr(m, "GATE_RANGE", None)))
    except Exception as e:
        log("reload runtime fail " + str(e))


def main():
    log("=== fix_map_dungeon_pawn_t218 ===")
    try:
        shrink_gate_range()
        pawn = load_pawn_class()
        if not pawn:
            log("FATAL no pawn class")
            flush()
            return
        if not unreal.EditorAssetLibrary.does_asset_exist(DUNGEON_MAP):
            log("FATAL Map_Dungeon missing")
            flush()
            return
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON_MAP)
        log("loaded Map_Dungeon")
        world = unreal.EditorLevelLibrary.get_editor_world()
        log("world=" + str(world.get_path_name()))
        configure_gm(pawn)
        ensure_player_start()
        ensure_floor_collision()
        set_world_gm()
        # ensure lights/floor still there (don't recreate hub stuff)
        by = actors_by_label()
        log("dungeon_labels=" + ",".join(sorted([k for k in by if k.startswith("Dungeon_")])))
        unreal.EditorLevelLibrary.save_current_level()
        unreal.EditorAssetLibrary.save_asset(DUNGEON_MAP)
        log("Map_Dungeon saved")
        # return to hub WITHOUT modifying buildings
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("reloaded Map_Hub (buildings untouched)")
        log("DONE")
    except Exception as e:
        log("FATAL " + str(e))
        log(traceback.format_exc())
        try:
            unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
            log("recovered to Map_Hub")
        except Exception:
            pass
    flush()


main()
