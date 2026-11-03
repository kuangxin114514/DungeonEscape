# -*- coding: utf-8 -*-
import unreal
import os
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_disk_delete_result.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

disk_files = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitFromTP_BROKEN.uasset",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitKnight_Probe_BROKEN.uasset",
]
game_paths = [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN",
]

# Close any open asset editors by path name without full load if possible
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
try:
    # close all editors to release packages
    # AssetEditorSubsystem in 4.27: close_all_editors? 
    if hasattr(aes, "close_all_editors"):
        aes.close_all_editors()
        L("close_all_editors OK")
except Exception as e:
    L("close_all_editors ERR {}".format(e))

# Ensure BP uses locomotion BEFORE deleting (already done, reaffirm without touching broken)
loco_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
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
L("BP anim_class={}".format(anim.get_name() if anim else None))

# Collect packages to unload WITHOUT using load_asset on broken (use find_package)
pkgs = []
for gp in game_paths:
    try:
        # unreal.find_package in some builds
        pkg = None
        if hasattr(unreal, "find_package"):
            pkg = unreal.find_package(gp)
        if pkg is None:
            # Package path is same as asset path for one-asset packages
            try:
                pkg = unreal.load_package(gp)
            except TypeError:
                try:
                    pkg = unreal.load_package(None)  # wrong
                except Exception:
                    pkg = None
            except Exception as e:
                L("load_package1 ERR {}".format(e))
                try:
                    pkg = unreal.load_package(gp)
                except Exception as e2:
                    L("load_package2 ERR {}".format(e2))
        if pkg:
            pkgs.append(pkg)
            L("will unload {}".format(pkg))
    except Exception as e:
        L("find pkg ERR {} {}".format(gp, e))

if pkgs:
    try:
        unreal.EditorLoadingAndSavingUtils.unload_packages(pkgs)
        L("unloaded {}".format(len(pkgs)))
    except Exception as e:
        L("unload ERR {}".format(e))

time.sleep(0.5)

# Disk delete
for f in disk_files:
    L("disk exists {} = {}".format(f, os.path.exists(f)))
    if os.path.exists(f):
        try:
            os.chmod(f, 0o666)
        except Exception:
            pass
        try:
            os.remove(f)
            L("os.remove OK {}".format(os.path.basename(f)))
        except Exception as e:
            L("os.remove ERR {} {}".format(os.path.basename(f), e))

# Also remove .uexp/.ubulk if any
for f in disk_files:
    for ext in [".uexp", ".ubulk"]:
        alt = f[:-7] + ext if f.endswith(".uasset") else f + ext
        # correct: replace .uasset
        alt = f.replace(".uasset", ext)
        if os.path.exists(alt):
            try:
                os.remove(alt)
                L("removed {}".format(os.path.basename(alt)))
            except Exception as e:
                L("remove alt ERR {}".format(e))

# Rescan asset registry
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(["/Game/Characters/Player/KayKit/Animations"], True)
    L("scan_paths_synchronous OK")
except Exception as e:
    L("scan ERR {}".format(e))

time.sleep(0.5)

for gp in game_paths:
    # does_asset_exist may still cache; list_assets is better
    L("does_asset_exist {} = {}".format(gp, unreal.EditorAssetLibrary.does_asset_exist(gp)))

assets_left = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
broken_left = [a for a in assets_left if "BROKEN" in a or "FromTP" in a or "Probe" in a]
L("broken_or_fromtp_left={}".format(broken_left))
abps = [a for a in assets_left if "/ABP_" in a]
L("remaining_ABPs={}".format(abps))
L("DONE")
flush()