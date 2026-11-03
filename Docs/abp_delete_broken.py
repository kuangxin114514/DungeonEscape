# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_delete_broken_result.txt"
lines = []

def L(m):
    lines.append(str(m))

def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
broken = [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN",
]
loco_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"

for p in broken:
    exists = unreal.EditorAssetLibrary.does_asset_exist(p)
    L("exists {} = {}".format(p, exists))
    if not exists:
        continue
    try:
        a = unreal.EditorAssetLibrary.load_asset(p)
        aes.close_all_editors_for_asset(a)
        L("closed editor {}".format(p))
    except Exception as e:
        L("close ERR {} {}".format(p, e))

pkgs = []
for p in broken:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        try:
            pkg = unreal.load_package(None, p)
            if pkg:
                pkgs.append(pkg)
                L("pkg {}".format(pkg))
        except Exception as e:
            L("load_package ERR {} {}".format(p, e))
if pkgs:
    try:
        unreal.EditorLoadingAndSavingUtils.unload_packages(pkgs)
        L("unloaded {}".format(len(pkgs)))
    except Exception as e:
        L("unload ERR {}".format(e))

time.sleep(0.3)

for p in broken:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        ok = unreal.EditorAssetLibrary.delete_asset(p)
        L("delete {} -> {}".format(p, ok))
    else:
        L("already gone {}".format(p))

for p in [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe",
]:
    L("leftover {} exists={}".format(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
loco_cls = unreal.EditorAssetLibrary.load_blueprint_class(loco_path)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", loco_cls)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
anim = meshc.get_editor_property("anim_class")
L("BP anim_class={}".format(anim))
L("BP anim_name={}".format(anim.get_name() if anim else None))

for p in broken:
    L("after_delete exists {} = {}".format(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

for name in ["ABP_KayKitFromTP_BROKEN", "ABP_KayKitKnight_Probe_BROKEN", "ABP_KayKitFromTP", "ABP_KayKitKnight_Probe"]:
    path = "/Game/Characters/Player/KayKit/Animations/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        refs = unreal.EditorAssetLibrary.find_package_referencers_for_asset(path, load_assets_to_confirm=False)
        L("refs for {} count={}".format(name, len(refs) if refs else 0))
        for r in (refs or []):
            L("  {}".format(r))
    else:
        L("no asset to ref-check: {}".format(name))

assets = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
abps = [a for a in assets if "/ABP_" in a]
L("remaining_ABPs={}".format(abps))
L("loco_exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(loco_path)))
L("DONE")
flush()