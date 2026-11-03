# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_pin_api_t231.txt"
lines=[]
def L(m): lines.append(str(m))
def flush(): open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

def main():
    L("=== pin api ===")
    # Any Slot anywhere?
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    slots=[]
    for obj in unreal.ObjectIterator(EdGraphNode):
        cn=obj.get_class().get_name()
        if cn=="AnimGraphNode_Slot":
            slots.append(obj.get_path_name())
    L("all_slots_in_memory=%d" % len(slots))
    for s in slots[:20]:
        L("  "+s)

    # Graph methods
    EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
    graph=None
    for g in unreal.ObjectIterator(EdGraph):
        if g.get_path_name().endswith("ABP_KayKitLocomotion:AnimGraph"):
            graph=g; break
    L("graph="+str(graph))
    if graph:
        meths=[x for x in dir(graph) if any(k in x.lower() for k in ("node","pin","add","link","schema","notify"))]
        L("graph_meths="+str(meths[:60]))
        for prop in ("nodes","Nodes","schema","Schema"):
            try:
                v=graph.get_editor_property(prop)
                L("graph.%s=%s" % (prop, str(v)[:200]))
            except Exception as e:
                L("graph.%s ERR %s" % (prop,e))

    # Blueprint helpers
    for name in ("KismetEditorUtilities","BlueprintEditorLibrary","AnimationLibrary","EditorAssetLibrary"):
        if hasattr(unreal,name):
            cls=getattr(unreal,name)
            attrs=[x for x in dir(cls) if any(k in x.lower() for k in ("compile","node","graph","anim","add","pin"))]
            L("%s attrs=%s" % (name, attrs[:40]))

    # Try duplicate a SequencePlayer node as template for pin structure? 
    # Find SequencePlayer in AnimGraph top level — none; find Root pins
    root=None
    for obj in unreal.ObjectIterator(EdGraphNode):
        if "ABP_KayKitLocomotion:AnimGraph.AnimGraphNode_Root" in obj.get_path_name():
            root=obj; break
    L("root="+str(root))
    if root:
        L("root dir sample="+str([x for x in dir(root) if not x.startswith("_")][:50]))
        try:
            pins=root.get_editor_property("pins")
            L("root pins=%d" % (len(pins) if pins else 0))
            if pins:
                p0=pins[0]
                L("pin0 dir="+str([x for x in dir(p0) if not x.startswith("_")][:40]))
                for meth in ("make_link_to","break_link_to","break_all_pin_links","get_owning_node"):
                    L("pin has %s=%s" % (meth, hasattr(p0,meth)))
        except Exception as e:
            L("root pins "+str(e))

    # Try: duplicate Root? useless. Create Slot and call get_schema from pin
    SlotCls=unreal.load_class(None,"/Script/AnimGraph.AnimGraphNode_Slot")
    # Find existing orphan slot
    slot=None
    for obj in unreal.ObjectIterator(EdGraphNode):
        if obj.get_class().get_name()=="AnimGraphNode_Slot" and "ABP_KayKitLocomotion" in obj.get_path_name():
            slot=obj; break
    if slot is None and graph:
        slot=unreal.new_object(SlotCls, outer=graph)
        L("created new slot "+str(slot))
    L("slot="+str(slot))
    if slot:
        L("slot dir="+str([x for x in dir(slot) if not x.startswith("_")][:60]))
        try:
            pins=slot.get_editor_property("pins")
            L("slot pins=%s" % (len(pins) if pins else 0))
        except Exception as e:
            L("slot pins ERR "+str(e))
        # Try notify_add / on_demand
        for meth in ("allocate_default_pins","AllocateDefaultPins","reconstruct_node","ReconstructNode",
                     "create_new_guid","CreateNewGuid","prepare_for_copying","post_paste_node",
                     "autowire_new_node","AutowireNewNode","node_connection_list_changed"):
            L("slot hasattr %s=%s" % (meth, hasattr(slot,meth)))

    # Schema CDO methods
    for sp in ("/Script/AnimGraph.AnimationGraphSchema","/Script/BlueprintGraph.EdGraphSchema_K2","/Script/Engine.EdGraphSchema"):
        sc=unreal.load_class(None,sp)
        L("schema %s=%s" % (sp,sc))
        if sc:
            try:
                cdo=unreal.get_default_object(sc)
                attrs=[x for x in dir(cdo) if any(k in x.lower() for k in ("connect","link","create","node","pin","break"))]
                L("  cdo attrs="+str(attrs[:50]))
            except Exception as e:
                L("  cdo "+str(e))

    # Can we use duplicate_object on Root to get a node with pins, then change class? No.
    # Try unreal.SystemLibrary.execute_console_command to run editor cmd
    L("=== done ===")
    flush(); print("WROTE", OUT)
main()
