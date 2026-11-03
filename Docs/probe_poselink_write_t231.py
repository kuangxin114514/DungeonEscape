# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_poselink_write_t231.txt"
lines=[]
def L(m): lines.append(str(m))
def flush(): open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

def main():
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    root=slot=sm=None
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn=obj.get_path_name()
        if "ABP_KayKitLocomotion:AnimGraph." not in pn: continue
        if "StateMachine_1.Default" in pn: continue
        cn=obj.get_class().get_name()
        if cn=="AnimGraphNode_Root": root=obj
        elif cn=="AnimGraphNode_Slot": slot=obj
        elif cn=="AnimGraphNode_StateMachine": sm=obj

    # Try writing LinkID on PoseLinks
    root_node = root.get_editor_property("node")
    result = root_node.get_editor_property("result")
    L("result.to_tuple=%s" % (result.to_tuple(),))
    for prop, val in (("LinkID", 0), ("SourceLinkID", 0), ("link_id", 0), ("source_link_id", 0)):
        try:
            result.set_editor_property(prop, val)
            L("SET result.%s=%s OK" % (prop, val))
        except Exception as e:
            L("SET result.%s ERR %s" % (prop, e))

    # Slot source PoseLink
    slot_node = slot.get_editor_property("node")
    src = slot_node.get_editor_property("source")
    L("slot.source.to_tuple=%s" % (src.to_tuple(),))
    for prop in ("LinkID", "SourceLinkID"):
        try:
            src.set_editor_property(prop, 0)
            L("SET slot.source.%s OK" % prop)
        except Exception as e:
            L("SET slot.source.%s ERR %s" % (prop, e))

    # Try set_editor_properties bulk
    try:
        result.set_editor_properties({"LinkID": 1, "SourceLinkID": 1})
        L("bulk set OK")
    except Exception as e:
        L("bulk set ERR %s" % e)

    # NodeGuid / NodeIndex for pose linking?
    for label, n in (("root", root), ("slot", slot), ("sm", sm)):
        for p in ("node_guid", "NodeGuid", "node_pos_x", "NodePosX", "node_title", "ErrorType"):
            try:
                L("%s.%s=%s" % (label, p, n.get_editor_property(p)))
            except Exception as e:
                pass

    # Try AnimationBlueprintLibrary / AnimBlueprintEditorUtils via load_class
    for path in (
        "/Script/AnimGraph.AnimationBlueprintLibrary",
        "/Script/AnimGraph.AnimBlueprintLibrary",
        "/Script/AnimGraphRuntime.AnimationBlueprintLibrary",
        "/Script/BlueprintGraph.BlueprintEditorLibrary",
        "/Script/UnrealEd.BlueprintEditorLibrary",
        "/Script/AnimGraph.AnimGraphNode_Base",
    ):
        c = unreal.load_class(None, path)
        L("class %s -> %s" % (path, c))

    # Try unreal.AnimationBlueprintLibrary if exists
    for name in ("AnimationBlueprintLibrary", "AnimBlueprintFunctionLibrary", "BlueprintEditorLibrary",
                 "EdGraphSchema_K2", "AnimationGraphSchema"):
        try:
            obj = getattr(unreal, name)
            L("unreal.%s = %s" % (name, obj))
            meths = [x for x in dir(obj) if not x.startswith("_")]
            L("  methods sample: %s" % meths[:40])
        except Exception as e:
            L("unreal.%s ERR %s" % (name, e))

    flush(); print("WROTE", OUT)
main()
