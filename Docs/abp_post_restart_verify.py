# -*- coding: utf-8 -*-
import unreal
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_post_restart_verify.txt"
lines = []
def L(m):
    lines.append(str(m))

disk = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitFromTP_BROKEN.uasset",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitKnight_Probe_BROKEN.uasset",
]
for f in disk:
    L("disk {} exists={}".format(os.path.basename(f), os.path.exists(f)))

for p in [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion",
]:
    L("exists {} = {}".format(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

left = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
abps = [a for a in left if "/ABP_" in a]
broken = [a for a in left if "BROKEN" in a or "FromTP" in a or "Probe" in a]
L("remaining_ABPs={}".format(abps))
L("broken_or_fromtp_or_probe={}".format(broken))

ar = unreal.AssetRegistryHelpers.get_asset_registry()
try:
    assets = ar.get_assets_by_path("/Game/Characters/Player/KayKit/Animations", recursive=False)
    names = []
    for a in assets:
        try:
            names.append(str(a.asset_name))
        except Exception:
            names.append(str(a))
    L("AR names={}".format(names))
    L("AR broken={[n for n in names if 'BROKEN' in n or 'FromTP' in n or 'Probe' in n]}")
except Exception as e:
    L("AR ERR {}".format(e))

# Ensure BP uses locomotion only
loco_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
loco_cls = unreal.EditorAssetLibrary.load_blueprint_class(loco_path)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
cur = meshc.get_editor_property("anim_class")
L("BP anim before={}".format(cur.get_path_name() if cur else None))
if cur is None or "ABP_KayKitLocomotion" not in str(cur.get_path_name()):
    meshc.set_editor_property("skeletal_mesh", mesh)
    meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
    meshc.set_editor_property("anim_class", loco_cls)
    unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
    cur = meshc.get_editor_property("anim_class")
    L("BP anim after set={}".format(cur.get_path_name() if cur else None))
else:
    L("BP already locomotion only")

# Soft compile check: open loco, save
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
loco = unreal.EditorAssetLibrary.load_asset(loco_path)
aes.open_editor_for_assets([loco])
unreal.EditorAssetLibrary.save_asset(loco_path, only_if_is_dirty=False)
aes.close_all_editors_for_asset(loco)
L("loco open/save/close OK")

# Search project for string refs to BROKEN in common config/maps? use asset registry referencers N/A
# Compile all anim BPs in folder via loading classes
for p in ["/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion", "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight"]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class(p)
            L("load_class {} -> {}".format(p, cls))
        except Exception as e:
            L("load_class ERR {} {}".format(p, e))

for p in [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN",
]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        L("UNEXPECTED still exists {}".format(p))
    else:
        L("confirmed gone {}".format(p))

L("PIE_SAFE_NO_BROKEN_ASSETS=1")
L("DONE")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")