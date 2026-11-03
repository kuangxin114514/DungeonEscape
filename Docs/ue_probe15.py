# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
folder = "/Game/Characters/Player/KayKit/Animations"

# Inspect ThirdPerson_IdleRun_2D class and sample properties
bs_src = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D")
unreal.log("bs_src class={}".format(bs_src.get_class().get_name()))
for prop in ["skeleton","BlendSamples","SampleData","blend_samples","sample_data","BlendParameters","InterpolationParam"]:
    try:
        v = bs_src.get_editor_property(prop)
        unreal.log("bs_src.{}={}".format(prop, v))
    except Exception as e:
        unreal.log("bs_src.{} ERR {}".format(prop, e))

# Duplicate BS and inspect
dst_bs = folder + "/BS_KayKitLocomotion"
if unreal.EditorAssetLibrary.does_asset_exist(dst_bs):
    unreal.EditorAssetLibrary.delete_asset(dst_bs)
# Also delete 2D leftover
if unreal.EditorAssetLibrary.does_asset_exist(folder + "/BS_KayKitLocomotion2D"):
    unreal.EditorAssetLibrary.delete_asset(folder + "/BS_KayKitLocomotion2D")

bs = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D", dst_bs)
unreal.log("bs dup class={} path={}".format(bs.get_class().get_name() if bs else None, bs))

if bs:
    for prop in ["BlendSamples","SampleData","blend_samples","sample_data","Skeleton","skeleton"]:
        try:
            v = bs.get_editor_property(prop)
            unreal.log("bs.{} type={} val={}".format(prop, type(v).__name__, v))
            if hasattr(v, "__iter__") and not isinstance(v, (str, bytes)):
                for i, item in enumerate(list(v)[:8]):
                    unreal.log("  [{}] {} type={}".format(i, item, type(item).__name__))
                    for ip in ["Animation","animation","SampleValue","sample_value","Left","Right"]:
                        try:
                            unreal.log("    .{}={}".format(ip, item.get_editor_property(ip) if hasattr(item,"get_editor_property") else getattr(item, ip, "no")))
                        except Exception as e:
                            try:
                                unreal.log("    .{}={}".format(ip, getattr(item, ip)))
                            except Exception as e2:
                                unreal.log("    .{} ERR {}".format(ip, e))
        except Exception as e:
            unreal.log("bs.{} ERR {}".format(prop, e))

# Export BS to T3D text
try:
    task = unreal.AssetExportTask()
    task.set_editor_property("automated", True)
    task.set_editor_property("prompt", False)
    task.set_editor_property("object", bs if bs else bs_src)
    task.set_editor_property("filename", r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\bs_export.t3d")
    task.set_editor_property("exporter", unreal.ObjectExporterT3D())
    ok = unreal.Exporter.run_asset_export_task(task)
    unreal.log("export ok={}".format(ok))
except Exception as e:
    unreal.log("export ERR {}".format(e))

# Fix ABP_KayKitFromTP - set preview mesh, compile
abp_path = folder + "/ABP_KayKitFromTP"
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
if abp:
    try:
        abp.set_editor_property("target_skeleton", skel)
        unreal.log("abp skel set")
    except Exception as e:
        unreal.log("abp skel ERR {}".format(e))
    # preview mesh protected - try
    try:
        abp.set_editor_property("PreviewSkeletalMesh", mesh)
    except Exception as e:
        unreal.log("preview ERR {}".format(e))

    # Find BlendSpacePlayer nodes and list their blendspace
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    for obj in unreal.ObjectIterator(EdGraphNode):
        p = obj.get_path_name()
        if "ABP_KayKitFromTP" in p and "AnimGraph" in p:
            cn = obj.get_class().get_name()
            if "Blend" in cn or "Sequence" in cn or "State" in cn or "Root" in cn:
                unreal.log("NODE {} {}".format(cn, obj.get_name()))
                try:
                    node = obj.get_editor_property("Node")
                    unreal.log("  Node={}".format(node))
                    for np in ["BlendSpace","blend_space","Sequence","sequence","X","Y","GroupName"]:
                        try:
                            unreal.log("  .{}={}".format(np, node.get_editor_property(np) if hasattr(node,"get_editor_property") else getattr(node,np,None)))
                        except Exception:
                            try:
                                unreal.log("  .{}={}".format(np, getattr(node, np)))
                            except Exception:
                                pass
                except Exception as e:
                    unreal.log("  Node ERR {}".format(e))

unreal.log("PROBE15_DONE")