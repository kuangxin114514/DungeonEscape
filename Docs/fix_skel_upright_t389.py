# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skel_upright_t389.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T389: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bp=unreal.load_asset(BP)
L("bp=%s"%bp)

def fix_mesh(o, tag):
    try:
        before=o.get_editor_property("relative_rotation")
    except Exception as e:
        L("%s read fail %s"%(tag,e)); return
    L("%s before %s"%(tag, before))
    # Upright: zero relative rotation (capsule provides facing). Do NOT use yaw=270 as pitch by mistake.
    try:
        o.set_editor_property("relative_rotation", unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
        after=o.get_editor_property("relative_rotation")
        L("%s after %s"%(tag, after))
    except Exception as e:
        L("%s set fail %s"%(tag,e))
    try:
        o.set_editor_property("anim_class", None)
    except Exception:
        pass
    try:
        o.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        pass
    # Idle standing pose if possible
    try:
        idle=unreal.load_asset("/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig")
        if idle is not None:
            try:
                o.set_editor_property("animation_data", None)
            except Exception:
                pass
            try:
                o.override_animation_data(idle, True, True, 0.0, 1.0)
                L("%s idle override"%tag)
            except Exception:
                try:
                    o.set_animation(idle)
                    o.play(True)
                    L("%s idle set_animation"%tag)
                except Exception as e2:
                    L("%s idle fail %s"%(tag,e2))
    except Exception as e:
        L("%s idle load %s"%(tag,e))

# Fix all skeletal meshes belonging to skeleton BP / placed instances
for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn and "Enemy_Skeleton" not in pn:
        continue
    fix_mesh(o, pn.split("/")[-1][:80])

# Also fix via SCS nodes if accessible
try:
    scs=bp.simple_construction_script
except Exception:
    scs=None
try:
    if scs is None: scs=bp.get_editor_property("simple_construction_script")
except Exception:
    pass
if scs is not None:
    try:
        nodes=list(scs.get_all_nodes())
    except Exception:
        nodes=[]
    L("scs nodes=%d"%len(nodes))
    for n in nodes:
        tmpl=None
        try: tmpl=n.component_template
        except Exception:
            try: tmpl=n.get_editor_property("component_template")
            except Exception: tmpl=None
        if tmpl is None: continue
        try:
            if isinstance(tmpl, unreal.SkeletalMeshComponent) or "SkeletalMesh" in tmpl.get_class().get_name():
                fix_mesh(tmpl, "SCS:"+str(n.get_variable_name()))
        except Exception as e:
            L("scs "+str(e))

try:
    unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")
except Exception as e:
    L("save "+str(e))

# Fix placed actors actor rotation pitch/roll just in case
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
except Exception:
    world=None
if world is not None:
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        try:
            n=a.get_name() or ""
            cn=a.get_class().get_name() if a.get_class() else ""
        except Exception:
            continue
        if "Skeleton" not in n and "Skeleton" not in cn:
            continue
        try:
            r=a.get_actor_rotation()
            L("actor %s rot=%s"%(n,r))
            if abs(float(r.pitch))>1 or abs(float(r.roll))>1:
                a.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=float(r.yaw), roll=0.0), False)
                L("  actor uprighted")
        except Exception as e:
            L("actor "+str(e))
        mesh=None
        try: mesh=a.get_editor_property("mesh")
        except Exception: mesh=None
        if mesh is not None:
            fix_mesh(mesh, "placed:"+n)

try:
    unreal.EditorLevelLibrary.save_current_level(); L("level saved")
except Exception as e:
    L("level save "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
