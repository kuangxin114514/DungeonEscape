# -*- coding: utf-8 -*-
"""Attach test WidgetComponent to current pawn to verify API, then remove."""
from __future__ import print_function
import unreal
import os
import sys
import importlib
import traceback

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "probe_wc_api.txt")
lines = []


def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("PROBEWCAPI: " + s)
    except Exception:
        print(s)


def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    log("=== probe WC API on pawn ===")
    pydir = os.path.join(ROOT, "Content", "Python")
    if pydir not in sys.path:
        sys.path.insert(0, pydir)
    import shop_interact_runtime as r
    importlib.reload(r)
    r.bootstrap()

    world = r._pie_world()
    log("world=" + (world.get_path_name() if world else "None"))
    if not world:
        flush(); return
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    log("pawn=" + str(pawn))
    if not pawn:
        flush(); return

    widget, pb, wpath = r._make_enemy_widget(world, pc)
    log("widget=%s pb=%s path=%s" % (widget, pb, wpath))
    if widget:
        r._fit_enemy_bar_layout(widget, pb)
        try:
            slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(pb) if pb else None
            if slot:
                log("anchors=%s" % slot.get_anchors())
                log("offsets=%s" % slot.get_offsets())
                try:
                    log("size=%s pos=%s" % (slot.get_size(), slot.get_position()))
                except Exception as e:
                    log("size/pos " + str(e))
        except Exception as e:
            log("slot " + str(e))

    # Try add_component_by_class directly
    wc1 = None
    try:
        xf = unreal.Transform()
        try:
            xf.translation = unreal.Vector(0, 0, 130)
        except Exception:
            pass
        wc1 = pawn.add_component_by_class(unreal.WidgetComponent, False, xf, False)
        log("add_component_by_class -> " + str(wc1))
    except Exception as e:
        log("add_component_by_class " + str(e))
        log(traceback.format_exc())

    wc2 = None
    try:
        wc2 = unreal.new_object(unreal.WidgetComponent, pawn, "EnemyHealthBarProbe")
        log("new_object -> " + str(wc2))
        try:
            root = pawn.get_editor_property("root_component")
        except Exception:
            root = pawn.root_component
        log("root=" + str(root))
        if root and wc2:
            try:
                wc2.attach_to_component(root, unreal.AttachmentTransformRules.KEEP_RELATIVE_TRANSFORM, "")
                log("attach ok")
            except Exception as e:
                log("attach " + str(e))
            try:
                wc2.register_component()
                log("register ok")
            except Exception as e:
                log("register " + str(e))
    except Exception as e:
        log("new_object path " + str(e))
        log(traceback.format_exc())

    wc = wc1 or wc2
    if wc and widget:
        try:
            wc.set_relative_location(unreal.Vector(0, 0, 130), False, False)
            log("set_rel ok")
        except Exception as e:
            log("set_rel " + str(e))
        try:
            wc.set_draw_size(unreal.Vector2D(180, 22))
            log("draw_size ok")
        except Exception as e:
            log("draw_size " + str(e))
        try:
            wc.set_widget_space(unreal.WidgetSpace.SCREEN)
            log("space SCREEN ok")
        except Exception as e:
            log("space " + str(e))
            try:
                wc.set_editor_property("space", unreal.WidgetSpace.SCREEN)
                log("space prop ok")
            except Exception as e2:
                log("space prop " + str(e2))
        try:
            wc.set_pivot(unreal.Vector2D(0.5, 1.0))
        except Exception:
            pass
        try:
            wc.set_widget(widget)
            log("set_widget ok")
        except Exception as e:
            log("set_widget " + str(e))
        try:
            log("user_widget=" + str(wc.get_user_widget_object()))
        except Exception as e:
            log("user_widget " + str(e))
        try:
            log("rel=" + str(wc.get_relative_location()))
        except Exception as e:
            log("rel " + str(e))
        try:
            log("world=" + str(wc.get_world_location()))
        except Exception:
            try:
                log("comp_loc=" + str(wc.get_component_location()))
            except Exception as e:
                log("loc " + str(e))
        for prop in ("space", "draw_size", "pivot"):
            try:
                log("%s=%s" % (prop, wc.get_editor_property(prop)))
            except Exception as e:
                log("%s err %s" % (prop, e))

    # Also test helper
    wc3 = r._attach_widget_component(pawn, widget)
    log("helper_wc=" + str(wc3))

    # Cleanup all probe WCs on pawn so we don't leave a bar on the knight
    try:
        for c in list(pawn.get_components_by_class(unreal.WidgetComponent) or []):
            try:
                nm = c.get_name() or ""
            except Exception:
                nm = ""
            log("destroy wc " + nm)
            try:
                c.set_widget(None)
            except Exception:
                pass
            try:
                c.destroy_component(False)
            except Exception as e:
                log("destroy " + str(e))
                try:
                    c.unregister_component()
                except Exception as e2:
                    log("unreg " + str(e2))
    except Exception as e:
        log("cleanup " + str(e))

    if widget:
        try:
            widget.remove_from_parent()
        except Exception:
            pass
    log("DONE")
    flush()


main()
