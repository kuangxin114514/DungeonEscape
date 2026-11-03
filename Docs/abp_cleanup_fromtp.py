# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_cleanup_result.txt"
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
knight_abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"

loco_cls = unreal.EditorAssetLibrary.load_blueprint_class(loco_path)
L("loco_cls={}".format(loco_cls))

# Ensure BP uses locomotion only
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", loco_cls)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("BP anim_class={}".format(meshc.get_editor_property("anim_class")))

# Find any other skeletal mesh components / blueprints referencing FromTP
fromtp_cls = unreal.load_object(None, fromtp_path + ".ABP_KayKitFromTP_C")
L("fromtp_cls={}".format(fromtp_cls))

# Search assets that reference FromTP
deps = unreal.EditorAssetLibrary.find_package_referencers_for_asset(fromtp_path, load_assets_to_confirm=False)
L("FromTP referencers count={}".format(len(deps) if deps else 0))
for d in (deps or []):
    L("  ref {}".format(d))

# Close editors and unload FromTP package then delete
for p in [fromtp_path, probe_path]:
    if not unreal.EditorAssetLibrary.does_asset_exist(p):
        L("missing {}".format(p))
        continue
    try:
        a = unreal.EditorAssetLibrary.load_asset(p)
        aes.close_all_editors_for_asset(a)
    except Exception as e:
        L("close {} {}".format(p, e))

# Unload packages
pkgs = []
for p in [fromtp_path, probe_path]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        pkg = unreal.load_package(None, p)
        if pkg:
            pkgs.append(pkg)
            L("pkg {}".format(pkg))
if pkgs:
    try:
        unreal.EditorLoadingAndSavingUtils.unload_packages(pkgs)
        L("unloaded {}".format(len(pkgs)))
    except Exception as e:
        L("unload ERR {}".format(e))

time.sleep(0.5)

# Delete probe (safe) and FromTP
for p in [probe_path, fromtp_path]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        ok = unreal.EditorAssetLibrary.delete_asset(p)
        L("delete {} -> {}".format(p, ok))
    else:
        L("already gone {}".format(p))

# If FromTP still exists, try to repair it so PIE won't fail: set skeleton + BS + open compile
# OR replace its generated class by renaming loco over it - can't.
# Last resort: create empty factory ABP on top? 

if unreal.EditorAssetLibrary.does_asset_exist(fromtp_path):
    L("FromTP still exists - attempting repair")
    abp = unreal.EditorAssetLibrary.load_asset(fromtp_path)
    abp.set_editor_property("target_skeleton", skel)
    bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
    idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
    jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
    jump_loop = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
    jump_land = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
    jump_full = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig")
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    for obj in unreal.ObjectIterator(EdGraphNode):
        if "ABP_KayKitFromTP" not in obj.get_path_name():
            continue
        if "Default__" in obj.get_path_name() or "AnimPreview" in obj.get_path_name():
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
                elif "loop" in name or "idle" in name and "jump" in name: node.set_editor_property("sequence", jump_loop)
                elif "jump" in name: node.set_editor_property("sequence", jump_full)
                else: node.set_editor_property("sequence", idle)
        except Exception as e:
            L("repair node ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(fromtp_path, only_if_is_dirty=False)
    aes.open_editor_for_assets([abp])
    time.sleep(3)
    unreal.EditorAssetLibrary.save_asset(fromtp_path, only_if_is_dirty=False)
    aes.close_all_editors_for_asset(abp)
    L("repaired FromTP open/close done")

# Final BP check
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
L("FINAL BP anim={} mesh={}".format(meshc.get_editor_property("anim_class"), meshc.get_editor_property("skeletal_mesh")))

# Confirm loco still good
L("loco exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(loco_path)))
L("fromtp exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(fromtp_path)))
L("probe exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(probe_path)))

flush()
