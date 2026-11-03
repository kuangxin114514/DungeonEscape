# -*- coding: utf-8 -*-
import unreal

bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
K2Node = unreal.load_class(None, "/Script/BlueprintGraph.K2Node")

unreal.log("=== graphs in BP_KayKitKnight ===")
for obj in unreal.ObjectIterator(EdGraph):
    try:
        if obj.get_outer() == bp or (bp and bp.get_name() in obj.get_path_name() and "KayKit" in obj.get_path_name()):
            unreal.log("GRAPH {} class={} path={}".format(obj.get_name(), obj.get_class().get_name(), obj.get_path_name()))
    except Exception:
        pass

unreal.log("=== K2 nodes (sample) ===")
count = 0
for obj in unreal.ObjectIterator(K2Node):
    try:
        p = obj.get_path_name()
        if "BP_KayKitKnight" in p:
            unreal.log("NODE {} class={}".format(obj.get_name(), obj.get_class().get_name()))
            count += 1
            if count > 60:
                unreal.log("...")
                break
    except Exception:
        pass
unreal.log("node count listed={}".format(count))

# ThirdPersonCharacter for comparison - does it use AnimBP on mesh?
tp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter")
tp = unreal.get_default_object(tp_cls)
tmesh = tp.get_editor_property("mesh")
unreal.log("TP mode={} anim={}".format(tmesh.get_editor_property("animation_mode"), tmesh.get_editor_property("anim_class")))

# Try create BlendSpace via Skeleton context menu command?
# Execute an editor command
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, "py print('hi')")
    unreal.log("console py OK")
except Exception as e:
    unreal.log("console ERR {}".format(e))

# Try AssetTools.create_asset with BlendSpaceFactory1D after forcing property via ObjectIterator on factory class default
# Inspect all UPROPERTY via unreal.EditorAssetLibrary.find_asset_data

# Another idea: use AnimCompositeFactory - can we set skeleton?
for fname in ["AnimCompositeFactory","AnimMontageFactory","AimOffsetBlendSpaceFactory1D"]:
    f = getattr(unreal, fname)()
    try:
        f.set_editor_property("TargetSkeleton", unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"))
        unreal.log("{} TargetSkeleton settable!".format(fname))
    except Exception as e:
        unreal.log("{} TargetSkeleton ERR {}".format(fname, e))
    try:
        f.set_editor_property("target_skeleton", unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"))
        unreal.log("{} target_skeleton settable!".format(fname))
    except Exception as e:
        unreal.log("{} target_skeleton ERR {}".format(fname, e))

unreal.log("PROBE11_DONE")