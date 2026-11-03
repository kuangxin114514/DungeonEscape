# -*- coding: utf-8 -*-
import unreal

def has(name):
    return hasattr(unreal, name)

checks = [
    "AnimBlueprintFactory","BlendSpaceFactory1D","BlendSpace1D","AnimBlueprint",
    "AnimationBlueprintLibrary","BlueprintEditorLibrary","AssetToolsHelpers",
    "EditorAssetLibrary","AnimGraphNode_BlendSpacePlayer","AnimGraphNode_Root",
    "K2Node","EdGraph","AnimInstance"
]
for c in checks:
    unreal.log("HAS {}: {}".format(c, has(c)))

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")
unreal.log("skel={} idle={} run={} walk={}".format(skel, idle, run, walk))
for a,n in [(idle,"idle"),(run,"run"),(walk,"walk")]:
    try:
        unreal.log("{} class={} len={} skel={}".format(n, a.get_class().get_name(), a.sequence_length, a.get_editor_property("skeleton")))
    except Exception as e:
        unreal.log("{} err {}".format(n, e))

bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.log("bp={}".format(bp))
try:
    cdo = unreal.get_default_object(bp.generated_class())
    mesh = cdo.get_editor_property("mesh")
    unreal.log("mesh={}".format(mesh))
    for prop in ["animation_mode","anim_class","animation_data"]:
        try:
            unreal.log("mesh.{}={}".format(prop, mesh.get_editor_property(prop)))
        except Exception as e:
            unreal.log("mesh.{} err {}".format(prop, e))
except Exception as e:
    unreal.log("cdo err {}".format(e))

try:
    names = [x for x in dir(unreal) if ("Anim" in x or "Blend" in x) and ("Factory" in x or "Graph" in x or "Library" in x or "Node" in x)]
    unreal.log("DIR " + ",".join(names[:100]))
except Exception as e:
    unreal.log("dir err "+str(e))

unreal.log("PROBE_ANIM_DONE")