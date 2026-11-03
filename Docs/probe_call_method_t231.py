# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_call_method_t231.txt"
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
    L("root=%s" % root)
    L("slot=%s" % slot)
    L("sm=%s" % sm)

    # Try call_method with common UFUNCTIONS
    for label, node in (("root", root), ("slot", slot), ("sm", sm)):
        if not node: continue
        for meth in (
            "AllocateDefaultPins", "ReconstructNode", "CreateNewGuid",
            "GetPin", "FindPin", "GetAllPins", "AutowireNewNode",
            "PinConnectionListChanged", "PostEditChange",
        ):
            try:
                r = node.call_method(meth)
                L("%s.call_method(%s) -> %s" % (label, meth, r))
            except Exception as e:
                L("%s.call_method(%s) ERR %s" % (label, meth, e))
        # After allocate, try get pins again
        try:
            pins = node.get_editor_property("pins")
            L("%s pins=%s" % (label, pins))
        except Exception as e:
            L("%s pins still ERR %s" % (label, e))
        # Try get_editor_property with different cases
        for prop in ("Pins", "pins", "Node", "node"):
            try:
                v=node.get_editor_property(prop)
                L("%s.%s type=%s" % (label, prop, type(v).__name__))
                if prop.lower()=="node":
                    # dump pose links on FAnimNode_Root / Slot
                    for pp in dir(v):
                        if pp.startswith("_"): continue
                    for pp in ("result", "Result", "source", "Source", "slot_name", "SlotName",
                               "pose", "Pose", "blend_poses", "BlendPoses", "base_pose", "BasePose"):
                        try:
                            L("  node.%s=%s" % (pp, v.get_editor_property(pp)))
                        except Exception as e:
                            pass
            except Exception as e:
                L("%s.%s ERR %s" % (label, prop, e))

    # Graph call_method AddNode?
    EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
    graph=None
    for g in unreal.ObjectIterator(EdGraph):
        if g.get_path_name().endswith("ABP_KayKitLocomotion:AnimGraph"):
            graph=g; break
    L("graph=%s" % graph)
    if graph:
        for meth in ("AddNode", "RemoveNode", "GetSchema", "NotifyGraphChanged", "CreateIntermediateNode"):
            try:
                r=graph.call_method(meth)
                L("graph.call_method(%s)->%s" % (meth, r))
            except Exception as e:
                L("graph.call_method(%s) ERR %s" % (meth, e))
        # AddNode with args?
        if slot:
            try:
                r=graph.call_method("AddNode", (slot, False, False))
                L("AddNode(slot) -> %s" % r)
            except Exception as e:
                L("AddNode(slot) ERR %s" % e)
            try:
                r=graph.call_method("AddNode", slot)
                L("AddNode(slot single) -> %s" % r)
            except Exception as e:
                L("AddNode(slot single) ERR %s" % e)

    # Inner FAnimNode pose link fields on Root
    if root:
        try:
            n=root.get_editor_property("node")
            L("root.inner=%s" % n)
            # FPoseLink fields
            try:
                result=n.get_editor_property("result")
                L("root.result=%s type=%s" % (result, type(result)))
                if result is not None:
                    for pp in ("link_id", "LinkID", "source_link_id", "SourceLinkID", "pose_link", "Link"):
                        try:
                            L("  result.%s=%s" % (pp, result.get_editor_property(pp)))
                        except Exception as e:
                            L("  result.%s ERR %s" % (pp, e))
                    L("  result dir non_=%s" % [x for x in dir(result) if not x.startswith("_")])
            except Exception as e:
                L("root.result ERR %s" % e)
        except Exception as e:
            L("root.node ERR %s" % e)

    if slot:
        try:
            n=slot.get_editor_property("node")
            L("slot.inner=%s" % n)
            for pp in ("slot_name","SlotName","source","Source","result","Result"):
                try:
                    L("  slot.%s=%s" % (pp, n.get_editor_property(pp)))
                except Exception as e:
                    L("  slot.%s ERR %s" % (pp, e))
        except Exception as e:
            L("slot.node ERR %s" % e)

    flush(); print("WROTE", OUT)
main()
