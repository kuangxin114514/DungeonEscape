# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

# BlendSpace factory props
factory = unreal.BlendSpaceFactory1D()
unreal.log("factory dir skeletonish: " + ",".join([x for x in dir(factory) if "kel" in x.lower() or "targ" in x.lower() or "preview" in x.lower()]))
for name in ["TargetSkeleton","target_skeleton","Skeleton","skeleton","PreviewSkeleton","preview_skeleton","SupportedSkeleton"]:
    try:
        setattr(factory, name, skel)
        unreal.log("setattr {} OK".format(name))
    except Exception as e:
        unreal.log("setattr {} ERR {}".format(name, e))
    try:
        factory.set_editor_property(name, skel)
        unreal.log("set_editor_property {} OK".format(name))
    except Exception as e:
        unreal.log("set_editor_property {} ERR {}".format(name, e))

# Create BS via AnimBlueprint-like: use BlendSpaceFactoryNew?
for fname in ["BlendSpaceFactory1D","BlendSpaceFactoryNew"]:
    fcls = getattr(unreal, fname)
    f = fcls()
    unreal.log("{} attrs: {}".format(fname, ",".join([a for a in dir(f) if not a.startswith("_")][:40])))

# Graph node creation probe
EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
AnimGraphNode_Root = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Root")
AnimGraphNode_SequencePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe")
anim_graph = None
for obj in unreal.ObjectIterator(EdGraph):
    if obj.get_name() == "AnimGraph" and obj.get_outer() == abp:
        anim_graph = obj
        break
unreal.log("anim_graph={}".format(anim_graph))

root = None
for obj in unreal.ObjectIterator(AnimGraphNode_Root):
    if abp.get_name() in obj.get_path_name():
        root = obj
        break
unreal.log("root={}".format(root))

# Inspect root pins / node
if root:
    for p in ["node_pos_x","node_pos_y","pins","node"]:
        try:
            unreal.log("root.{}={}".format(p, root.get_editor_property(p)))
        except Exception as e:
            unreal.log("root.{} ERR {}".format(p, e))
    methods = [m for m in dir(root) if "pin" in m.lower() or "schema" in m.lower() or "allocate" in m.lower()]
    unreal.log("root methods pinish: "+",".join(methods))

# EdGraph methods
if anim_graph:
    methods = [m for m in dir(anim_graph) if not m.startswith("_")]
    unreal.log("graph methods: "+",".join(methods[:60]))
    for p in ["nodes","schema","graph_guid"]:
        try:
            unreal.log("graph.{}={}".format(p, anim_graph.get_editor_property(p)))
        except Exception as e:
            unreal.log("graph.{} ERR {}".format(p, e))

# Try new_object SequencePlayer outer=anim_graph
if anim_graph:
    try:
        node = unreal.new_object(AnimGraphNode_SequencePlayer, anim_graph)
        unreal.log("new sequence player={}".format(node))
        # set sequence
        for p in ["node","Node","sequence","Sequence"]:
            try:
                unreal.log("sp.{}={}".format(p, node.get_editor_property(p)))
            except Exception as e:
                unreal.log("sp.{} ERR {}".format(p, e))
        # try set sequence on AnimNode_SequencePlayer inside
        try:
            n = node.get_editor_property("node")
            unreal.log("inner node type {} dir sample {}".format(type(n), [x for x in dir(n) if "seq" in x.lower() or "anim" in x.lower()][:30]))
            try:
                n.set_editor_property("sequence", idle)
                unreal.log("set sequence via set_editor_property OK")
            except Exception as e:
                unreal.log("set sequence err {}".format(e))
            try:
                n.sequence = idle
                unreal.log("set sequence attr OK")
            except Exception as e:
                unreal.log("set sequence attr err {}".format(e))
        except Exception as e:
            unreal.log("inner node err {}".format(e))
    except Exception as e:
        unreal.log("new_object err {}".format(e))

unreal.log("PROBE5_DONE")