# -*- coding: utf-8 -*-
import unreal

abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
abp = unreal.EditorAssetLibrary.load_asset(abp_path)

# Find compile helpers
hits = [n for n in dir(unreal) if "lueprint" in n.lower() or "AnimBlueprint" in n]
unreal.log("hits={}".format(hits))

# Try AssetEditorSubsystem open then save (triggers compile)
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    unreal.log("AES {}".format([n for n in dir(aes) if not n.startswith("_") and ("open" in n.lower() or "compile" in n.lower() or "save" in n.lower() or "close" in n.lower())]))
    aes.open_editor_for_assets([abp])
    unreal.log("opened ABP editor")
except Exception as e:
    unreal.log("AES ERR {}".format(e))

# AnimBlueprint specific - regenerate class
try:
    # Some versions: abp.status
    for prop in ["status", "blueprint_system_version", "is_regenerating_on_load", "generated_class"]:
        try:
            unreal.log("{}={}".format(prop, abp.get_editor_property(prop)))
        except Exception as e:
            unreal.log("{} ERR".format(prop))
except Exception:
    pass

# Touch and save BS + ABP + BP
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
# Re-confirm BSP
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
for obj in unreal.ObjectIterator(EdGraphNode):
    if "ABP_KayKitFromTP" not in obj.get_path_name():
        continue
    cn = obj.get_class().get_name()
    if cn == "AnimGraphNode_BlendSpacePlayer":
        node = obj.get_editor_property("Node")
        bso = node.get_editor_property("blend_space")
        unreal.log("BSP -> {}".format(bso.get_path_name() if bso else None))
    if cn == "AnimGraphNode_StateMachine":
        unreal.log("StateMachine node present {}".format(obj.get_name()))

# Character max speed vs blend space axis (0-375)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
cdo = unreal.get_default_object(bp_cls)
try:
    cm = cdo.get_editor_property("character_movement")
    unreal.log("max_walk_speed={}".format(cm.get_editor_property("max_walk_speed")))
except Exception as e:
    unreal.log("move ERR {}".format(e))

# Save all kaykit anim folder
unreal.EditorAssetLibrary.save_directory("/Game/Characters/Player/KayKit")
unreal.EditorAssetLibrary.save_directory("/Game/Mannequin/Character/Mesh")

unreal.log("POST_DONE")