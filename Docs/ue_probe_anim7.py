# -*- coding: utf-8 -*-
import unreal

# Find any BlendSpace in memory / content
bs_cls = unreal.BlendSpace1D
found = []
for obj in unreal.ObjectIterator(bs_cls):
    try:
        found.append(obj.get_path_name())
    except Exception:
        pass
unreal.log("BS1D in mem count={} sample={}".format(len(found), found[:10]))

bs2 = unreal.BlendSpace
found2 = []
for obj in unreal.ObjectIterator(bs2):
    try:
        found2.append(obj.get_path_name())
    except Exception:
        pass
unreal.log("BS in mem count={} sample={}".format(len(found2), found2[:10]))

# Asset registry search
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for clsname in ["BlendSpace1D","BlendSpace","AnimBlueprint"]:
        assets = ar.get_assets_by_class(clsname, True)
        unreal.log("AR {} count={}".format(clsname, len(assets) if assets else 0))
        if assets:
            for a in list(assets)[:8]:
                unreal.log("  {} /{}".format(a.asset_name, a.package_path))
except Exception as e:
    unreal.log("AR err {}".format(e))

# Try factory create with edit_after_new False and create_new
factory = unreal.BlendSpaceFactory1D()
factory.set_editor_property("edit_after_new", False)
factory.set_editor_property("create_new", True)
# Try get TargetSkeleton via get_editor_property (read)
try:
    unreal.log("read TargetSkeleton={}".format(factory.get_editor_property("TargetSkeleton")))
except Exception as e:
    unreal.log("read TS err {}".format(e))

# AnimSequenceFactory style - use duplicate of ABP probe and change?
# Try using AssetDuplicate

# Alternative: set single node to Running and also create a montages?
# Check Character parent class event graph for existing tick

bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
cdo = unreal.get_default_object(bp_cls)
unreal.log("char class={} parent={}".format(bp_cls.get_name(), bp_cls.get_super_class().get_name() if hasattr(bp_cls,"get_super_class") else "?"))
try:
    unreal.log("super={}".format(cdo.get_class().get_super_class()))
except Exception as e:
    unreal.log("super err {}".format(e))

# max walk speed
try:
    cm = cdo.get_editor_property("character_movement")
    unreal.log("max_walk_speed={}".format(cm.get_editor_property("max_walk_speed")))
except Exception as e:
    unreal.log("cm err {}".format(e))

# Try create blendspace via AnimationLibrary? no
# Use unreal.AssetToolsHelpers.get_asset_tools().create_asset with BlendSpaceFactoryNew
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
for fname, ucls in [("BlendSpaceFactory1D", unreal.BlendSpace1D), ("BlendSpaceFactoryNew", unreal.BlendSpace)]:
    f = getattr(unreal, fname)()
    f.set_editor_property("edit_after_new", False)
    # try set via call_method SetSkeleton?
    for m in ["set_skeleton","SetSkeleton","set_target_skeleton"]:
        try:
            unreal.log("{} {} -> {}".format(fname, m, f.call_method(m, (skel,))))
        except Exception as e:
            unreal.log("{} {} ERR {}".format(fname, m, e))
    name = "BS_Try_" + fname
    path = "/Game/Characters/Player/KayKit/Animations"
    full = path + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    try:
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, ucls, f)
        unreal.log("{} create -> {}".format(fname, asset))
        if asset:
            for pn in ["skeleton","Skeleton"]:
                try:
                    asset.set_editor_property(pn, skel)
                    unreal.log("asset set {} OK".format(pn))
                except Exception as e:
                    unreal.log("asset set {} ERR {}".format(pn, e))
                try:
                    unreal.log("asset get {} = {}".format(pn, asset.get_editor_property(pn)))
                except Exception as e:
                    unreal.log("asset get {} ERR {}".format(pn, e))
    except Exception as e:
        unreal.log("{} create ERR {}".format(fname, e))

unreal.log("PROBE7_DONE")