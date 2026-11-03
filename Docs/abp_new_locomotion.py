# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_new_result.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")

mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = mesh.get_editor_property("skeleton")
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
jump_loop = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_land = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
jump_full = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig")

src = "/Game/Mannequin/Animations/ThirdPerson_AnimBP"
dst_dir = "/Game/Characters/Player/KayKit/Animations"
dst_name = "ABP_KayKitLocomotion"
dst = dst_dir + "/" + dst_name

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)

# If exists, delete if possible
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    try:
        a = unreal.EditorAssetLibrary.load_asset(dst)
        aes.close_all_editors_for_asset(a)
    except Exception:
        pass
    ok = unreal.EditorAssetLibrary.delete_asset(dst)
    L("delete existing new abp -> {}".format(ok))

dup = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
L("duplicate -> {}".format(dup))
if dup is None:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    src_obj = unreal.EditorAssetLibrary.load_asset(src)
    dup = tools.duplicate_asset(dst_name, dst_dir, src_obj)
    L("tools.duplicate -> {}".format(dup))

abp = unreal.EditorAssetLibrary.load_asset(dst)
if not abp:
    L("FAIL load dst")
    flush()
    raise SystemExit(0)

abp.set_editor_property("target_skeleton", skel)
L("target set")

def pick_seq(name):
    if not name:
        return jump_loop
    n = name.lower()
    # order matters: jump_idle before idle
    if "jump_start" in n or ("jump" in n and "start" in n):
        return jump_start
    if "jump_land" in n or "jump_end" in n or ("land" in n):
        return jump_land
    if "jump_loop" in n or "jump_idle" in n or ("jump" in n and "idle" in n):
        return jump_loop
    if "jump_full" in n or ("jump" in n and "full" in n):
        return jump_full
    if "jump" in n:
        return jump_full
    if "run" in n:
        return run
    if "walk" in n:
        return walk
    if "idle" in n:
        return idle
    return jump_loop

EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
for obj in unreal.ObjectIterator(EdGraphNode):
    pn = obj.get_path_name()
    if dst_name not in pn:
        continue
    if "Default__" in pn or "AnimPreview" in pn:
        continue
    cn = obj.get_class().get_name()
    try:
        if cn == "AnimGraphNode_BlendSpacePlayer":
            node = obj.get_editor_property("node")
            for n in ["blend_space", "BlendSpace", "blend_space_asset", "BlendSpaceAsset"]:
                try:
                    node.set_editor_property(n, bs)
                except Exception:
                    pass
            L("BSP set {}".format(obj.get_name()))
        elif cn == "AnimGraphNode_SequencePlayer":
            node = obj.get_editor_property("node")
            seq = node.get_editor_property("sequence")
            name = seq.get_name() if seq else None
            new_seq = pick_seq(name)
            node.set_editor_property("sequence", new_seq)
            L("SP {} {} -> {}".format(obj.get_name(), name, new_seq.get_name()))
    except Exception as e:
        L("ERR {} {}".format(obj.get_name(), e))

unreal.EditorAssetLibrary.save_asset(dst, only_if_is_dirty=False)
L("saved")

# Open longer to compile
aes.open_editor_for_assets([abp])
time.sleep(4.0)
unreal.EditorAssetLibrary.save_asset(dst, only_if_is_dirty=False)
aes.close_all_editors_for_asset(abp)
L("compiled via open")

# Load generated class
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(dst)
L("abp_cls={}".format(abp_cls))
if abp_cls is None:
    abp_cls = unreal.load_object(None, dst + "." + dst_name + "_C")
    L("load_object gen={}".format(abp_cls))

# Assign to BP
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
if abp_cls:
    meshc.set_editor_property("anim_class", abp_cls)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("BP anim_class={} mode={}".format(meshc.get_editor_property("anim_class"), meshc.get_editor_property("animation_mode")))

# Verify
abp2 = unreal.EditorAssetLibrary.load_asset(dst)
L("verify target={} same={}".format(
    abp2.get_editor_property("target_skeleton").get_path_name(),
    abp2.get_editor_property("target_skeleton") == skel))
for obj in unreal.ObjectIterator(EdGraphNode):
    if dst_name not in obj.get_path_name() or "Default__" in obj.get_path_name() or "AnimPreview" in obj.get_path_name():
        continue
    cn = obj.get_class().get_name()
    if cn == "AnimGraphNode_BlendSpacePlayer":
        node = obj.get_editor_property("node")
        bsa = None
        for n in ["blend_space", "BlendSpace"]:
            try:
                bsa = node.get_editor_property(n)
                if bsa: break
            except Exception:
                pass
        bskel = bsa.get_editor_property("skeleton").get_path_name() if bsa else None
        L("V BSP {} {}".format(bsa.get_name() if bsa else None, bskel == skel.get_path_name()))
    elif cn == "AnimGraphNode_SequencePlayer":
        node = obj.get_editor_property("node")
        seq = node.get_editor_property("sequence")
        ok = seq and seq.get_editor_property("skeleton") == skel
        L("V SP {} ok={}".format(seq.get_name() if seq else None, ok))

flush()
