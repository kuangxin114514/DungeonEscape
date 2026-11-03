# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_recreate_result.txt"
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

# Fix BS samples to sensible speeds matching default MaxWalkSpeed ~600 but param max 600
# Keep max at 600 to match character; walk around 200
new_samples = []
for anim, x in [(idle, 0.0), (walk, 200.0), (run, 500.0)]:
    s = unreal.BlendSample()
    s.set_editor_property("animation", anim)
    s.set_editor_property("sample_value", unreal.Vector(x, 0.0, 0.0))
    try:
        s.set_editor_property("rate_scale", 1.0)
    except Exception:
        pass
    new_samples.append(s)
bs.set_editor_property("sample_data", new_samples)
params = list(bs.get_editor_property("blend_parameters"))
if params:
    p0 = params[0]
    p0.set_editor_property("display_name", "Speed")
    p0.set_editor_property("min", 0.0)
    p0.set_editor_property("max", 600.0)
    params[0] = p0
    bs.set_editor_property("blend_parameters", params)
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion", only_if_is_dirty=False)
L("BS updated skel={}".format(bs.get_editor_property("skeleton").get_name()))

src = "/Game/Mannequin/Animations/ThirdPerson_AnimBP"
dst_dir = "/Game/Characters/Player/KayKit/Animations"
dst_name = "ABP_KayKitFromTP"
dst = dst_dir + "/" + dst_name

# Close editors first
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
for p in [dst, dst_dir + "/ABP_KayKitKnight", dst_dir + "/ABP_KayKitKnight_Probe"]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        try:
            a = unreal.EditorAssetLibrary.load_asset(p)
            aes.close_all_editors_for_asset(a)
        except Exception as e:
            L("close {} ERR {}".format(p, e))

# Delete broken ABP so we can recreate clean
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    ok = unreal.EditorAssetLibrary.delete_asset(dst)
    L("deleted old FromTP -> {}".format(ok))
    time.sleep(0.5)

# Duplicate ThirdPerson
dup = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
L("duplicate -> {}".format(dup))
if not dup:
    # try asset tools duplicate
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    src_obj = unreal.EditorAssetLibrary.load_asset(src)
    dup = tools.duplicate_asset(dst_name, dst_dir, src_obj)
    L("tools.duplicate -> {}".format(dup))

abp = unreal.EditorAssetLibrary.load_asset(dst)
if not abp:
    L("FAIL no abp after duplicate")
    flush()
    raise SystemExit(0)

# IMMEDIATELY set skeleton before touching graphs that would compile against mannequin
abp.set_editor_property("target_skeleton", skel)
L("set target_skeleton {}".format(skel.get_path_name()))

# Remap all nodes
mapping_by_name = {
    "ThirdPersonIdle": idle,
    "ThirdPersonWalk": walk,
    "ThirdPersonRun": run,
    "ThirdPersonJump_Start": jump_start,
    "ThirdPersonJump_Loop": jump_loop,
    "ThirdPersonJump_End": jump_land,
    "ThirdPerson_Jump": jump_full,
    # also mannequin anim names that might appear
    "ThirdPerson_Idle": idle,
    "ThirdPerson_Walk": walk,
    "ThirdPerson_Run": run,
}

EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
bsp_count = 0
sp_count = 0
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
            set_ok = False
            for n in ["blend_space", "BlendSpace", "blend_space_asset", "BlendSpaceAsset"]:
                try:
                    node.set_editor_property(n, bs)
                    set_ok = True
                except Exception:
                    pass
            bsp_count += 1
            L("BSP {} set={}".format(obj.get_name(), set_ok))
        elif cn == "AnimGraphNode_SequencePlayer":
            node = obj.get_editor_property("node")
            seq = None
            try:
                seq = node.get_editor_property("sequence")
            except Exception:
                pass
            name = seq.get_name() if seq else None
            new_seq = mapping_by_name.get(name)
            if new_seq is None:
                # fallback by substring
                if name and "Idle" in name:
                    new_seq = idle
                elif name and "Walk" in name:
                    new_seq = walk
                elif name and "Run" in name:
                    new_seq = run
                elif name and "Jump_Start" in name:
                    new_seq = jump_start
                elif name and ("Jump_Loop" in name or "Jump_Idle" in name):
                    new_seq = jump_loop
                elif name and ("Jump_End" in name or "Jump_Land" in name or "Land" in name):
                    new_seq = jump_land
                elif name and "Jump" in name:
                    new_seq = jump_full
                else:
                    new_seq = jump_loop
            node.set_editor_property("sequence", new_seq)
            sp_count += 1
            L("SP {} {} -> {}".format(obj.get_name(), name, new_seq.get_name() if new_seq else None))
    except Exception as e:
        L("node ERR {} {}".format(obj.get_name(), e))

L("remapped bsp={} sp={}".format(bsp_count, sp_count))

# Save before compile
unreal.EditorAssetLibrary.save_asset(dst, only_if_is_dirty=False)
L("saved pre-compile")

# Open editor to trigger compile - keep open briefly
opened = aes.open_editor_for_assets([abp])
L("opened editor {}".format(opened))
time.sleep(3.0)

# Try to find and invoke compile via editor - keep open longer
# Save again while open
unreal.EditorAssetLibrary.save_asset(dst, only_if_is_dirty=False)
time.sleep(1.0)
aes.close_all_editors_for_asset(abp)
L("closed editor")

# Assign to character - clear probe too
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(dst)
L("abp_cls={}".format(abp_cls))
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
if abp_cls:
    meshc.set_editor_property("anim_class", abp_cls)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("BP assigned anim_class={} mode={}".format(meshc.get_editor_property("anim_class"), meshc.get_editor_property("animation_mode")))

# Also ensure ABP_KayKitKnight is healthy fallback: set its sequence to idle and assign BS if possible
# Upgrade ABP_KayKitKnight sequence player to use Idle for safety, keep as backup
kabp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
for obj in unreal.ObjectIterator(EdGraphNode):
    if "ABP_KayKitKnight." not in obj.get_path_name() or "Probe" in obj.get_path_name():
        continue
    if obj.get_class().get_name() == "AnimGraphNode_SequencePlayer":
        try:
            node = obj.get_editor_property("node")
            node.set_editor_property("sequence", idle)
            L("KayKitKnight SP -> Idle")
        except Exception as e:
            L("KayKitKnight SP ERR {}".format(e))
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight", only_if_is_dirty=False)

# Verify refs
abp2 = unreal.EditorAssetLibrary.load_asset(dst)
L("verify target={}".format(abp2.get_editor_property("target_skeleton").get_path_name()))
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
        L("verify BSP bs={} skel={}".format(bsa.get_name() if bsa else None, bsa.get_editor_property("skeleton").get_name() if bsa else None))
    elif cn == "AnimGraphNode_SequencePlayer":
        node = obj.get_editor_property("node")
        seq = node.get_editor_property("sequence")
        sskel = seq.get_editor_property("skeleton").get_name() if seq else None
        L("verify SP {} {}".format(seq.get_name() if seq else None, sskel))

flush()
L("DONE")
