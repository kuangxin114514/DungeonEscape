# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_abp_layered_t231c.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def dump_abp(path):
    L("--- " + path + " ---")
    abp = unreal.load_asset(path)
    L("abp=" + str(abp))
    if not abp:
        return
    try:
        L("target_skeleton=" + str(abp.get_editor_property("target_skeleton")))
    except Exception as e:
        L("skel " + str(e))
    tag = path.split("/")[-1]
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    counts = {}
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if tag not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn or "ANIM_PREVIEW" in pn.upper():
            continue
        cn = obj.get_class().get_name()
        counts[cn] = counts.get(cn, 0) + 1
        interesting = any(k in cn for k in ("Slot", "Layered", "Root", "BlendSpace", "StateMachine", "Cached", "Sequence", "BlendList", "Transition", "Result"))
        if interesting or counts[cn] <= 2:
            extra = ""
            try:
                if "Slot" in cn:
                    node = obj.get_editor_property("node")
                    for prop in ("slot_name", "SlotName"):
                        try:
                            extra = " slot=" + str(node.get_editor_property(prop)); break
                        except Exception:
                            pass
                if cn == "AnimGraphNode_BlendSpacePlayer":
                    node = obj.get_editor_property("node")
                    for n in ("blend_space", "BlendSpace", "blend_space_asset"):
                        try:
                            bsa = node.get_editor_property(n)
                            if bsa:
                                extra = " bs=" + bsa.get_name(); break
                        except Exception:
                            pass
                if cn == "AnimGraphNode_SequencePlayer":
                    node = obj.get_editor_property("node")
                    seq = node.get_editor_property("sequence")
                    extra = " seq=" + (seq.get_name() if seq else "None")
                # pins
                try:
                    pins = obj.get_editor_property("pins")
                    pininfo = []
                    for p in (pins or [])[:12]:
                        try:
                            pininfo.append("%s/%s linked=%s" % (
                                p.get_editor_property("direction"),
                                p.get_editor_property("pin_name"),
                                bool(p.get_editor_property("linked_to")),
                            ))
                        except Exception:
                            pass
                    if pininfo:
                        extra += " pins=" + str(pininfo)
                except Exception:
                    pass
            except Exception as e:
                extra = " e=" + str(e)
            L("NODE %s %s%s" % (cn, obj.get_name(), extra))
    L("counts=" + str(sorted(counts.items(), key=lambda x: -x[1])))

def bones():
    L("--- bones ---")
    skm = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
    L("skm=" + str(skm))
    skel = skm.get_editor_property("skeleton")
    L("skel=" + skel.get_path_name())
    names = []
    # try component in editor world via spawn temp
    try:
        loc = unreal.Vector(0, 0, 0)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkeletalMeshActor, loc)
        smc = actor.skeletal_mesh_component
        smc.set_editor_property("skeletal_mesh", skm)
        n = smc.get_num_bones()
        L("spawned actor bones=" + str(n))
        for i in range(int(n)):
            names.append(str(smc.get_bone_name(i)))
        unreal.EditorLevelLibrary.destroy_actor(actor)
    except Exception as e:
        L("spawn bones " + str(e))
    if not names:
        # AnimationLibrary.does_bone_name_exist probe common names
        common = [
            "root", "Root", "pelvis", "Pelvis", "hips", "Hips", "spine", "Spine",
            "spine_01", "spine_02", "spine_03", "Spine1", "Spine2", "Chest", "chest",
            "neck_01", "Neck", "head", "Head", "clavicle_l", "clavicle_r",
            "upperarm_l", "upperarm_r", "thigh_l", "thigh_r", "calf_l", "calf_r",
            "mixamorig:Hips", "mixamorig:Spine", "mixamorig:Spine1", "mixamorig:Spine2",
            "Body", "Torso", "spine.001", "spine.002", "spine.003", "DEF-spine",
            "bip_spine_0", "bip_spine_1", "bip_pelvis", "Bone", "Bone.001",
        ]
        al = unreal.AnimationLibrary
        for bn in common:
            try:
                ok = al.does_bone_name_exist(skel, bn)
                if ok:
                    names.append(bn + "(exists)")
            except Exception as e:
                L("does_bone %s ERR %s" % (bn, e)); break
        L("probe_exists=" + str(names))
    else:
        L("bone_count=%d" % len(names))
        L("bones=" + str(names))
        interesting = [n for n in names if any(k in n.lower() for k in ("spine","chest","pelvis","hip","neck","clav","root","body","torso","thigh","leg"))]
        L("interesting=" + str(interesting))

