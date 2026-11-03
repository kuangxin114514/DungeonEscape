# -*- coding: utf-8 -*-
import unreal

folder = "/Game/Characters/Player/KayKit/Animations"
bs_path = folder + "/BS_KayKitLocomotion"
abp_path = folder + "/ABP_KayKitFromTP"
alias_path = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mat_path = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"

# Reload assets from disk
try:
    unreal.EditorAssetLibrary.sync_browser_to_objects([bs_path])
except Exception as e:
    unreal.log("sync ERR {}".format(e))

# Force reload by unload if available
try:
    # Package reload
    pkgs = ["/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"]
    unreal.EditorLoadingAndSavingUtils.reload_packages  # attr check
except Exception:
    pass

# Try AssetRegistry scan
try:
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    reg.scan_paths_synchronous(["/Game/Characters/Player/KayKit/Animations"], True)
    unreal.log("scanned")
except Exception as e:
    unreal.log("scan ERR {}".format(e))

# Load and check BS skeleton - may still be memory-cached
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
unreal.log("bs skel={}".format(bs.get_editor_property("skeleton") if bs else None))

alias = unreal.EditorAssetLibrary.load_asset(alias_path)
orig_skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
unreal.log("alias={} orig={}".format(alias, orig_skel))

# If still mannequin, try using EditorAssetLibrary to explicitly find
skel_name = bs.get_editor_property("skeleton").get_name() if bs else "?"
unreal.log("skel_name={}".format(skel_name))

# Set ABP to alias skeleton (must match BS)
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
if "KayKit" in skel_name or "XXXXXX" in skel_name:
    abp.set_editor_property("target_skeleton", alias)
    use_skel = alias
    unreal.log("ABP -> alias")
else:
    # Patch didn't take in memory; set ABP to orig and hope we can still assign
    abp.set_editor_property("target_skeleton", orig_skel)
    use_skel = orig_skel
    unreal.log("ABP -> orig (patch not visible in memory yet)")

# Update jump SequencePlayers to KayKit jump anims if present
jump = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
# list jump-related
mesh_assets = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Mesh", False, False)
jumps = [p for p in mesh_assets if "Jump" in p and p.endswith("_Rig")]
unreal.log("jumps={}".format(jumps))

EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
for obj in unreal.ObjectIterator(EdGraphNode):
    p = obj.get_path_name()
    if "ABP_KayKitFromTP" not in p:
        continue
    if obj.get_class().get_name() != "AnimGraphNode_SequencePlayer":
        continue
    try:
        node = obj.get_editor_property("Node")
        seq = node.get_editor_property("sequence")
        unreal.log("SeqPlayer {} seq={}".format(obj.get_name(), seq.get_name() if seq else None))
        # Replace mannequin jump anims with KayKit Jump_Idle as safe loop
        if seq and "ThirdPerson" in seq.get_path_name():
            if jump:
                node.set_editor_property("sequence", jump)
                unreal.log("  replaced with Jump_Idle_Rig")
    except Exception as e:
        unreal.log("SeqPlayer ERR {}".format(e))

# Verify BSP points to our BS
for obj in unreal.ObjectIterator(EdGraphNode):
    p = obj.get_path_name()
    if "ABP_KayKitFromTP" in p and obj.get_class().get_name() == "AnimGraphNode_BlendSpacePlayer":
        node = obj.get_editor_property("Node")
        bso = node.get_editor_property("blend_space")
        unreal.log("BSP blend_space={}".format(bso.get_path_name() if bso else None))

# Assign AnimBP to character mesh (and set skeleton on mesh to match if needed)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
mesh_comp = cdo.get_editor_property("mesh")
unreal.log("before mode={} anim_class={} anim_to_play={}".format(
    mesh_comp.get_editor_property("animation_mode"),
    mesh_comp.get_editor_property("anim_class"),
    mesh_comp.get_editor_property("animation")))

# Load generated anim class
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
unreal.log("abp_cls={}".format(abp_cls))

mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh_comp.set_editor_property("anim_class", abp_cls)

# Keep skeletal mesh asset
sk_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
mesh_comp.set_editor_property("skeletal_mesh", sk_mesh)

# Material
mat = unreal.EditorAssetLibrary.load_asset(mat_path)
try:
    # override materials on component
    mesh_comp.set_editor_property("override_materials", [mat])
except Exception as e:
    unreal.log("mat override ERR {}".format(e))

unreal.log("after mode={} anim_class={}".format(
    mesh_comp.get_editor_property("animation_mode"),
    mesh_comp.get_editor_property("anim_class")))

# If BS still mannequin in memory, try to set skeleton by reloading package from file
# Compile ABP
try:
    unreal.EditorAssetLibrary.save_asset(abp_path)
except Exception as e:
    unreal.log("save abp ERR {}".format(e))

# Save character BP
unreal.EditorAssetLibrary.save_asset(bp_path)

# Confirm GM_Hub default pawn
gm = unreal.EditorAssetLibrary.load_asset("/Game/Core/GameFlow/GM_Hub")
if gm:
    gm_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Core/GameFlow/GM_Hub")
    gm_cdo = unreal.get_default_object(gm_cls)
    try:
        unreal.log("GM default_pawn={}".format(gm_cdo.get_editor_property("default_pawn_class")))
    except Exception as e:
        unreal.log("GM pawn ERR {}".format(e))

# Re-read BS skeleton after suggesting package reload via load_package
try:
    pkg = unreal.load_package(None, "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion", 0)
    unreal.log("pkg={}".format(pkg))
except Exception as e:
    unreal.log("load_package ERR {}".format(e))

bs2 = unreal.EditorAssetLibrary.load_asset(bs_path)
unreal.log("bs2 skel={}".format(bs2.get_editor_property("skeleton") if bs2 else None))

# Also set mesh asset's skeleton to alias if BS uses alias - so they match
if bs2:
    sn = bs2.get_editor_property("skeleton").get_path_name()
    if "KayKitKnightSkelXXXXXX" in sn:
        try:
            sk_mesh.set_editor_property("skeleton", alias)
            unreal.log("mesh skeleton -> alias OK")
            unreal.EditorAssetLibrary.save_asset(mesh_path)
        except Exception as e:
            unreal.log("mesh skel ERR {}".format(e))
        abp.set_editor_property("target_skeleton", alias)
        unreal.EditorAssetLibrary.save_asset(abp_path)

unreal.log("WIRE_DONE")