# -*- coding: utf-8 -*-
import unreal

def dump(name):
    cls = getattr(unreal, name, None)
    if cls is None:
        unreal.log("{} MISSING".format(name))
        return
    unreal.log("=== {} ===".format(name))
    try:
        obj = cls()
    except Exception:
        try:
            obj = cls.get_default_object() if hasattr(cls, "get_default_object") else cls
        except Exception as e:
            unreal.log("cannot instance {}: {}".format(name, e))
            obj = cls
    methods = [m for m in dir(obj) if not m.startswith("_")]
    unreal.log("methods: {}".format(methods))

dump("AnimGraphLibrary")
dump("AnimationLibrary")
dump("AnimSequenceFactory")

# Can AnimSequenceFactory set skeleton?
try:
    f = unreal.AnimSequenceFactory()
    skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
    for prop in ["TargetSkeleton","target_skeleton","Skeleton","skeleton","PreviewSkeletalMesh","preview_skeletal_mesh"]:
        try:
            f.set_editor_property(prop, skel)
            unreal.log("AnimSequenceFactory.{} SET OK".format(prop))
        except Exception as e:
            unreal.log("AnimSequenceFactory.{} ERR {}".format(prop, e))
except Exception as e:
    unreal.log("ASF err {}".format(e))

# Try AnimationLibrary static methods via unreal.AnimationLibrary.
al = unreal.AnimationLibrary
unreal.log("AL dir: {}".format([m for m in dir(al) if not m.startswith("_")]))

agl = unreal.AnimGraphLibrary
unreal.log("AGL dir: {}".format([m for m in dir(agl) if not m.startswith("_")]))

# Check if we can use LinkedAnimGraph / PostProcess
# Try loading AnimGraphNode_SequencePlayer via unreal.AnimGraphNode_AssetPlayerBase

# Inspect EdGraphSchema via load_class and new_object
Schema = unreal.load_class(None, "/Script/BlueprintGraph.EdGraphSchema_K2")
unreal.log("Schema={}".format(Schema))
if Schema:
    schema = unreal.get_default_object(Schema)
    unreal.log("schema methods: {}".format([m for m in dir(schema) if not m.startswith("_")]))
    for m in ["try_create_connection","TryCreateConnection","create_connection","can_create_connection","make_link"]:
        if hasattr(schema, m):
            unreal.log("schema HAS {}".format(m))

AnimSchema = unreal.load_class(None, "/Script/AnimGraph.AnimationGraphSchema")
unreal.log("AnimSchema={}".format(AnimSchema))
if AnimSchema:
    asch = unreal.get_default_object(AnimSchema)
    unreal.log("animschema methods: {}".format([m for m in dir(asch) if not m.startswith("_")]))

# EdGraphPin?
Pin = unreal.load_class(None, "/Script/Engine.EdGraphPin")
unreal.log("Pin class={}".format(Pin))

# Try get pins via call_method on root node
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
root = None
seq = None
for obj in unreal.ObjectIterator(EdGraphNode):
    p = obj.get_path_name()
    if "ABP_KayKitKnight" in p and "AnimGraph" in p and "Probe" not in p:
        cn = obj.get_class().get_name()
        if cn == "AnimGraphNode_Root":
            root = obj
        if cn == "AnimGraphNode_SequencePlayer":
            seq = obj
unreal.log("root={} seq={}".format(root, seq))
if root:
    for m in ["GetPins","get_pins","Pins","AllocateDefaultPins","GetPinNames"]:
        try:
            r = root.call_method(m)
            unreal.log("root.call_method({})={}".format(m, r))
        except Exception as e:
            unreal.log("root.call_method({}) ERR {}".format(m, e))
    # editor properties dump
    try:
        # Some nodes expose Pins as array through get_editor_property - unlikely
        pass
    except Exception:
        pass

# BlendSpace: try creating with AssetImportTask / Intermediate format
# Or use duplicate of existing BlendSpace and replace sample animations + skeleton via AnimationLibrary

bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
if not bs:
    # try create path from earlier probe
    paths = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", True, False)
    unreal.log("anim folder assets: {}".format(paths))
else:
    unreal.log("bs skel={}".format(bs.get_editor_property("skeleton") if hasattr(bs,"get_editor_property") else "?"))
    try:
        unreal.log("bs skeleton={}".format(bs.get_editor_property("skeleton")))
    except Exception as e:
        unreal.log("bs skel ERR {}".format(e))

# AnimationLibrary - get_animation_curves etc. Check for blend space helpers
for m in dir(unreal.AnimationLibrary):
    if not m.startswith("_"):
        unreal.log("AL.{}".format(m))

unreal.log("PROBE13_DONE")