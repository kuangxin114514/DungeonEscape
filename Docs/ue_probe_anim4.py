# -*- coding: utf-8 -*-
import unreal

EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
AnimGraphNode_Root = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Root")
AnimGraphNode_SequencePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
AnimGraphNode_BlendSpacePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")
unreal.log("classes ok")

abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe")
# iterate graphs owned by abp
count = 0
graphs = []
for obj in unreal.ObjectIterator(EdGraph):
    try:
        outer = obj.get_outer()
        if outer == abp or (outer and abp and str(abp.get_path_name()) in str(obj.get_path_name())):
            graphs.append(obj)
            unreal.log("GRAPH {} outer={} nodes?".format(obj.get_name(), outer.get_name() if outer else None))
            count += 1
    except Exception:
        pass
unreal.log("graph count {}".format(count))

# Also try get_editor_property with different casing via get_editor_property list - use unreal.SystemLibrary
# Inspect root nodes via ObjectIterator of AnimGraphNode_Root
for obj in unreal.ObjectIterator(AnimGraphNode_Root):
    try:
        if abp and str(abp.get_name()) in str(obj.get_path_name()):
            unreal.log("ROOTNODE {} path={}".format(obj.get_name(), obj.get_path_name()))
            # try props
            for p in ["node","Node","pose","Pose"]:
                try:
                    unreal.log("  prop {}={}".format(p, obj.get_editor_property(p)))
                except Exception as e:
                    pass
    except Exception as e:
        pass

# Try creating blend space
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion_Probe"
if unreal.EditorAssetLibrary.does_asset_exist(bs_path):
    unreal.EditorAssetLibrary.delete_asset(bs_path)
factory = unreal.BlendSpaceFactory1D()
factory.set_editor_property("target_skeleton", skel)
tools = unreal.AssetToolsHelpers.get_asset_tools()
bs = tools.create_asset("BS_KayKitLocomotion_Probe", "/Game/Characters/Player/KayKit/Animations", unreal.BlendSpace1D, factory)
unreal.log("bs={}".format(bs))
if bs:
    # inspect methods for adding samples
    meths = [m for m in dir(bs) if "sample" in m.lower() or "blend" in m.lower() or "axis" in m.lower() or "add" in m.lower()]
    unreal.log("bs methods: "+",".join(meths))
    try:
        axes = bs.get_editor_property("blend_parameters")
        unreal.log("blend_parameters={}".format(axes))
    except Exception as e:
        unreal.log("blend_parameters err {}".format(e))
    try:
        samples = bs.get_editor_property("sample_data")
        unreal.log("sample_data={}".format(samples))
    except Exception as e:
        unreal.log("sample_data err {}".format(e))

unreal.log("PROBE4_DONE")