# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

dest_dir = "/Game/Characters/Player/KayKit/Animations"
if not unreal.EditorAssetLibrary.does_directory_exist(dest_dir):
    unreal.EditorAssetLibrary.make_directory(dest_dir)

bs_dest = dest_dir + "/BS_KayKitLocomotion"
abp_dest = dest_dir + "/ABP_KayKitKnight"

for p in [bs_dest, abp_dest]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        unreal.EditorAssetLibrary.delete_asset(p)
        unreal.log("deleted " + p)

# duplicate_asset(source, dest_with_name)
bs_ok = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D", bs_dest)
unreal.log("dup bs -> {}".format(bs_ok))
bs2 = unreal.EditorAssetLibrary.load_asset(bs_dest)
if not bs2:
    unreal.log("FAIL no bs2")
else:
    bs2.set_editor_property("skeleton", skel)
    new_samples = []
    for anim, x in [(idle, 0.0), (walk, 250.0), (run, 500.0)]:
        s = unreal.BlendSample()
        s.set_editor_property("animation", anim)
        s.set_editor_property("sample_value", unreal.Vector(x, 0.0, 0.0))
        try:
            s.set_editor_property("rate_scale", 1.0)
        except Exception:
            pass
        new_samples.append(s)
    bs2.set_editor_property("sample_data", new_samples)
    params = bs2.get_editor_property("blend_parameters")
    p0 = params[0]
    p0.set_editor_property("display_name", "Speed")
    p0.set_editor_property("min", 0.0)
    p0.set_editor_property("max", 600.0)
    p0.set_editor_property("grid_num", 4)
    params[0] = p0
    bs2.set_editor_property("blend_parameters", params)
    unreal.EditorAssetLibrary.save_asset(bs_dest)
    unreal.log("BS READY skel={} samples={}".format(
        bs2.get_editor_property("skeleton").get_name(),
        [s.get_editor_property("animation").get_name() for s in bs2.get_editor_property("sample_data")]
    ))

abp_ok = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_AnimBP", abp_dest)
unreal.log("dup abp -> {}".format(abp_ok))
abp = unreal.EditorAssetLibrary.load_asset(abp_dest)
if not abp:
    unreal.log("FAIL no abp")
else:
    try:
        abp.set_editor_property("target_skeleton", skel)
        unreal.log("abp target_skeleton set")
    except Exception as e:
        unreal.log("abp skeleton ERR {}".format(e))

    # Replace blendspace references inside AnimGraph nodes
    AnimGraphNode_BlendSpacePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")
    replaced = 0
    for obj in unreal.ObjectIterator(AnimGraphNode_BlendSpacePlayer):
        if "ABP_KayKitKnight" not in obj.get_path_name():
            continue
        unreal.log("found BSP {}".format(obj.get_path_name()))
        try:
            node = obj.get_editor_property("node")
            unreal.log("  inner={}".format(node))
            # try common property names
            for pn in ["blend_space_asset","BlendSpaceAsset","blend_space","BlendSpace"]:
                try:
                    old = node.get_editor_property(pn)
                    unreal.log("  node.{}={}".format(pn, old))
                    node.set_editor_property(pn, bs2)
                    unreal.log("  set {} OK".format(pn))
                    replaced += 1
                except Exception as e:
                    unreal.log("  node.{} ERR {}".format(pn, e))
            # also try on the graph node itself
            for pn in ["blend_space_asset","BlendSpaceAsset"]:
                try:
                    old = obj.get_editor_property(pn)
                    unreal.log("  obj.{}={}".format(pn, old))
                    obj.set_editor_property(pn, bs2)
                    unreal.log("  obj set {} OK".format(pn))
                    replaced += 1
                except Exception as e:
                    unreal.log("  obj.{} ERR {}".format(pn, e))
        except Exception as e:
            unreal.log("BSP inspect ERR {}".format(e))
    unreal.log("replaced={}".format(replaced))

    # Also fix any SequencePlayers referencing mannequin anims if needed - jump etc.
    AnimGraphNode_SequencePlayer = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
    for obj in unreal.ObjectIterator(AnimGraphNode_SequencePlayer):
        if "ABP_KayKitKnight" not in obj.get_path_name():
            continue
        try:
            node = obj.get_editor_property("node")
            seq = node.get_editor_property("sequence")
            unreal.log("SEQPLAYER seq={}".format(seq))
            if seq:
                name = seq.get_name()
                # map jump-ish to KayKit jump if present
                mapping = {
                    "ThirdPersonIdle": idle,
                    "ThirdPersonWalk": walk,
                    "ThirdPersonRun": run,
                    "ThirdPersonJump_Start": unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start"),
                    "ThirdPersonJump_Loop": unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle"),
                    "ThirdPersonJump_End": unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land"),
                    "ThirdPerson_Jump": unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short"),
                }
                if name in mapping and mapping[name]:
                    node.set_editor_property("sequence", mapping[name])
                    unreal.log("  remapped {} -> {}".format(name, mapping[name].get_name()))
        except Exception as e:
            unreal.log("SEQPLAYER ERR {}".format(e))

    unreal.EditorAssetLibrary.save_asset(abp_dest)
    unreal.log("ABP SAVED")

# Assign ABP to BP_KayKitKnight mesh
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
cdo = unreal.get_default_object(bp_cls)
mesh = cdo.get_editor_property("mesh")
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_dest)
unreal.log("abp_cls={}".format(abp_cls))
mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh.set_editor_property("anim_class", abp_cls)
unreal.log("mesh mode={} anim_class={}".format(
    mesh.get_editor_property("animation_mode"),
    mesh.get_editor_property("anim_class")
))

# compile BP
try:
    unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
except Exception as e:
    unreal.log("save bp ERR {}".format(e))

# try compile utilities
for name in ["KismetEditorUtilities","BlueprintEditorLibrary"]:
    unreal.log("has {} {}".format(name, hasattr(unreal, name)))

# cleanup probe
probe = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe"
if unreal.EditorAssetLibrary.does_asset_exist(probe):
    try:
        unreal.EditorAssetLibrary.delete_asset(probe)
        unreal.log("deleted probe")
    except Exception as e:
        unreal.log("del probe ERR {}".format(e))

unreal.log("SETUP_LOCOMOTION_DONE")