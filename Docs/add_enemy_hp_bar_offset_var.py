# -*- coding: utf-8 -*-
"""T288: try add HealthBarHeightOffset on BP_Enemy_Skeleton; strip orphan WidgetComponents."""
from __future__ import print_function
import unreal
import os

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "add_enemy_hp_bar_offset_var.txt")
BP_PATH = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
VAR_NAME = "HealthBarHeightOffset"
DEFAULT = 40.0
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("T288OFFSET: " + str(m))
    except Exception:
        print(m)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def try_read_write_cdo(cdo):
    # If var already exists, set default
    for name in (VAR_NAME, "HealthBarWorldZOffset", "HealthBarZOffset"):
        try:
            got = cdo.get_editor_property(name)
            log("CDO has %s=%s" % (name, got))
            try:
                cdo.set_editor_property(name, float(DEFAULT))
                log("CDO set %s=%s" % (name, DEFAULT))
            except Exception as e:
                log("CDO set fail %s: %s" % (name, e))
            return True
        except Exception as e:
            log("CDO missing %s (%s)" % (name, e))
    return False

def strip_wc_from_actor(actor):
    n = 0
    try:
        comps = actor.get_components_by_class(unreal.WidgetComponent)
    except Exception:
        comps = []
    for c in list(comps or []):
        try:
            name = c.get_name()
        except Exception:
            name = "?"
        try:
            c.destroy_component(c)
            log("destroyed WC %s on %s" % (name, actor.get_name()))
            n += 1
        except Exception as e:
            try:
                c.destroy_component(True)
                log("destroyed WC2 %s" % name)
                n += 1
            except Exception as e2:
                log("WC destroy fail %s: %s / %s" % (name, e, e2))
    # Also by name
    for nm in ("EnemyHealthBar", "HealthBar", "Widget"):
        try:
            c = actor.get_editor_property(nm) if False else None
        except Exception:
            c = None
        try:
            for c in actor.get_components_by_tag(nm):
                pass
        except Exception:
            pass
    return n

def main():
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    log("bp=" + str(bp))
    gc = None
    try:
        gc = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
    except Exception as e:
        log("load_bp_class " + str(e))
    if gc is None and bp:
        try:
            gc = bp.generated_class()
        except Exception as e:
            log("generated_class " + str(e))
    cdo = unreal.get_default_object(gc) if gc else None
    log("gc=%s cdo=%s" % (gc, cdo))
    has_var = False
    if cdo:
        has_var = try_read_write_cdo(cdo)
    if not has_var:
        log("NOTE: HealthBarHeightOffset not on BP yet (UE4.27 Python cannot safely add NewVariables).")
        log("User knob = Content/Python/shop_interact_runtime.py  ENEMY_HP_BAR_Z_OFFSET")
        log("Optional: manually add float var '%s' (default %s) on BP_Enemy_Skeleton Details." % (VAR_NAME, DEFAULT))

    # Strip leftover WidgetComponents from dungeon placed skeletons only
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        wpath = world.get_path_name() if world else ""
        log("editor world=" + wpath)
        if world and ("Map_Hub" in wpath) and ("Dungeon" not in wpath):
            log("skip WC strip on Map_Hub")
        elif world and gc:
            stripped = 0
            for a in unreal.EditorLevelLibrary.get_all_level_actors():
                try:
                    cn = a.get_class().get_name()
                except Exception:
                    continue
                if "BP_Enemy_Skeleton" not in cn and a.get_class() != gc:
                    continue
                stripped += strip_wc_from_actor(a)
            log("stripped_wc_count=%d" % stripped)
            if "Map_Dungeon" in wpath:
                try:
                    unreal.EditorLevelLibrary.save_current_level()
                    log("saved current dungeon level")
                except Exception as e:
                    log("save level " + str(e))
    except Exception as e:
        log("strip err " + str(e))

    if bp:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            log("compiled bp")
        except Exception as e:
            log("compile " + str(e))
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            log("saved bp")
        except Exception as e:
            log("save bp " + str(e))
    log("OK")
    flush()
    print("WROTE", LOG)

main()
