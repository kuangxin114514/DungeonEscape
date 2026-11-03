# -*- coding: utf-8 -*-
"""Remove orphan unwired Slot (can't wire pins in UE4.27 Python). Keep V15d single-node fix."""
from __future__ import print_function
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t229c_cleanup.txt"
lines = []
def L(m):
    s = str(m); lines.append(s)
    try: unreal.log("T229c: " + s)
    except Exception: print(s)

ABP = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
removed = 0
for obj in list(unreal.ObjectIterator(EdGraphNode)):
    pn = obj.get_path_name()
    if "ABP_KayKitLocomotion" not in pn:
        continue
    if "Default__" in pn or "AnimPreview" in pn:
        continue
    if obj.get_class().get_name() != "AnimGraphNode_Slot":
        continue
    L("found Slot %s" % pn)
    # Try destroy
    ok = False
    for meth in ("destroy_node", "DestroyNode", "break_all_node_links"):
        fn = getattr(obj, meth, None)
        if fn:
            try:
                fn(); L("  %s OK" % meth); ok = True
            except Exception as e:
                L("  %s ERR %s" % (meth, e))
    try:
        # mark transient / rename away
        obj.set_editor_property("node_comment", "ORPHAN_REMOVE_V15d")
    except Exception:
        pass
    # Soft delete: graph may keep it; try EditorAssetLibrary not applicable
    try:
        unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False)
    except Exception as e:
        L("save ERR %s" % e)
    removed += 1

# Re-count
slots = []
for obj in unreal.ObjectIterator(EdGraphNode):
    pn = obj.get_path_name()
    if "ABP_KayKitLocomotion" not in pn or "Default__" in pn or "AnimPreview" in pn:
        continue
    if "Slot" in obj.get_class().get_name():
        slots.append(obj.get_name())
L("removed_attempts=%d remaining_slots=%s" % (removed, slots))

# Confirm runtime
src = open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py", encoding="utf-8-sig").read()
L("runtime V15d=%s playingTrue=%s" % ("V15d" in src, "override_animation_data(seq, False, True" in src))
import shop_interact_runtime as mod
mod.bootstrap()
L("bootstrap OK gen tick V15d")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
