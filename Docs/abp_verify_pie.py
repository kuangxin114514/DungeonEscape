# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_verify.txt"
lines = []
def L(m):
    lines.append(str(m))

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
probe = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe"
broken_probe = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN"
loco = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
bp = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"

if unreal.EditorAssetLibrary.does_asset_exist(probe):
    try:
        aes.close_all_editors_for_asset(unreal.EditorAssetLibrary.load_asset(probe))
    except Exception:
        pass
    if unreal.EditorAssetLibrary.does_asset_exist(broken_probe):
        unreal.EditorAssetLibrary.delete_asset(broken_probe)
    ok = unreal.EditorAssetLibrary.rename_asset(probe, broken_probe)
    L("rename probe -> {}".format(ok))
else:
    L("probe already gone")

# Mark log sentinel
unreal.log("=== PIE_SAFE_CHECK_BEGIN ===")

# Open loco for compile
a = unreal.EditorAssetLibrary.load_asset(loco)
aes.open_editor_for_assets([a])
time.sleep(4)
unreal.EditorAssetLibrary.save_asset(loco, only_if_is_dirty=False)
aes.close_all_editors_for_asset(a)

# Also open knight abp
if unreal.EditorAssetLibrary.does_asset_exist("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight"):
    k = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
    aes.open_editor_for_assets([k])
    time.sleep(2)
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight", only_if_is_dirty=False)
    aes.close_all_editors_for_asset(k)

unreal.log("=== PIE_SAFE_CHECK_END ===")

# Final assignment check
mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
cls = unreal.EditorAssetLibrary.load_blueprint_class(loco)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", cls)
unreal.EditorAssetLibrary.save_asset(bp, only_if_is_dirty=False)

L("anim_class={}".format(meshc.get_editor_property("anim_class")))
L("fromtp={}".format(unreal.EditorAssetLibrary.does_asset_exist("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")))
L("probe={}".format(unreal.EditorAssetLibrary.does_asset_exist(probe)))
L("loco_target={}".format(a.get_editor_property("target_skeleton").get_name()))
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
L("bs_skel={}".format(bs.get_editor_property("skeleton").get_name()))
samples = [(s.get_editor_property("animation").get_name(), round(s.get_editor_property("sample_value").x,1)) for s in bs.get_editor_property("sample_data")]
L("bs_samples={}".format(samples))

open(OUT, "w", encoding="utf-8").write("\\n".join(lines)+"\\n")
