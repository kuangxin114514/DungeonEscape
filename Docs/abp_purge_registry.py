# -*- coding: utf-8 -*-
import unreal
import os
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_purge_registry_result.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

disk = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitFromTP_BROKEN.uasset",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitKnight_Probe_BROKEN.uasset",
]
for f in disk:
    L("disk {} exists={}".format(os.path.basename(f), os.path.exists(f)))

ar = unreal.AssetRegistryHelpers.get_asset_registry()
# Inspect available methods
meths = [m for m in dir(ar) if ("scan" in m.lower() or "path" in m.lower() or "delet" in m.lower() or "remov" in m.lower() or "purge" in m.lower() or "tick" in m.lower())]
L("ar_methods={}".format(meths))

# Force rescan folder
try:
    ar.scan_paths_synchronous(["/Game/Characters/Player/KayKit/Animations"], True)
    L("rescanned")
except Exception as e:
    L("rescan ERR {}".format(e))

# Try tick
try:
    ar.tick(1.0)
    L("tick OK")
except Exception as e:
    L("tick ERR {}".format(e))

# Wait and list via AssetRegistry filter
try:
    filt = unreal.ARFilter(
        class_names=["AnimBlueprint"],
        package_paths=["/Game/Characters/Player/KayKit/Animations"],
        recursive_paths=True,
    )
    assets = ar.get_assets(filt)
    names = []
    for a in assets:
        try:
            names.append(str(a.asset_name))
        except Exception:
            names.append(str(a))
    L("AR AnimBlueprints={}".format(names))
except Exception as e:
    L("ARFilter ERR {}".format(e))
    try:
        assets = ar.get_assets_by_path("/Game/Characters/Player/KayKit/Animations", recursive=False)
        L("get_assets_by_path={}".format([str(a.asset_name) if hasattr(a,'asset_name') else str(a) for a in assets]))
    except Exception as e2:
        L("get_assets_by_path ERR {}".format(e2))

# EditorAssetLibrary list again
left = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
L("EAL list={}".format([x for x in left if "ABP_" in x]))

# BP check
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
anim = meshc.get_editor_property("anim_class")
L("BP anim={}".format(anim.get_name() if anim else None))
L("anim_path={}".format(anim.get_path_name() if anim else None))

# If registry still shows ghosts, try notifying file deleted
for f in disk:
    try:
        # Absolute path to package filename
        if hasattr(ar, "scan_modified_asset_files"):
            ar.scan_modified_asset_files([f])
            L("scan_modified {}".format(os.path.basename(f)))
    except Exception as e:
        L("scan_modified ERR {}".format(e))

time.sleep(0.5)
left2 = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
L("EAL list2={}".format([x for x in left2 if "BROKEN" in x or "FromTP" in x or "Probe" in x]))
L("DONE")
flush()