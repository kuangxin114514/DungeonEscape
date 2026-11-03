# -*- coding: utf-8 -*-
import unreal

candidates = [
    "/Script/AnimGraph.AnimGraphNode_SequencePlayer",
    "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer",
    "/Script/AnimGraph.AnimGraphNode_Root",
    "/Script/AnimGraph.AnimGraphNode_StateMachine",
    "/Script/AnimGraph.AnimGraphNode_TransitionResult",
    "/Script/BlueprintGraph.K2Node_Event",
    "/Script/BlueprintGraph.K2Node_VariableSet",
    "/Script/BlueprintGraph.K2Node_VariableGet",
    "/Script/BlueprintGraph.K2Node_CallFunction",
]
for p in candidates:
    try:
        c = unreal.load_class(None, p)
        unreal.log("LOAD {} -> {}".format(p, c))
    except Exception as e:
        unreal.log("LOAD {} ERR {}".format(p, e))

# Blueprint structure
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
props = []
for name in ["ubergraph_pages","function_graphs","macro_graphs","delegate_signature_graphs","event_graphs","new_variables","skeleton","parent_class","simple_construction_script","blueprint_system_version"]:
    try:
        v = bp.get_editor_property(name)
        unreal.log("BPprop {} = {} type={}".format(name, v, type(v)))
    except Exception as e:
        unreal.log("BPprop {} ERR {}".format(name, e))

# try create tiny abp to inspect
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
factory = unreal.AnimBlueprintFactory()
factory.set_editor_property("target_skeleton", skel)
factory.set_editor_property("parent_class", unreal.AnimInstance)
tools = unreal.AssetToolsHelpers.get_asset_tools()
path = "/Game/Characters/Player/KayKit/Animations"
if not unreal.EditorAssetLibrary.does_directory_exist(path):
    unreal.EditorAssetLibrary.make_directory(path)
existing = path + "/ABP_KayKitKnight_Probe"
if unreal.EditorAssetLibrary.does_asset_exist(existing):
    unreal.EditorAssetLibrary.delete_asset(existing)
abp = tools.create_asset("ABP_KayKitKnight_Probe", path, unreal.AnimBlueprint, factory)
unreal.log("created abp {}".format(abp))
if abp:
    for name in ["ubergraph_pages","function_graphs","anim_blueprint_functions","target_skeleton","parent_class"]:
        try:
            v = abp.get_editor_property(name)
            unreal.log("ABPprop {} = {}".format(name, v))
        except Exception as e:
            unreal.log("ABPprop {} ERR {}".format(name, e))
    # list all editor props that look like graphs
    try:
        # dump dir of object
        unreal.log("ABP class="+abp.get_class().get_name())
    except Exception as e:
        unreal.log(str(e))

unreal.log("PROBE3_DONE")