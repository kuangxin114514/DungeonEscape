# -*- coding: utf-8 -*-
import unreal

abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
alias_path = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"

# Compile AnimBP
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
try:
    unreal.KismetEditorUtilities.compile_blueprint(abp)
    unreal.log("compile_blueprint OK")
except Exception as e:
    unreal.log("compile_blueprint ERR {}".format(e))

# Check generated class still valid
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
unreal.log("abp_cls={}".format(abp_cls))
unreal.log("abp target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))

# Status
try:
    status = abp.get_editor_property("status")
    unreal.log("abp status={}".format(status))
except Exception as e:
    unreal.log("status ERR {}".format(e))

# Inspect Event Graph for Speed variable / velocity logic (from ThirdPerson)
# Look for AnimBlueprint variables
try:
    # generated class defaults
    cdo = unreal.get_default_object(abp_cls)
    unreal.log("abp cdo={}".format(cdo))
    for prop in ["speed", "Speed", "direction", "Direction", "pitch", "roll"]:
        try:
            unreal.log("  {}={}".format(prop, cdo.get_editor_property(prop)))
        except Exception:
            pass
except Exception as e:
    unreal.log("cdo ERR {}".format(e))

# Check BP_KayKitKnight for sword/shield - via Blueprint asset subobjects / simple construction
bp_asset = unreal.EditorAssetLibrary.load_asset(bp_path)
# Try get_editor_property components on Blueprint
for prop in ["simple_construction_script", "SimpleConstructionScript", "inherited_scsc", "ubergraph_pages"]:
    try:
        v = bp_asset.get_editor_property(prop)
        unreal.log("bp.{}={}".format(prop, v))
    except Exception as e:
        unreal.log("bp.{} ERR".format(prop))

# Iterate all objects under BP package looking for StaticMeshComponent templates
count_sm = 0
sword = shield = None
for obj in unreal.ObjectIterator(unreal.StaticMeshComponent):
    p = obj.get_path_name()
    if "BP_KayKitKnight" not in p:
        continue
    count_sm += 1
    sm = None
    try:
        sm = obj.get_editor_property("static_mesh")
    except Exception:
        pass
    unreal.log("SMC {} mesh={} socket?".format(obj.get_name(), sm.get_name() if sm else None))
    try:
        # attach socket
        unreal.log("  attach_socket={}".format(obj.get_editor_property("attach_socket_name")))
    except Exception:
        pass
    if sm:
        n = sm.get_name().lower()
        if "sword" in n: sword = obj
        if "shield" in n: shield = obj

unreal.log("SMC count={} sword={} shield={}".format(count_sm, sword, shield))

# Also skeletal mesh component materials
for obj in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    p = obj.get_path_name()
    if "BP_KayKitKnight" not in p:
        continue
    unreal.log("SkelMC {} mode={} anim_class={} mesh={}".format(
        obj.get_name(),
        obj.get_editor_property("animation_mode"),
        obj.get_editor_property("anim_class"),
        obj.get_editor_property("skeletal_mesh")))
    try:
        unreal.log("  override_materials={}".format(obj.get_editor_property("override_materials")))
    except Exception as e:
        unreal.log("  mats ERR {}".format(e))

# Save all
unreal.EditorAssetLibrary.save_asset(abp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)
unreal.EditorAssetLibrary.save_asset(bs_path)
unreal.EditorAssetLibrary.save_asset(alias_path)

# GM check
gm_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Core/GameFlow/GM_Hub")
gm_cdo = unreal.get_default_object(gm_cls)
unreal.log("GM pawn={}".format(gm_cdo.get_editor_property("default_pawn_class")))

unreal.log("VERIFY_DONE")