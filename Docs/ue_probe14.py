# -*- coding: utf-8 -*-
import unreal

# Export AnimBP / Character BP as text to see pin links?
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
# Try export
try:
    tf = unreal.AssetExportTask()
    tf.set_editor_property("object", abp)
    tf.set_editor_property("filename", r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_export.txt")
    tf.set_editor_property("automated", True)
    tf.set_editor_property("prompt", False)
    # find exporter
    for name in ["AnimBlueprintExporter","ObjectExporterT3D","AssetExporter"]:
        if hasattr(unreal, name):
            unreal.log("has exporter {}".format(name))
except Exception as e:
    unreal.log("export setup ERR {}".format(e))

# Try unreal.Exporter
exporters = [n for n in dir(unreal) if "Export" in n]
unreal.log("exporters: {}".format(exporters))

# Look at ThirdPerson_AnimBP AnimGraph nodes - how Speed connects - we could duplicate whole ABP and retarget
tp = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Animations/ThirdPerson_AnimBP")
unreal.log("TP abp={}".format(tp))
try:
    unreal.log("TP target_skeleton={}".format(tp.get_editor_property("target_skeleton")))
except Exception as e:
    unreal.log("TP skel ERR {}".format(e))
for prop in ["target_skeleton","TargetSkeleton","preview_skeletal_mesh","PreviewSkeletalMesh","parent_class"]:
    try:
        unreal.log("TP.{}={}".format(prop, tp.get_editor_property(prop)))
    except Exception as e:
        unreal.log("TP.{} ERR {}".format(prop, e))

# Can we SET target_skeleton on duplicated AnimBP?
dst = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    unreal.EditorAssetLibrary.delete_asset(dst)
dup = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_AnimBP", dst)
unreal.log("dup abp={}".format(dup))
if dup:
    skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
    for prop in ["target_skeleton","TargetSkeleton"]:
        try:
            dup.set_editor_property(prop, skel)
            unreal.log("dup set {} OK".format(prop))
        except Exception as e:
            unreal.log("dup set {} ERR {}".format(prop, e))
    try:
        unreal.log("dup skel now={}".format(dup.get_editor_property("target_skeleton")))
    except Exception as e:
        try:
            unreal.log("dup TargetSkeleton now={}".format(dup.get_editor_property("TargetSkeleton")))
        except Exception as e2:
            unreal.log("read ERR {} / {}".format(e, e2))

# Inspect SCS for KayKit BP
SCS = unreal.load_class(None, "/Script/Engine.SimpleConstructionScript")
unreal.log("SCS class={}".format(SCS))
if SCS:
    for obj in unreal.ObjectIterator(SCS):
        if "KayKitKnight" in obj.get_path_name():
            unreal.log("SCS obj {}".format(obj.get_path_name()))
            unreal.log("SCS methods {}".format([m for m in dir(obj) if not m.startswith("_")]))

# USCS_Node
USCS = unreal.load_class(None, "/Script/Engine.SCS_Node")
if USCS:
    n = 0
    for obj in unreal.ObjectIterator(USCS):
        if "KayKitKnight" in obj.get_path_name():
            unreal.log("SCS_Node {} class={}".format(obj.get_name(), obj.get_class().get_name()))
            n += 1
            if n > 30: break
    unreal.log("scs node count listed {}".format(n))

unreal.log("PROBE14_DONE")