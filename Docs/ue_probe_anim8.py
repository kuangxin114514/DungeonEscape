# -*- coding: utf-8 -*-
import unreal

ar = unreal.AssetRegistryHelpers.get_asset_registry()
for clsname in ["BlendSpace1D","BlendSpace","AnimBlueprint","AnimSequence"]:
    assets = ar.get_assets_by_class(clsname, True)
    unreal.log("=== {} count={} ===".format(clsname, len(assets) if assets else 0))
    if not assets:
        continue
    shown = 0
    for a in assets:
        path = str(a.package_path) + "/" + str(a.asset_name)
        # filter mannequin / third / kaykit / abp
        if clsname == "AnimSequence":
            if "Mannequin" in path or "ThirdPerson" in path or "KayKit" in path:
                unreal.log("  " + path)
                shown += 1
                if shown > 40:
                    break
        else:
            unreal.log("  " + path)

# Inspect ThirdPerson_IdleRun_2D
bs = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D")
unreal.log("bs={}".format(bs))
if bs:
    unreal.log("bs class={}".format(bs.get_class().get_name()))
    for pn in ["skeleton","sample_data","blend_parameters"]:
        try:
            v = bs.get_editor_property(pn)
            unreal.log("bs.{}={}".format(pn, v))
        except Exception as e:
            unreal.log("bs.{} ERR {}".format(pn, e))

# List mannequin folder
try:
    assets = unreal.EditorAssetLibrary.list_assets("/Game/Mannequin", True, False)
    for a in assets:
        unreal.log("MAN " + a)
except Exception as e:
    unreal.log("list err {}".format(e))

unreal.log("PROBE8_DONE")