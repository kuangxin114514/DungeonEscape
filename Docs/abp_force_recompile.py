# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_fix_result2.txt"
lines = []

def L(m):
    lines.append(str(m))

def flush():
    open(OUT, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")

mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = mesh.get_editor_property("skeleton")
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
L("mesh_skel={}".format(skel.get_path_name()))
L("abp_target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))
L("bs_skel={}".format(bs.get_editor_property("skeleton").get_path_name()))

# Inspect generated class skeleton if any
gen = unreal.load_object(None, "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP.ABP_KayKitFromTP_C")
L("gen={}".format(gen))
if gen:
    for prop in ["target_skeleton", "TargetSkeleton", "skeleton", "Skeleton"]:
        try:
            v = gen.get_editor_property(prop)
            L("gen.{}={}".format(prop, v.get_path_name() if hasattr(v, "get_path_name") else v))
        except Exception as e:
            L("gen.{} ERR {}".format(prop, e))
    cdo = unreal.get_default_object(gen)
    L("gen cdo={}".format(cdo))
    for prop in ["target_skeleton", "TargetSkeleton"]:
        try:
            v = cdo.get_editor_property(prop)
            L("cdo.{}={}".format(prop, v.get_path_name() if hasattr(v, "get_path_name") else v))
        except Exception as e:
            L("cdo.{} ERR {}".format(prop, e))

# Also check alternate skeleton object
alt = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Character/Mesh/KayKitKnightSkeleton")
L("alt_skel={}".format(alt.get_path_name() if alt else None))

# Ensure target
abp.set_editor_property("target_skeleton", skel)

# Open asset editor to force compile
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
L("aes={}".format(aes))
opened = False
try:
    opened = aes.open_editor_for_assets([abp])
    L("open_editor_for_assets -> {}".format(opened))
except Exception as e:
    L("open_editor ERR {}".format(e))
    try:
        opened = aes.open_editor_for_asset(abp)
        L("open_editor_for_asset -> {}".format(opened))
    except Exception as e2:
        L("open_editor_for_asset ERR {}".format(e2))

# Give editor a tick - remote exec is sync so sleep may help
time.sleep(1.0)

# Try close
try:
    aes.close_all_editors_for_asset(abp)
    L("closed editors")
except Exception as e:
    L("close ERR {}".format(e))

# Save
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP", only_if_is_dirty=False)
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion", only_if_is_dirty=False)

# Re-read gen after open
gen2 = unreal.load_object(None, "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP.ABP_KayKitFromTP_C")
L("gen2={}".format(gen2))
if gen2:
    for prop in ["target_skeleton", "TargetSkeleton"]:
        try:
            v = gen2.get_editor_property(prop)
            L("gen2.{}={}".format(prop, v.get_path_name() if hasattr(v, "get_path_name") else v))
        except Exception as e:
            L("gen2.{} ERR {}".format(prop, e))

# Assign to BP
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", abp_cls)
meshc.set_editor_property("skeletal_mesh", mesh)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("assigned anim_class={}".format(meshc.get_editor_property("anim_class")))

# Compare skeleton compatibility: AnimBP generated class target vs mesh
# Read TargetSkeleton from UAnimBlueprint via get_editor_property again
L("final abp target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))
L("final mesh skel={}".format(mesh.get_editor_property("skeleton").get_path_name()))
same = abp.get_editor_property("target_skeleton") == mesh.get_editor_property("skeleton")
L("same_object={}".format(same))
L("path_equal={}".format(abp.get_editor_property("target_skeleton").get_path_name() == mesh.get_editor_property("skeleton").get_path_name()))

flush()
