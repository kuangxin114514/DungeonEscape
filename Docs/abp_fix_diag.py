# -*- coding: utf-8 -*-
"""Diagnose ABP_KayKitFromTP compile failure: skeleton / blendspace / anim refs."""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_fix_diag.txt"
lines = []

def L(msg):
    s = str(msg)
    lines.append(s)
    unreal.log(s)

def load(path):
    a = unreal.EditorAssetLibrary.load_asset(path)
    L("LOAD {} -> {}".format(path, a))
    return a

mesh = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel_asset = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
abp = load("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
abp2 = load("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
bs = load("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
idle = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
idle2 = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
walk2 = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")
run2 = load("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")

# mesh skeleton
if mesh:
    try:
        mskel = mesh.get_editor_property("skeleton")
        L("MESH.skeleton={}".format(mskel))
        if mskel:
            L("MESH.skeleton path={} name={} class={}".format(mskel.get_path_name(), mskel.get_name(), mskel.get_class().get_name()))
            try:
                L("MESH.skel package={}".format(mskel.get_outer().get_path_name() if mskel.get_outer() else None))
            except Exception as e:
                L("MESH.skel outer ERR {}".format(e))
    except Exception as e:
        L("MESH.skeleton ERR {}".format(e))

# anim skeletons
for label, anim in [("idle_rig", idle), ("walk_rig", walk), ("run_rig", run), ("idle", idle2), ("walk", walk2), ("run", run2)]:
    if not anim:
        continue
    try:
        askel = anim.get_editor_property("skeleton")
        L("ANIM {}.skeleton={}".format(label, askel.get_path_name() if askel else None))
    except Exception as e:
        L("ANIM {}.skeleton ERR {}".format(label, e))

# BS
if bs:
    try:
        L("BS class={} skeleton={}".format(bs.get_class().get_name(), bs.get_editor_property("skeleton")))
        samples = bs.get_editor_property("sample_data")
        L("BS samples count={}".format(len(samples) if samples else 0))
        if samples:
            for i, s in enumerate(samples):
                anim = s.get_editor_property("animation")
                val = s.get_editor_property("sample_value")
                L("  sample[{}] anim={} val={}".format(i, anim.get_path_name() if anim else None, val))
        params = bs.get_editor_property("blend_parameters")
        if params:
            for i, p in enumerate(params):
                L("  param[{}] name={} min={} max={} grid={}".format(
                    i, p.get_editor_property("display_name"), p.get_editor_property("min"),
                    p.get_editor_property("max"), p.get_editor_property("grid_num")))
    except Exception as e:
        L("BS ERR {}".format(e))

# ABP target skeleton
for label, bp in [("FromTP", abp), ("KayKit", abp2)]:
    if not bp:
        continue
    L("ABP {} class={}".format(label, bp.get_class().get_name()))
    for prop in ["target_skeleton", "TargetSkeleton", "preview_skeletal_mesh", "PreviewSkeletalMesh"]:
        try:
            v = bp.get_editor_property(prop)
            L("  {}.{}={}".format(label, prop, v.get_path_name() if hasattr(v, "get_path_name") else v))
        except Exception as e:
            L("  {}.{} ERR {}".format(label, prop, e))
    # compile status
    try:
        gen = bp.generated_class()
        L("  {}.generated_class={}".format(label, gen))
    except Exception as e:
        L("  {}.generated_class ERR {}".format(label, e))
    try:
        status = bp.status
        L("  {}.status={}".format(label, status))
    except Exception as e:
        L("  {}.status ERR {}".format(label, e))

# Find all Skeleton objects in memory related to KayKit
SkeletonCls = unreal.load_class(None, "/Script/Engine.Skeleton")
kaykit_skels = []
if SkeletonCls:
    for obj in unreal.ObjectIterator(SkeletonCls):
        pn = obj.get_path_name()
        if "KayKit" in pn or "Knight" in pn:
            kaykit_skels.append(pn)
L("KayKit Skeleton objects in memory: {}".format(kaykit_skels))

# ThirdPerson skeleton
tp = load("/Game/Mannequin/Character/Mesh/UE4_Mannequin_Skeleton")
if not tp:
    tp = load("/Game/Characters/Mannequin/Mesh/UE4_Mannequin_Skeleton")
L("TP skeleton={}".format(tp))

# Compile ABP and capture messages if possible
if abp:
    try:
        ok = unreal.KismetEditorUtilities.compile_blueprint(abp)
        L("compile FromTP returned {}".format(ok))
    except Exception as e:
        L("compile FromTP ERR {}".format(e))
    try:
        # BlueprintEditorLibrary
        bel = unreal.BlueprintEditorLibrary
        L("BEL methods: {}".format([m for m in dir(bel) if "ompil" in m.lower() or "skel" in m.lower() or "status" in m.lower()]))
    except Exception as e:
        L("BEL ERR {}".format(e))

# BP mesh anim class
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
if bp_cls:
    cdo = unreal.get_default_object(bp_cls)
    meshc = cdo.get_editor_property("mesh")
    L("BP mesh mode={} anim_class={} skmesh={}".format(
        meshc.get_editor_property("animation_mode"),
        meshc.get_editor_property("anim_class"),
        meshc.get_editor_property("skeletal_mesh")))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
L("WROTE " + OUT)
L("DIAG_DONE")
