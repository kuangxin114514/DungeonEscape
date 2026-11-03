# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_skeleton_scs.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

BP_PATH = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
L("bp=%s" % bp)
for attr in ("simple_construction_script","SimpleConstructionScript","generated_class"):
    try:
        L("%s=%s" % (attr, getattr(bp, attr) if hasattr(bp, attr) else bp.get_editor_property(attr)))
    except Exception as e:
        L("%s err %s" % (attr, e))

scs = None
try:
    scs = bp.get_editor_property("simple_construction_script")
except Exception as e:
    L("scs prop %s" % e)
L("scs=%s" % scs)
if scs:
    nodes = []
    try:
        nodes = scs.get_all_nodes()
    except Exception as e:
        L("get_all_nodes %s" % e)
        try:
            nodes = scs.get_editor_property("root_nodes")
        except Exception as e2:
            L("root_nodes %s" % e2)
    L("nodes=%s" % nodes)
    for n in (nodes or []):
        try:
            L("node %s class=%s" % (n, n.get_class().get_name()))
        except Exception as e:
            L("node %s" % e)
        for p in ("component_class","variable_name","component_template","parent_component_or_variable_name"):
            try:
                L("  %s=%s" % (p, n.get_editor_property(p)))
            except Exception:
                pass
        try:
            tmpl = n.get_editor_property("component_template")
            if tmpl:
                L("  tmpl class=%s" % tmpl.get_class().get_name())
                for q in ("relative_location","relative_rotation","relative_scale3d","capsule_half_height","skeletal_mesh"):
                    try:
                        L("    %s=%s" % (q, tmpl.get_editor_property(q)))
                    except Exception:
                        pass
        except Exception as e:
            L("  tmpl err %s" % e)

# inspect preview actor components relative via get_editor_property
acts = unreal.EditorLevelLibrary.get_all_level_actors()
for a in acts:
    if "Preview_Skeleton" in a.get_name():
        L("actor %s loc=%s" % (a.get_name(), a.get_actor_location()))
        for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
            L(" mesh name=%s" % c.get_name())
            for q in ("relative_location","relative_scale3d","animation_mode"):
                try:
                    L("  %s=%s" % (q, c.get_editor_property(q)))
                except Exception as e:
                    L("  %s err %s" % (q, e))
        for c in a.get_components_by_class(unreal.CapsuleComponent):
            for q in ("capsule_half_height","capsule_radius","relative_location"):
                try:
                    L("  cap %s=%s" % (q, c.get_editor_property(q)))
                except Exception:
                    pass

# spawn a transient one to see construction result
gc = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
loc = unreal.Vector(0,0,300)
try:
    act = unreal.EditorLevelLibrary.spawn_actor_from_class(gc, loc, unreal.Rotator(0,0,0))
    L("spawned %s" % act)
    for c in act.get_components_by_class(unreal.SkeletalMeshComponent):
        L("spawn mesh rel=%s scale=%s" % (c.get_editor_property("relative_location"), c.get_editor_property("relative_scale3d")))
    for c in act.get_components_by_class(unreal.CapsuleComponent):
        L("spawn cap half=%s" % c.get_editor_property("capsule_half_height"))
    unreal.EditorLevelLibrary.destroy_actor(act)
    L("destroyed temp")
except Exception as e:
    L("spawn err %s" % e)

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
