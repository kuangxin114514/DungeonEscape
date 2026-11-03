# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

# Create BlendSpace1D without factory skeleton, set after
path = "/Game/Characters/Player/KayKit/Animations"
bs_name = "BS_KayKitLocomotion"
bs_path = path + "/" + bs_name
if unreal.EditorAssetLibrary.does_asset_exist(bs_path):
    unreal.EditorAssetLibrary.delete_asset(bs_path)
factory = unreal.BlendSpaceFactory1D()
tools = unreal.AssetToolsHelpers.get_asset_tools()
try:
    bs = tools.create_asset(bs_name, path, unreal.BlendSpace1D, factory)
    unreal.log("bs created {}".format(bs))
except Exception as e:
    unreal.log("bs create err {}".format(e))
    bs = None

if bs:
    for pname in ["skeleton","Skeleton","preview_base_pose","blend_parameters","sample_data"]:
        try:
            unreal.log("bs.{} = {}".format(pname, bs.get_editor_property(pname)))
        except Exception as e:
            unreal.log("bs.{} ERR {}".format(pname, e))
    try:
        bs.set_editor_property("skeleton", skel)
        unreal.log("set skeleton OK")
    except Exception as e:
        unreal.log("set skeleton ERR {}".format(e))

    # try add samples via sample_data array
    try:
        # BlendSample struct
        samples = []
        for anim, x in [(idle, 0.0), (walk, 200.0), (run, 400.0)]:
            s = unreal.BlendSample()
            try:
                s.set_editor_property("animation", anim)
            except Exception as e:
                unreal.log("sample anim err {}".format(e))
            try:
                s.set_editor_property("sample_value", unreal.Vector(x, 0.0, 0.0))
            except Exception as e:
                unreal.log("sample value err {}".format(e))
            samples.append(s)
            unreal.log("prepared sample {}".format(anim.get_name()))
        bs.set_editor_property("sample_data", samples)
        unreal.log("set sample_data OK n={}".format(len(samples)))
    except Exception as e:
        unreal.log("samples ERR {}".format(e))

    # axis config
    try:
        params = bs.get_editor_property("blend_parameters")
        unreal.log("params type={} lenish={}".format(type(params), params))
        # may be array of BlendParameter
        if params and len(params) > 0:
            p0 = params[0]
            for pn in ["display_name","min","max","grid_num"]:
                try:
                    unreal.log("p0.{}={}".format(pn, p0.get_editor_property(pn)))
                except Exception as e:
                    unreal.log("p0.{} ERR {}".format(pn, e))
            try:
                p0.set_editor_property("display_name", "Speed")
                p0.set_editor_property("min", 0.0)
                p0.set_editor_property("max", 400.0)
                p0.set_editor_property("grid_num", 4)
                params[0] = p0
                bs.set_editor_property("blend_parameters", params)
                unreal.log("axis configured")
            except Exception as e:
                unreal.log("axis set ERR {}".format(e))
    except Exception as e:
        unreal.log("params ERR {}".format(e))

    unreal.EditorAssetLibrary.save_asset(bs_path)
    unreal.log("saved bs")

# Pin / schema probe on existing probe ABP
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe")
EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
AnimGraphNode_Root = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Root")
AnimGraphNode_SequencePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
anim_graph = None
for obj in unreal.ObjectIterator(EdGraph):
    if obj.get_name() == "AnimGraph" and obj.get_outer() == abp:
        anim_graph = obj
        break
root = None
seq = None
for obj in unreal.ObjectIterator(AnimGraphNode_Root):
    if abp.get_name() in obj.get_path_name():
        root = obj
for obj in unreal.ObjectIterator(AnimGraphNode_SequencePlayer):
    if abp.get_name() in obj.get_path_name():
        seq = obj
        break
unreal.log("root={} seq={}".format(root, seq))

for label, node in [("root", root), ("seq", seq)]:
    if not node:
        continue
    for meth in ["get_all_pins","GetAllPins","allocate_default_pins","AllocateDefaultPins","reconstruct_node","ReconstructNode","find_pin","FindPin"]:
        try:
            r = node.call_method(meth)
            unreal.log("{} call {} -> {}".format(label, meth, r))
        except Exception as e:
            unreal.log("{} call {} ERR {}".format(label, meth, e))

# Schema classes
for sp in ["/Script/AnimGraph.AnimationGraphSchema", "/Script/BlueprintGraph.EdGraphSchema_K2", "/Script/Engine.EdGraphSchema"]:
    try:
        c = unreal.load_class(None, sp)
        unreal.log("schema class {} -> {}".format(sp, c))
        if c and anim_graph:
            try:
                schema = unreal.get_default_object(c)
                unreal.log("schema default={}".format(schema))
                meths = [m for m in dir(schema) if "pin" in m.lower() or "creat" in m.lower() or "link" in m.lower() or "connect" in m.lower()]
                unreal.log("schema meths: "+",".join(meths[:40]))
            except Exception as e:
                unreal.log("schema def ERR {}".format(e))
    except Exception as e:
        unreal.log("schema load ERR {}".format(e))

unreal.log("PROBE6_DONE")