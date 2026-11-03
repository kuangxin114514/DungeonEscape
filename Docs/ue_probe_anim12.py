# -*- coding: utf-8 -*-
import unreal

# Inspect AnimGraph pin APIs and whether we can wire SequencePlayer->Root
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
unreal.log("idle={} run={} walk={}".format(idle, run, walk))

# Ensure Animations folder
folder = "/Game/Characters/Player/KayKit/Animations"
if not unreal.EditorAssetLibrary.does_directory_exist(folder):
    unreal.EditorAssetLibrary.make_directory(folder)

# Create or load ABP
abp_path = folder + "/ABP_KayKitKnight"
if unreal.EditorAssetLibrary.does_asset_exist(abp_path):
    abp = unreal.EditorAssetLibrary.load_asset(abp_path)
    unreal.log("loaded existing ABP")
else:
    factory = unreal.AnimBlueprintFactory()
    factory.set_editor_property("target_skeleton", skel)
    # parent class AnimInstance
    try:
        factory.set_editor_property("parent_class", unreal.AnimInstance)
    except Exception as e:
        unreal.log("parent_class: {}".format(e))
    abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_KayKitKnight", folder, unreal.AnimBlueprint, factory)
    unreal.log("created ABP {}".format(abp))

# Find AnimGraph and nodes
AnimGraph = unreal.load_class(None, "/Script/AnimGraph.AnimationGraph")
AnimGraphNode = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Base")
SeqPlayerCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
RootCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Root")
BlendSpacePlayerCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")

anim_graph = None
for obj in unreal.ObjectIterator(AnimGraph):
    if abp and abp.get_name() in obj.get_path_name() and obj.get_name() == "AnimGraph":
        anim_graph = obj
        unreal.log("found AnimGraph {}".format(obj.get_path_name()))
        break

# List nodes in anim graph
nodes = []
for obj in unreal.ObjectIterator(AnimGraphNode):
    if anim_graph and obj.get_outer() == anim_graph:
        nodes.append(obj)
        unreal.log("AGNODE {} class={}".format(obj.get_name(), obj.get_class().get_name()))

# Also try EdGraphNode methods
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
for obj in unreal.ObjectIterator(EdGraphNode):
    if anim_graph and obj.get_outer() == anim_graph:
        unreal.log("EDNODE {} class={}".format(obj.get_name(), obj.get_class().get_name()))
        # inspect methods once
        if obj.get_class().get_name() == "AnimGraphNode_Root":
            methods = [m for m in dir(obj) if not m.startswith("_")]
            unreal.log("Root methods sample: {}".format(methods[:80]))
            # pins?
            for attr in ["get_pins", "pins", "node_pins", "get_pin", "find_pin", "allocate_default_pins"]:
                if hasattr(obj, attr):
                    unreal.log("HAS {}".format(attr))
                    try:
                        v = getattr(obj, attr)
                        unreal.log("  {} -> {}".format(attr, v() if callable(v) else v))
                    except Exception as e:
                        unreal.log("  {} ERR {}".format(attr, e))

# Try Schema
for name in dir(unreal):
    if "Schema" in name or "EdGraph" in name or "Kismet" in name and "Editor" in name:
        pass
schema_names = [n for n in dir(unreal) if "Schema" in n or n.startswith("EdGraph") or "AnimGraph" in n]
unreal.log("schema-ish: {}".format(schema_names))

# Try BlendSpace: duplicate skeleton to same-length path then binary? First try create_asset_with_dialog is interactive.

# Try setting TargetSkeleton via call_method
factory = unreal.BlendSpaceFactory1D()
for meth in dir(factory):
    if "skel" in meth.lower() or "target" in meth.lower() or "set_" in meth.lower():
        pass
unreal.log("factory dir skel-related: {}".format([m for m in dir(factory) if "skel" in m.lower() or "target" in m.lower() or "Target" in m]))

# Try AnimBlueprintLibrary / AnimationLibrary
libs = [n for n in dir(unreal) if "Anim" in n]
unreal.log("Anim* classes: {}".format(libs))

# Critical: can we set mesh anim_class to ABP even if AnimGraph empty (T-pose)? Then fix graph via UI later.
# First ensure SequencePlayer exists with Running
seq_node = None
root_node = None
for obj in unreal.ObjectIterator(EdGraphNode):
    if anim_graph and obj.get_outer() == anim_graph:
        cn = obj.get_class().get_name()
        if cn == "AnimGraphNode_Root":
            root_node = obj
        if cn == "AnimGraphNode_SequencePlayer":
            seq_node = obj

if anim_graph and SeqPlayerCls and not seq_node:
    seq_node = unreal.new_object(SeqPlayerCls, anim_graph)
    unreal.log("created SequencePlayer {}".format(seq_node))
    
if seq_node and run:
    try:
        # Node has property SequencePlayer with Sequence
        sp = seq_node.get_editor_property("Node")
        unreal.log("Node prop type {} dir {}".format(type(sp), [x for x in dir(sp) if "seq" in x.lower() or "Seq" in x][:20]))
        try:
            sp.set_editor_property("Sequence", run)
            unreal.log("set Sequence to run OK")
        except Exception as e:
            unreal.log("set Sequence ERR {}".format(e))
    except Exception as e:
        unreal.log("Node prop ERR {}".format(e))
        try:
            seq_node.set_editor_property("Sequence", run)
        except Exception as e2:
            unreal.log("direct Sequence ERR {}".format(e2))

# Inspect Root "Result" pin via get_editor_property
if root_node:
    for prop in ["Node", "BoundGraph", "Pins"]:
        try:
            unreal.log("root.{}={}".format(prop, root_node.get_editor_property(prop)))
        except Exception as e:
            unreal.log("root.{} ERR {}".format(prop, e))

unreal.EditorAssetLibrary.save_asset(abp_path)
unreal.log("PROBE12_DONE")