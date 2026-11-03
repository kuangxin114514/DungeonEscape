# -*- coding: utf-8 -*-
import unreal, inspect

els = unreal.EditorLoadingAndSavingUtils
for name in ["reload_packages", "unload_packages", "save_packages"]:
    fn = getattr(els, name)
    unreal.log("{} -> {}".format(name, fn))
    try:
        unreal.log("  doc={}".format(fn.__doc__[:500] if fn.__doc__ else None))
    except Exception:
        pass

# unreal.reload
unreal.log("unreal.reload={}".format(unreal.reload))
try:
    unreal.log("reload doc={}".format(unreal.reload.__doc__[:300] if unreal.reload.__doc__ else None))
except Exception:
    pass

# Try unload then reload
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
pkg = bs.get_outermost()
unreal.log("pkg={} name={}".format(pkg, pkg.get_name() if pkg else None))

# unload_packages expects Array(Package)
try:
    result = unreal.EditorLoadingAndSavingUtils.unload_packages([pkg])
    unreal.log("unload result={}".format(result))
except Exception as e:
    unreal.log("unload ERR {}".format(e))

# Now load again from disk
try:
    # After unload, load_asset should re-read disk
    bs2 = unreal.EditorAssetLibrary.load_asset(bs_path)
    sk = bs2.get_editor_property("skeleton") if bs2 else None
    unreal.log("AFTER_UNLOAD skel={}".format(sk.get_path_name() if sk else None))
except Exception as e:
    unreal.log("reload load ERR {}".format(e))

# Alternative: reload_packages
try:
    # Need packages list - if unload worked, package may be invalid
    bs3 = unreal.EditorAssetLibrary.load_asset(bs_path)
    pkg3 = bs3.get_outermost()
    # InteractionMode enum
    unreal.log("ReloadMode values try")
    try:
        modes = [x for x in dir(unreal.ReloadPackagesInteractionMode) if not x.startswith("_")]
        unreal.log("modes={}".format(modes))
    except Exception as e:
        unreal.log("modes ERR {}".format(e))
    try:
        r = unreal.EditorLoadingAndSavingUtils.reload_packages([pkg3])
        unreal.log("reload_packages result={}".format(r))
    except Exception as e:
        unreal.log("reload_packages ERR {}".format(e))
        try:
            r = unreal.EditorLoadingAndSavingUtils.reload_packages([pkg3], unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
            unreal.log("reload_packages ASSUME result={}".format(r))
        except Exception as e2:
            unreal.log("reload2 ERR {}".format(e2))
except Exception as e:
    unreal.log("outer reload ERR {}".format(e))

bs4 = unreal.EditorAssetLibrary.load_asset(bs_path)
sk4 = bs4.get_editor_property("skeleton") if bs4 else None
unreal.log("FINAL skel={}".format(sk4.get_path_name() if sk4 else None))
unreal.log("RELOAD_TEST_DONE")