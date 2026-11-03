# -*- coding: utf-8 -*-
"""Spawn a temp skeleton in current PIE world and verify WidgetComponent overhead bar."""
from __future__ import print_function
import unreal
import os
import sys
import importlib
import traceback

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "probe_overhead_wc.txt")
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("PROBEWC: " + s)
    except Exception:
        print(s)


def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    log("=== probe WidgetComponent on skeleton ===")
    pydir = os.path.join(ROOT, "Content", "Python")
    if pydir not in sys.path:
        sys.path.insert(0, pydir)
    import shop_interact_runtime as r
    importlib.reload(r)
    r.bootstrap()
    log("runtime Z=%s draw=%s" % (r._ENEMY_BAR_Z, r._ENEMY_DRAW))

    world = None
    try:
        world = r._pie_world()
    except Exception as e:
        log("pie_world " + str(e))
    if world is None:
        try:
            world = unreal.EditorLevelLibrary.get_game_world()
        except Exception as e:
            log("game_world " + str(e))
    log("world=" + (world.get_path_name() if world else "None"))
    if world is None:
        log("FAIL no PIE world")
        flush()
        return

    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    log("pc=" + str(pc))
    pawn = None
    try:
        pawn = pc.get_controlled_pawn() if pc else None
    except Exception:
        pawn = None
    log("pawn=" + str(pawn))
    spawn_loc = unreal.Vector(0, 0, 200)
    if pawn:
        try:
            pl = pawn.get_actor_location()
            spawn_loc = unreal.Vector(pl.x + 150, pl.y, pl.z)
        except Exception:
            pass
    log("spawn_loc=" + str(spawn_loc))

    cls = None
    for p in (
        "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton.BP_Enemy_Skeleton_C",
        "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton_C",
    ):
        try:
            cls = unreal.load_class(None, p)
            if cls:
                log("cls=" + p)
                break
        except Exception as e:
            log("load_class " + str(e))
    if cls is None:
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton")
            log("cls via EditorAssetLibrary=" + str(cls))
        except Exception as e:
            log("bp class " + str(e))
    if cls is None:
        log("FAIL no enemy class")
        flush()
        return

    actor = None
    # Prefer GameplayStatics spawn in PIE
    for attempt in (
        lambda: unreal.GameplayStatics.begin_deferred_actor_spawn_from_class(world, cls, unreal.Transform(spawn_loc)),
    ):
        try:
            actor = attempt()
            if actor:
                try:
                    unreal.GameplayStatics.finish_spawning_actor(actor, unreal.Transform(spawn_loc))
                except Exception as e:
                    log("finish spawn " + str(e))
                break
        except Exception as e:
            log("deferred spawn " + str(e))
            actor = None
    if actor is None:
        try:
            actor = world.spawn_actor(cls, spawn_loc, unreal.Rotator(0, 0, 0))
            log("world.spawn_actor -> " + str(actor))
        except Exception as e:
            log("world.spawn_actor " + str(e))
    if actor is None:
        try:
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, spawn_loc, unreal.Rotator(0, 0, 0))
            log("EditorLevelLibrary.spawn -> " + str(actor))
        except Exception as e:
            log("editor spawn " + str(e))
    if actor is None:
        log("FAIL spawn")
        flush()
        return
    log("spawned=" + actor.get_name() + " @ " + str(actor.get_actor_location()))

    # Direct WC attach test
    widget, pb, wpath = r._make_enemy_widget(world, pc)
    log("widget=%s pb=%s wpath=%s" % (widget, pb, wpath))
    if widget and pb:
        r._fit_enemy_bar_layout(widget, pb)
        try:
            slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb)
            log("slot anchors/pos after fit: " + str(slot))
            if slot:
                try:
                    log("  anchors=%s" % slot.get_anchors())
                except Exception:
                    pass
                try:
                    log("  offsets=%s" % slot.get_offsets())
                except Exception:
                    pass
                try:
                    log("  size=%s" % slot.get_size())
                except Exception:
                    pass
                try:
                    log("  pos=%s" % slot.get_position())
                except Exception:
                    pass
        except Exception as e:
            log("slot probe " + str(e))
    wc = r._attach_widget_component(actor, widget)
    log("wc=" + str(wc))
    if wc is not None:
        for prop in ("relative_location", "draw_size", "space", "pivot"):
            try:
                log("wc.%s=%s" % (prop, wc.get_editor_property(prop)))
            except Exception as e:
                log("wc.%s err %s" % (prop, e))
        try:
            log("wc.user_widget=" + str(wc.get_user_widget_object()))
        except Exception as e:
            log("wc.user_widget err " + str(e))
        try:
            log("wc.widget_prop=" + str(wc.get_editor_property("widget")))
        except Exception as e:
            log("wc.widget_prop err " + str(e))
        try:
            log("wc.world_loc=" + str(wc.get_world_location()))
        except Exception:
            try:
                log("wc.world_loc=" + str(wc.get_component_location()))
            except Exception as e:
                log("wc.world_loc err " + str(e))

    # Also via ensure path
    r._clear_enemy_bars()
    r.ensure_enemy_health_bars(world, pc, pawn)
    log("bars_after_ensure=%d" % len(r._ENEMY_BARS))
    for k, st in list(r._ENEMY_BARS.items()):
        log("ensure %s wc=%s pb=%s hp=%s/%s" % (k, st.get("wc"), st.get("pb"), st.get("health"), st.get("max_health")))

    # cleanup temp actor after a moment? keep it so user can see if in dungeon/hub
    # Destroy only if we are in Hub and don't want leftovers — destroy to avoid polluting Hub
    try:
        if "Map_Hub" in world.get_path_name():
            actor.destroy_actor()
            log("destroyed temp hub spawn")
            r._clear_enemy_bars()
    except Exception as e:
        log("cleanup " + str(e))

    log("DONE")
    flush()


main()
