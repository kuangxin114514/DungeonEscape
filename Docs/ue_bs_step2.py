# -*- coding: utf-8 -*-
import unreal
import os

folder = "/Game/Characters/Player/KayKit/Animations"
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
bs_path = folder + "/BS_KayKitLocomotion"
bs = unreal.EditorAssetLibrary.load_asset(bs_path)

# Try import T3D as new asset name
t3d = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\BS_KayKitLocomotion_import.t3d"
task = unreal.AssetImportTask()
task.set_editor_property("filename", t3d)
task.set_editor_property("destination_path", folder)
task.set_editor_property("destination_name", "BS_KayKitLocoImported")
task.set_editor_property("replace_existing", True)
task.set_editor_property("automated", True)
task.set_editor_property("save", True)
try:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.log("import paths={}".format(task.get_editor_property("imported_object_paths")))
except Exception as e:
    unreal.log("import ERR {}".format(e))

imp = unreal.EditorAssetLibrary.load_asset(folder + "/BS_KayKitLocoImported")
unreal.log("imported={}".format(imp))
if imp:
    try:
        unreal.log("imp class={} skel={}".format(imp.get_class().get_name(), imp.get_editor_property("skeleton")))
    except Exception as e:
        unreal.log("imp read ERR {}".format(e))

# Binary patch approach with SAME length:
# Mannequin path string in asset may appear as full soft path
man = "/Game/Mannequin/Character/Mesh/UE4_Mannequin_Skeleton"
# Build alias with EXACT same length
pad = len(man) - len("/Game/Mannequin/Character/Mesh/")
name = ("KayKitKnightSkel" + "X" * 20)[:pad]
alias_path = "/Game/Mannequin/Character/Mesh/" + name
unreal.log("man len={} alias len={} alias={}".format(len(man), len(alias_path), alias_path))

if unreal.EditorAssetLibrary.does_asset_exist(alias_path):
    unreal.EditorAssetLibrary.delete_asset(alias_path)
# delete wrong shorter alias if exists
old = "/Game/Mannequin/Character/Mesh/KayKitKnightSkeleton"
# keep old for now

dsk = unreal.EditorAssetLibrary.duplicate_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton", alias_path)
unreal.log("alias skel={}".format(dsk))

# Save and unload BS for patching
unreal.EditorAssetLibrary.save_asset(bs_path)

# Also try: make KayKit skeleton list Mannequin as compatible AND vice versa; assign BS (mannequin skel) to ABP (kaykit) - may still fail compile
try:
    compat = skel.get_editor_property("compatible_skeletons")
    unreal.log("kaykit compat={}".format(compat))
except Exception as e:
    unreal.log("compat ERR {}".format(e))
for prop in ["compatible_skeletons","CompatibleSkeletons"]:
    try:
        man_skel = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Character/Mesh/UE4_Mannequin_Skeleton")
        skel.set_editor_property(prop, [man_skel])
        unreal.log("set {} OK".format(prop))
    except Exception as e:
        unreal.log("set {} ERR {}".format(prop, e))

# Update ABP BlendSpacePlayer to use our BS (even with mannequin skel tag but kaykit samples)
abp = unreal.EditorAssetLibrary.load_asset(folder + "/ABP_KayKitFromTP")
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
bsp_nodes = []
seq_nodes = []
for obj in unreal.ObjectIterator(EdGraphNode):
    p = obj.get_path_name()
    if "ABP_KayKitFromTP" not in p:
        continue
    cn = obj.get_class().get_name()
    if cn == "AnimGraphNode_BlendSpacePlayer":
        bsp_nodes.append(obj)
    if cn == "AnimGraphNode_SequencePlayer":
        seq_nodes.append(obj)

unreal.log("bsp_nodes={} seq_nodes={}".format(len(bsp_nodes), len(seq_nodes)))
for obj in bsp_nodes:
    try:
        node = obj.get_editor_property("Node")
        unreal.log("BSP Node dir={}".format([x for x in dir(node) if not x.startswith("_")]))
        for prop in ["BlendSpace","blend_space","X","Y","GroupName","bLoop"]:
            try:
                unreal.log("  {}={}".format(prop, node.get_editor_property(prop)))
            except Exception as e:
                unreal.log("  {} ERR {}".format(prop, e))
        # Set blend space to our BS
        try:
            node.set_editor_property("BlendSpace", bs)
            unreal.log("set BlendSpace OK")
        except Exception as e:
            unreal.log("set BlendSpace ERR {}".format(e))
        try:
            node.set_editor_property("blend_space", bs)
            unreal.log("set blend_space OK")
        except Exception as e:
            unreal.log("set blend_space ERR {}".format(e))
    except Exception as e:
        unreal.log("BSP ERR {}".format(e))

# Replace jump sequence players with KayKit idle as safe placeholders? Optional.
# Ensure ABP uses KayKit skeleton
abp.set_editor_property("target_skeleton", skel)
unreal.EditorAssetLibrary.save_asset(folder + "/ABP_KayKitFromTP")
unreal.EditorAssetLibrary.save_asset(bs_path)
unreal.log("STEP2_DONE")