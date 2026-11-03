# -*- coding: utf-8 -*-
"""Probe GI_DungeonGame + BlueprintEditorLibrary for adding Gold/Inventory."""
from __future__ import print_function
import unreal
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_gi_meta.txt"
GI_PATH = "/Game/Core/GameFlow/GI_DungeonGame"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("ProbeGI: " + str(m))
    except Exception:
        print(m)

def main():
    log("BEGIN")
    exists = unreal.EditorAssetLibrary.does_asset_exist(GI_PATH)
    log("exists=%s" % exists)
    bp = unreal.EditorAssetLibrary.load_asset(GI_PATH)
    log("bp=%s type=%s" % (bp, type(bp).__name__ if bp else None))
    # BlueprintEditorLibrary attrs
    bel = getattr(unreal, "BlueprintEditorLibrary", None)
    log("BlueprintEditorLibrary=%s" % bel)
    if bel:
        names = [n for n in dir(bel) if ("var" in n.lower() or "member" in n.lower() or "add" in n.lower() or "compile" in n.lower())]
        log("BEL interesting=%s" % names)
    # Class / CDO
    cls = None
    try:
        cls = unreal.EditorAssetLibrary.load_blueprint_class(GI_PATH)
    except Exception as e:
        log("load_blueprint_class %s" % e)
    if cls is None and bp is not None:
        for attr in ("generated_class", "GeneratedClass"):
            try:
                cls = bp.get_editor_property(attr)
                log("bp.%s=%s" % (attr, cls))
            except Exception as e:
                log("bp.%s ERR %s" % (attr, e))
        try:
            cls = bp.generated_class()
            log("bp.generated_class()=%s" % cls)
        except Exception as e:
            log("generated_class() %s" % e)
    log("cls=%s" % cls)
    cdo = unreal.get_default_object(cls) if cls else None
    log("cdo=%s" % cdo)
    if cdo:
        for name in ("Gold", "gold", "Inventory", "inventory", "CurrentState", "Coins", "Money"):
            try:
                v = cdo.get_editor_property(name)
                log("CDO.%s=%s" % (name, v))
            except Exception as e:
                log("CDO.%s missing (%s)" % (name, e))
    # Live GI if PIE
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        log("editor_world=%s" % (world.get_path_name() if world else None))
        pie = None
        try:
            pie_worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
            log("pie_worlds=%s" % pie_worlds)
            if pie_worlds:
                pie = pie_worlds[0]
        except Exception as e:
            log("get_pie_worlds %s" % e)
        w = pie or world
        if w:
            gi = unreal.GameplayStatics.get_game_instance(w)
            log("live_gi=%s class=%s" % (gi, gi.get_class().get_name() if gi else None))
            if gi:
                for name in ("Gold", "gold", "Inventory", "inventory", "CurrentState"):
                    try:
                        v = gi.get_editor_property(name)
                        log("live.%s=%s" % (name, v))
                    except Exception as e:
                        log("live.%s missing (%s)" % (name, e))
    except Exception as e:
        log("live probe %s" % e)
    # Project setting echo
    try:
        # soft: read from config via unreal
        log("GI asset path confirmed " + GI_PATH)
    except Exception:
        pass
    # Try create_asset duplicate name GI_DungeonEscape? skip if GI_DungeonGame exists
    log("DONE")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("WROTE", OUT)

main()