def bp_info():
    L("--- BP ---")
    # load generated class
    cls = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
    L("cls=" + str(cls))
    if not cls:
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
            L("EAL cls=" + str(cls))
        except Exception as e:
            L("EAL cls ERR " + str(e))
    if cls:
        cdo = unreal.get_default_object(cls)
        mesh = cdo.get_editor_property("mesh")
        L("anim_mode=%s anim_class=%s" % (
            mesh.get_editor_property("animation_mode"),
            mesh.get_editor_property("anim_class"),
        ))

def try_create_nodes():
    L("--- try create slot node ---")
    abp = unreal.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion")
    if not abp:
        L("no abp"); return
    # Find AnimGraph
    graphs = []
    try:
        # Ubergraph / function graphs
        for prop in ("function_graphs", "ubergraph_pages", "delegate_signature_graphs"):
            try:
                v = abp.get_editor_property(prop)
                L("abp.%s count=%s" % (prop, len(v) if v else 0))
                if v:
                    for g in v:
                        graphs.append(g)
                        L("  graph %s" % g.get_name())
            except Exception as e:
                L("abp.%s %s" % (prop, e))
    except Exception as e:
        L("graphs " + str(e))
    # Find via ObjectIterator EdGraph
    EdGraph = unreal.load_class(None, "/Script/Engine.EdGraph")
    anim_graph = None
    for g in unreal.ObjectIterator(EdGraph):
        pn = g.get_path_name()
        if "ABP_KayKitLocomotion" not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn:
            continue
        L("EdGraph %s name=%s" % (pn, g.get_name()))
        if g.get_name() == "AnimGraph":
            anim_graph = g
    if anim_graph is None:
        L("no AnimGraph found")
        return
    # Inspect schema
    try:
        schema = anim_graph.get_editor_property("schema")
        L("schema=" + str(schema))
    except Exception as e:
        L("schema " + str(e))
    # Try create node via graph.add_node / construct
    SlotCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_Slot")
    LayeredCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_LayeredBoneBlend")
    L("SlotCls=%s LayeredCls=%s" % (SlotCls, LayeredCls))
    # Method 1: unreal.new_object outer=graph
    try:
        node = unreal.new_object(SlotCls, outer=anim_graph)
        L("new_object Slot -> " + str(node))
        try:
            anim_graph.add_node(node, False, False)
            L("add_node OK")
        except Exception as e:
            L("add_node " + str(e))
        try:
            # allocate default pins
            node.create_new_guid()
        except Exception as e:
            L("create_new_guid " + str(e))
        try:
            node.allocate_default_pins()
            L("allocate_default_pins OK")
        except Exception as e:
            L("allocate_default_pins " + str(e))
        try:
            node.reconstruct_node()
            L("reconstruct OK")
        except Exception as e:
            L("reconstruct " + str(e))
        try:
            n = node.get_editor_property("node")
            n.set_editor_property("slot_name", "DefaultSlot")
            L("set slot_name DefaultSlot OK")
        except Exception as e:
            L("set slot_name " + str(e))
        # Don't save yet — just probe. Delete test node?
        L("test slot node path=" + node.get_path_name())
        # remove to avoid dirty broken graph if pins not linked
        try:
            anim_graph.remove_node(node)
            L("removed test node")
        except Exception as e:
            L("remove_node " + str(e))
    except Exception as e:
        L("new_object Slot FAIL " + str(e))

def main():
    L("=== T231c START ===")
    dump_abp("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion")
    dump_abp("/Game/Mannequin/Animations/ThirdPerson_AnimBP")
    bones()
    bp_info()
    try_create_nodes()
    L("=== T231c DONE ===")
    flush()
    print("WROTE", OUT)

main()
