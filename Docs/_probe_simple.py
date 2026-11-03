# -*- coding: utf-8 -*-
import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_simple.txt"
try:
    open(LOG,"w",encoding="utf-8").write("hello ok world="+str(unreal.EditorLevelLibrary.get_editor_world())+"\n")
    unreal.log("PROBE_SIMPLE_OK")
except Exception:
    open(LOG,"w",encoding="utf-8").write(traceback.format_exc())
