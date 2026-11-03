# -*- coding: utf-8 -*-
"""Place auto-possess KayKit in Map_Dungeon + runtime ensure pawn after OpenLevel.
Also keep GATE_RANGE=280. Does NOT edit Map_Hub buildings."""
from __future__ import print_function
import os
import re
import sys
import traceback
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_dungeon_pawn_spawn_t218b.txt"
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
        unreal.log("FixDungeonSpawnT218b: " + s)
    except Exception:
        print(s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


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


def set_auto_possess(actor):
    # EAutoReceiveInput::Player0
    vals = []
    try:
        vals.append(unreal.AutoReceiveInput.PLAYER0)
    except Exception:
        pass
    try:
        vals.append(getattr(unreal.AutoReceiveInput, "Player0", None))
    except Exception:
        pass
    # integer fallback Player0 == 1 in UE enum (Disabled=0, Player0=1)
    vals.append(1)
    for prop in ("auto_possess_player", "AutoPossessPlayer"):
        for v in vals:
            if v is None:
                continue
            try:
                actor.set_editor_property(prop, v)
                log("set %s=%s" % (prop, v))
                return True
            except Exception as e:
                log("set %s fail %s" % (prop, e))
    return False


def ensure_placed_pawn():
    pawn_cls = unreal.load_class(None, BP_CHAR + ".BP_KayKitKnight_C")
    if not pawn_cls:
        log("FAIL pawn class")
        return False
    by = actors_by_label()
    existing = by.get("Dungeon_PlayerPawn")
    loc = unreal.Vector(0.0, 0.0, 150.0)
    ps = by.get("Dungeon_PlayerStart")
    if not ps:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if isinstance(a, unreal.PlayerStart):
                ps = a
                break
    if ps:
        try:
            loc = ps.get_actor_location()
            # lift a bit so capsule clears floor
            loc = unreal.Vector(loc.x, loc.y, max(loc.z, 150.0))
        except Exception:
            pass
    if existing:
        try:
            existing.set_actor_location(loc, False, False)
        except Exception:
            pass
        set_auto_possess(existing)
        log("updated existing Dungeon_PlayerPawn at " + str(loc))
        return True
    # destroy other stray kaykit if any unlabeled
    a = spawn(pawn_cls, loc)
    if not a:
        log("FAIL spawn Dungeon_PlayerPawn")
        return False
    try:
        a.set_actor_label("Dungeon_PlayerPawn")
    except Exception:
        pass
    set_auto_possess(a)
    log("spawned Dungeon_PlayerPawn at " + str(loc))
    return True


def ensure_gm_and_ps():
    pawn = unreal.load_class(None, BP_CHAR + ".BP_KayKitKnight_C")
    gm_cls = unreal.load_class(None, GM_DUNGEON + ".GM_Dungeon_C")
    if gm_cls and pawn:
        cdo = unreal.get_default_object(gm_cls)
        try:
            cdo.set_editor_property("default_pawn_class", pawn)
            log("GM_Dungeon default_pawn refreshed")
        except Exception as e:
            log("gm pawn " + str(e))
        try:
            unreal.EditorAssetLibrary.save_asset(GM_DUNGEON)
        except Exception:
            pass
    ws = unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
    if gm_cls:
        try:
            ws.set_editor_property("default_game_mode", gm_cls)
            log("WorldSettings GM refreshed")
        except Exception as e:
            log("ws " + str(e))
    by = actors_by_label()
    if "Dungeon_PlayerStart" not in by:
        ps = None
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if isinstance(a, unreal.PlayerStart):
                ps = a
                break
        if not ps:
            ps = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 150.0))
            log("spawned PlayerStart")
        if ps:
            try:
                ps.set_actor_label("Dungeon_PlayerStart")
            except Exception:
                pass
    else:
        log("PlayerStart ok")


RUNTIME_ENSURE_SNIPPET = r'''
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
'''


def patch_runtime():
    for path in (RUNTIME_DOCS, RUNTIME_CONTENT):
        if not os.path.exists(path):
            log("missing " + path)
            continue
        raw = open(path, "r", encoding="utf-8").read()
        # GATE_RANGE
        raw2 = re.sub(r"GATE_RANGE\s*=\s*[0-9.]+", "GATE_RANGE = 280.0", raw, count=1)
        if "ensure_dungeon_pawn" not in raw2:
            # insert helpers before _on_tick
            marker = "def _on_tick(dt):"
            if marker not in raw2:
                log("no _on_tick in " + path)
            else:
                raw2 = raw2.replace(marker, RUNTIME_ENSURE_SNIPPET + "\n\n" + marker, 1)
                log("inserted ensure_dungeon_pawn into " + path)
        else:
            log("ensure_dungeon_pawn already in " + path)
        # call ensure early in _on_tick after world resolved
        if "ensure_dungeon_pawn(world)" not in raw2:
            needle = "world = _pie_world()\n    if world is None:"
            # add after world check passes - find "_fix_view_once(world)"
            if "_fix_view_once(world)" in raw2:
                raw2 = raw2.replace(
                    "_fix_view_once(world)",
                    "ensure_dungeon_pawn(world)\n    _fix_view_once(world)",
                    1,
                )
                log("wired ensure_dungeon_pawn call in " + path)
            else:
                log("WARN no _fix_view_once to wire in " + path)
        open(path, "w", encoding="utf-8").write(raw2)
        log("wrote " + path)


def reload_runtime():
    py_dir = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    docs = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
    for p in (py_dir, docs):
        if p not in sys.path:
            sys.path.insert(0, p)
    import importlib
    try:
        if "shop_interact_runtime" in sys.modules:
            importlib.reload(sys.modules["shop_interact_runtime"])
            m = sys.modules["shop_interact_runtime"]
        else:
            m = __import__("shop_interact_runtime")
        log("runtime GATE_RANGE=" + str(getattr(m, "GATE_RANGE", None)))
        log("has ensure_dungeon_pawn=" + str(hasattr(m, "ensure_dungeon_pawn")))
    except Exception as e:
        log("reload fail " + str(e) + "\n" + traceback.format_exc())


def main():
    log("=== fix_dungeon_pawn_spawn_t218b ===")
    try:
        patch_runtime()
        if not unreal.EditorAssetLibrary.does_asset_exist(DUNGEON_MAP):
            # maps often "not exist" via DoesAssetExist - still try load
            log("DoesAssetExist false (maps often); loading anyway")
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON_MAP)
        log("loaded Map_Dungeon path=" + str(unreal.EditorLevelLibrary.get_editor_world().get_path_name()))
        ensure_gm_and_ps()
        ensure_placed_pawn()
        # floor collision
        by = actors_by_label()
        floor = by.get("Dungeon_Floor")
        if floor:
            try:
                mesh = floor.static_mesh_component
                mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
                try:
                    mesh.set_collision_profile_name("BlockAll")
                except Exception:
                    pass
                log("floor collision ok")
            except Exception as e:
                log("floor " + str(e))
        labs = sorted([k for k in by.keys() if k.startswith("Dungeon_")] + (["Dungeon_PlayerPawn"] if "Dungeon_PlayerPawn" in actors_by_label() else []))
        # refresh labels
        labs = sorted([k for k in actors_by_label().keys() if k.startswith("Dungeon_")])
        log("labels=" + ",".join(labs))
        unreal.EditorLevelLibrary.save_current_level()
        log("saved level")
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("reloaded Map_Hub (buildings untouched)")
        reload_runtime()
        log("DONE")
    except Exception as e:
        log("FATAL " + str(e))
        log(traceback.format_exc())
        try:
            unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        except Exception:
            pass
    flush()


main()
