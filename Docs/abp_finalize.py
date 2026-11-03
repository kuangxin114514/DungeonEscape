# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_final.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = mesh.get_editor_property("skeleton")
loco_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
fromtp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
probe_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"

loco_cls = unreal.EditorAssetLibrary.load_blueprint_class(loco_path)
L("loco_cls={}".format(loco_cls))

# BP assign
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", loco_cls)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("BP anim_class={}".format(meshc.get_editor_property("anim_class")))

# Referencers
for p in [fromtp_path, probe_path, loco_path]:
    if not unreal.EditorAssetLibrary.does_asset_exist(p):
        L("no asset {}".format(p))
        continue
    refs = unreal.EditorAssetLibrary.find_package_referencers_for_asset(p, False)
    L("refs {} -> {}".format(p, list(refs) if refs else []))

# Close editors
for p in [fromtp_path, probe_path, loco_path]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        try:
            aes.close_all_editors_for_asset(unreal.EditorAssetLibrary.load_asset(p))
        except Exception as e:
            L("close ERR {}".format(e))

# Delete probe
if unreal.EditorAssetLibrary.does_asset_exist(probe_path):
    L("delete probe -> {}".format(unreal.EditorAssetLibrary.delete_asset(probe_path)))

# Rename broken FromTP out of the way
if unreal.EditorAssetLibrary.does_asset_exist(fromtp_path):
    new_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN"
    if unreal.EditorAssetLibrary.does_asset_exist(new_path):
        unreal.EditorAssetLibrary.delete_asset(new_path)
    ok = unreal.EditorAssetLibrary.rename_asset(fromtp_path, new_path)
    L("rename FromTP -> BROKEN : {}".format(ok))
    if not ok:
        # try delete
        L("delete FromTP -> {}".format(unreal.EditorAssetLibrary.delete_asset(fromtp_path)))

# Re-open loco to ensure compile clean
loco = unreal.EditorAssetLibrary.load_asset(loco_path)
# ensure skeleton + BS
loco.set_editor_property("target_skeleton", skel)
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
jump_loop = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_land = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
jump_full = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig")

EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
for obj in unreal.ObjectIterator(EdGraphNode):
    pn = obj.get_path_name()
    if "ABP_KayKitLocomotion" not in pn or "Default__" in pn or "AnimPreview" in pn:
        continue
    cn = obj.get_class().get_name()
    try:
        if cn == "AnimGraphNode_BlendSpacePlayer":
            node = obj.get_editor_property("node")
            for n in ["blend_space", "BlendSpace"]:
                try: node.set_editor_property(n, bs)
                except Exception: pass
        elif cn == "AnimGraphNode_SequencePlayer":
            node = obj.get_editor_property("node")
            seq = node.get_editor_property("sequence")
            name = (seq.get_name() if seq else "").lower()
            if "start" in name: node.set_editor_property("sequence", jump_start)
            elif "land" in name or "end" in name: node.set_editor_property("sequence", jump_land)
            elif "loop" in name or ("jump" in name and "idle" in name): node.set_editor_property("sequence", jump_loop)
            elif "jump" in name: node.set_editor_property("sequence", jump_full)
            elif "run" in name: node.set_editor_property("sequence", run)
            elif "walk" in name: node.set_editor_property("sequence", walk)
            elif "idle" in name: node.set_editor_property("sequence", idle)
    except Exception as e:
        L("node ERR {}".format(e))

unreal.EditorAssetLibrary.save_asset(loco_path, only_if_is_dirty=False)
aes.open_editor_for_assets([loco])
time.sleep(3)
unreal.EditorAssetLibrary.save_asset(loco_path, only_if_is_dirty=False)
aes.close_all_editors_for_asset(loco)

# Re-assign BP after possible class regen
loco_cls = unreal.EditorAssetLibrary.load_blueprint_class(loco_path)
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("anim_class", loco_cls)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("skeletal_mesh", mesh)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)

L("FINAL anim_class={}".format(meshc.get_editor_property("anim_class")))
L("fromtp exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(fromtp_path)))
L("broken exists={}".format(unreal.EditorAssetLibrary.does_asset_exist("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN")))
L("probe exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(probe_path)))
L("loco exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(loco_path)))
L("bs skel={}".format(bs.get_editor_property("skeleton").get_name()))
L("loco target={}".format(loco.get_editor_property("target_skeleton").get_name()))

flush()
