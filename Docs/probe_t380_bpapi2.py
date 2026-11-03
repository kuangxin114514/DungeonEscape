# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t380_bpapi2.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T380API: "+str(m))
    except Exception: print(m)

# Find ways to mutate graphs / create BT / AI helpers
for path in [
 "/Script/BlueprintEditorLibrary.BlueprintEditorLibrary",
 "/Script/Blutility.EditorUtilityLibrary",
 "/Script/AIModule.AIBlueprintHelperLibrary",
 "/Script/AIModule.AIHelpers",
 "/Script/NavigationSystem.NavigationSystemV1",
 "/Script/AIModule.BehaviorTree",
 "/Script/AIModule.BlackboardData",
 "/Script/AIModule.BehaviorTreeFactory",
 "/Script/AIModule.BlackboardDataFactory",
 "/Script/AnimGraph.AnimationBlueprintLibrary",
 "/Script/AnimationBlueprintLibrary.AnimationBlueprintLibrary",
]:
    o=None
    try: o=unreal.load_object(None, path)
    except Exception: o=None
    if o is None:
        try: o=unreal.load_class(None, path)
        except Exception: o=None
    L("load %s -> %s"%(path,o))

# unreal attrs
for n in sorted(dir(unreal)):
    if any(k in n.lower() for k in ("behavior", "blackboard", "blueprinteditor", "animgraph", "aiblueprint", "navmesh", "navigat", "kismet")):
        L("dir "+n)

# BehaviorTree factory create?
try:
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    L("AssetTools ok")
except Exception as e:
    L("AssetTools "+str(e))

# Inspect BP_Enemy_Skeleton via registry package name
pkg="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bp=unreal.load_asset(pkg)
L("load_asset bp="+str(bp))
if bp is None:
    bp=unreal.EditorAssetLibrary.load_asset(pkg)
    L("EAL load bp="+str(bp))
if bp:
    for n in ("generated_class","GeneratedClass","parent_class","ParentClass","simple_construction_script","SimpleConstructionScript","ubergraph_pages","UbergraphPages","status","Status"):
        try:
            L("bp.%s=%s"%(n, bp.get_editor_property(n)))
        except Exception as e:
            L("bp.%s ERR %s"%(n,e))
    # children
    kids=[]
    for o in unreal.ObjectIterator(unreal.Object):
        try:
            if o.get_outer()==bp:
                kids.append((o.get_name(), o.get_class().get_name()))
        except Exception:
            pass
    L("children n="+str(len(kids)))
    for name,cn in kids[:40]:
        L(" child %s %s"%(name,cn))

# Can we set CDO props via generated class?
bcls=unreal.EditorAssetLibrary.load_blueprint_class(pkg)
L("bcls="+str(bcls))
if bcls:
    cdo=unreal.get_default_object(bcls)
    L("cdo="+str(cdo))
    try:
        mov=cdo.get_editor_property("character_movement")
        L("mov="+str(mov))
        mov.set_editor_property("orient_rotation_to_movement", True)
        mov.set_editor_property("max_walk_speed", 190.0)
        L("mov set ok ortm=%s speed=%s"%(mov.get_editor_property("orient_rotation_to_movement"), mov.get_editor_property("max_walk_speed")))
    except Exception as e:
        L("mov set ERR "+traceback.format_exc())
    try:
        cdo.set_editor_property("use_controller_rotation_yaw", False)
        L("use_controller_rotation_yaw False ok")
    except Exception as e:
        L("ucry ERR "+str(e))
    try:
        # Auto possess
        cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        L("auto_possess ok")
    except Exception as e:
        L("auto_possess ERR "+str(e))
    try:
        cdo.set_editor_property("ai_controller_class", unreal.AIController)
        L("ai_controller_class set native AIController")
    except Exception as e:
        L("aiclass ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
