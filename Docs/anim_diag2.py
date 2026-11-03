# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_diag2.txt"
lines=[]
def L(m):
    lines.append(str(m))
    unreal.log("[DIAG2] "+str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

SKEL_ORIG="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
SKEL_ALIAS="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
MESH="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
BS="/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
ABP="/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
IDLE="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig"
BP="/Game/Characters/Player/KayKit/BP_KayKitKnight"

so=unreal.EditorAssetLibrary.load_asset(SKEL_ORIG)
sa=unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
mesh=unreal.EditorAssetLibrary.load_asset(MESH)
bs=unreal.EditorAssetLibrary.load_asset(BS)
abp=unreal.EditorAssetLibrary.load_asset(ABP)
idle=unreal.EditorAssetLibrary.load_asset(IDLE)

def bone_info(skel, label):
    if not skel:
        L(label+" None"); return
    L(label+" path="+skel.get_path_name())
    for prop in ["bone_tree","BoneTree","virtual_bones","sockets"]:
        try:
            v=skel.get_editor_property(prop)
            L("  {} type={} len={}".format(prop, type(v).__name__, (len(v) if hasattr(v,"__len__") else v)))
            if prop.lower()=="bone_tree" and v is not None:
                # print first few bone names if possible
                n=min(8,len(v))
                for i in range(n):
                    b=v[i]
                    name=None
                    for pn in ["name","Name","bone_name","BoneName"]:
                        try:
                            name=b.get_editor_property(pn); break
                        except Exception:
                            pass
                    if name is None:
                        try: name=str(b)
                        except Exception: name="?"
                    L("    bone[{}]={}".format(i,name))
        except Exception as e:
            L("  {} ERR {}".format(prop,e))

bone_info(so,"ORIG")
bone_info(sa,"ALIAS")
L("same_object={}".format(so==sa))

# Save alias to disk forcibly
try:
    ok=unreal.EditorAssetLibrary.save_loaded_asset(sa)
    L("save_loaded_asset alias -> {}".format(ok))
except Exception as e:
    L("save_loaded_asset ERR {}".format(e))
try:
    ok=unreal.EditorAssetLibrary.save_asset(SKEL_ALIAS, only_if_is_dirty=False)
    L("save_asset alias -> {}".format(ok))
except Exception as e:
    L("save_asset ERR {}".format(e))

# Also save orig
try:
    ok=unreal.EditorAssetLibrary.save_loaded_asset(so)
    L("save_loaded_asset orig -> {}".format(ok))
except Exception as e:
    L("save orig ERR {}".format(e))

# Idle anim details
L("idle={}".format(idle))
if idle:
    for prop in ["skeleton","sequence_length","num_frames","rate_scale","additive_anim_type","ref_pose_type"]:
        try:
            L("  idle.{}={}".format(prop, idle.get_editor_property(prop)))
        except Exception as e:
            L("  idle.{} ERR {}".format(prop,e))
    try:
        sk=idle.get_editor_property("skeleton")
        L("  idle.skel path={}".format(sk.get_path_name() if sk else None))
        L("  idle.skel is alias={}".format(sk==sa))
        L("  idle.skel is orig={}".format(sk==so))
    except Exception as e:
        L("  idle skel ERR {}".format(e))

# BS details
L("bs class={}".format(bs.get_class().get_name() if bs else None))
if bs:
    try:
        params=bs.get_editor_property("blend_parameters")
        L("  nparams={}".format(len(params)))
        for i,p in enumerate(params):
            try:
                L("  p[{}] name={} min={} max={} grid={}".format(
                    i, p.get_editor_property("display_name"),
                    p.get_editor_property("min"), p.get_editor_property("max"),
                    p.get_editor_property("grid_num")))
            except Exception as e:
                L("  p[{}] ERR {}".format(i,e))
    except Exception as e:
        L("  params ERR {}".format(e))
    sd=bs.get_editor_property("sample_data")
    L("  nsamples={}".format(len(sd)))
    for i,s in enumerate(sd):
        a=s.get_editor_property("animation")
        L("  s[{}] {} val={} askel={}".format(
            i, a.get_name() if a else None, s.get_editor_property("sample_value"),
            (a.get_editor_property("skeleton").get_path_name() if a and a.get_editor_property("skeleton") else None)))

# ABP variables / status
L("abp={}".format(abp))
if abp:
    for prop in ["status","target_skeleton","blueprint_status"]:
        try:
            L("  abp.{}={}".format(prop, abp.get_editor_property(prop)))
        except Exception as e:
            L("  abp.{} ERR {}".format(prop,e))
    cls=unreal.EditorAssetLibrary.load_blueprint_class(ABP)
    L("  gencls={}".format(cls))
    if cls:
        cdo=unreal.get_default_object(cls)
        for prop in ["speed","Speed","direction","Direction","is_in_air","IsInAir"]:
            try:
                L("  cdo.{}={}".format(prop, cdo.get_editor_property(prop)))
            except Exception as e:
                L("  cdo.{} missing".format(prop))

# BP mesh anim
bp_cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(bp_cls)
meshc=cdo.get_editor_property("mesh")
L("bp mesh mode={} anim_class={} skmesh={}".format(
    meshc.get_editor_property("animation_mode"),
    meshc.get_editor_property("anim_class"),
    meshc.get_editor_property("skeletal_mesh")))
try:
    L("bp mesh visibility={} hidden={}".format(meshc.get_editor_property("visible"), meshc.get_editor_property("hidden_in_game")))
except Exception:
    pass
# relative scale
try:
    L("bp mesh rel_scale={}".format(meshc.get_editor_property("relative_scale3d")))
    L("bp mesh rel_loc={}".format(meshc.get_editor_property("relative_location")))
    L("bp mesh rel_rot={}".format(meshc.get_editor_property("relative_rotation")))
except Exception as e:
    L("bp mesh xform ERR {}".format(e))

# Check if ThirdPerson EventGraph style: look for anim graph nodes count
EdGraphNode=unreal.load_class(None,"/Script/Engine.EdGraphNode")
kinds={}
speed_bound=0
for obj in unreal.ObjectIterator(EdGraphNode):
    pn=obj.get_path_name()
    if "ABP_KayKitLocomotion" not in pn or "Default__" in pn or "AnimPreview" in pn:
        continue
    cn=obj.get_class().get_name()
    kinds[cn]=kinds.get(cn,0)+1
L("abp node kinds={}".format(kinds))

# Try play idle via single-node temporarily? Just report; also ensure bEnableRootMotion false on idle
if idle:
    for prop in ["enable_root_motion","EnableRootMotion","force_root_lock","root_motion_root_lock","use_normalized_root_motion_root_length"]:
        try:
            L("idle.{}={}".format(prop, idle.get_editor_property(prop)))
        except Exception:
            pass

flush()
print("DIAG2_DONE")