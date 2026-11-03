# -*- coding: utf-8 -*-
import unreal
paths = [
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight",
    "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight",
]
for p in paths:
    a = unreal.EditorAssetLibrary.load_asset(p)
    if a:
        unreal.EditorAssetLibrary.save_loaded_asset(a)
        unreal.log("SAVED " + p)
    else:
        # skeleton name may differ
        unreal.log_warning("MISS " + p)
# save all dirty
try:
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log("SAVE_DIRTY_OK")
except Exception as e:
    unreal.log_warning(str(e))