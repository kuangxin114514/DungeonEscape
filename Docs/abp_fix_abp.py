# -*- coding: utf-8 -*-
import unreal

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_fix_result.txt"
lines = []

def L(msg):
    s = str(msg)
    lines.append(s)
    try:
        unreal.log(s)
    except Exception:
        pass

def flush():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\\n".join(lines) + "\\n")

# Resolve the real KayKit skeleton used by the mesh
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = mesh.get_editor_property("skeleton") if mesh else None
L("skel={}".format(skel.get_path_name() if skel else None))
if not skel:
    L("NO_SKEL"); flush(); raise SystemExit(1)

# Ensure skeleton package is saved on disk if missing
skel_path = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
if not unreal.EditorAssetLibrary.does_asset_exist(skel_path):
    L("skel asset missing on disk; attempting save_loaded_asset")
    try:
        ok = unreal.EditorAssetLibrary.save_loaded_asset(skel)
        L("save_loaded_asset skel -> {}".format(ok))
    except Exception as e:
        L("save_loaded_asset ERR {}".format(e))
else:
    L("skel asset exists on disk")

idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
jump_loop = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_land = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
jump_full = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig")
L("anims idle={} walk={} run={} js={} jl={} jland={} jf={}".format(bool(idle), bool(walk), bool(run), bool(jump_start), bool(jump_loop), bool(jump_land), bool(jump_full)))

# Fix BlendSpace1D
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
if not bs:
    # duplicate from mannequin idle/run 1D or 2D if needed
    src = "/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D"
    if unreal.EditorAssetLibrary.does_asset_exist(src):
        unreal.EditorAssetLibrary.duplicate_asset(src, bs_path)
        bs = unreal.EditorAssetLibrary.load_asset(bs_path)
        L("duplicated BS from {}".format(src))
    else:
        L("NO_BS_SOURCE"); flush(); raise SystemExit(2)

# Force skeleton + samples
bs.set_editor_property("skeleton", skel)
new_samples = []
for anim, x in [(idle, 0.0), (walk, 150.0), (run, 375.0)]:
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
    p0.set_editor_property("max", 375.0)
    try:
        p0.set_editor_property("grid_num", 4)
    except Exception:
        pass
    params[0] = p0
    bs.set_editor_property("blend_parameters", params)
unreal.EditorAssetLibrary.save_asset(bs_path, only_if_is_dirty=False)
L("BS fixed skel={} samples={}".format(
    bs.get_editor_property("skeleton").get_path_name(),
    [(s.get_editor_property("animation").get_name(), s.get_editor_property("sample_value").x) for s in bs.get_editor_property("sample_data")]
))

# Fix ABP_KayKitFromTP
abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
L("abp before target_skeleton try")
for prop in ["target_skeleton", "TargetSkeleton"]:
    try:
        old = abp.get_editor_property(prop)
        L("  get {} -> {}".format(prop, old.get_path_name() if old else None))
        abp.set_editor_property(prop, skel)
        new = abp.get_editor_property(prop)
        L("  set {} -> {}".format(prop, new.get_path_name() if new else None))
    except Exception as e:
        L("  {} ERR {}".format(prop, e))

# Preview mesh
try:
    abp.set_editor_property("preview_skeletal_mesh", mesh)
    L("preview mesh set")
except Exception as e:
    L("preview mesh ERR {}".format(e))

# Replace BlendSpacePlayer refs inside this ABP
BSPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")
replaced_bs = 0
for obj in unreal.ObjectIterator(BSPCls):
    pn = obj.get_path_name()
    if "ABP_KayKitFromTP" not in pn:
        continue
    L("BSP {}".format(pn))
    try:
        node = obj.get_editor_property("node")
        for pn_name in ["blend_space_asset", "BlendSpaceAsset", "blend_space", "BlendSpace"]:
            try:
                old = node.get_editor_property(pn_name)
                L("  node.{} old={}".format(pn_name, old))
                node.set_editor_property(pn_name, bs)
                replaced_bs += 1
                L("  node.{} SET".format(pn_name))
            except Exception as e:
                pass
        for pn_name in ["blend_space_asset", "BlendSpaceAsset"]:
            try:
                obj.set_editor_property(pn_name, bs)
                replaced_bs += 1
            except Exception:
                pass
    except Exception as e:
        L("BSP ERR {}".format(e))
L("replaced_bs={}".format(replaced_bs))

# Remap SequencePlayers that still point at mannequin anims
SPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
mapping = {
    "ThirdPersonIdle": idle,
    "ThirdPersonWalk": walk,
    "ThirdPersonRun": run,
    "ThirdPersonJump_Start": jump_start or jump_loop,
    "ThirdPersonJump_Loop": jump_loop or idle,
    "ThirdPersonJump_End": jump_land or idle,
    "ThirdPerson_Jump": jump_full or jump_loop or idle,
}
remapped = 0
for obj in unreal.ObjectIterator(SPCls):
    pn = obj.get_path_name()
    if "ABP_KayKitFromTP" not in pn:
        continue
    try:
        node = obj.get_editor_property("node")
        seq = node.get_editor_property("sequence")
        name = seq.get_name() if seq else None
        L("SP {} seq={}".format(obj.get_name(), name))
        if name in mapping and mapping[name]:
            node.set_editor_property("sequence", mapping[name])
            remapped += 1
            L("  remapped -> {}".format(mapping[name].get_name()))
        elif seq:
            # if sequence skeleton mismatches, force to jump_loop/idle
            try:
                sskel = seq.get_editor_property("skeleton")
                if sskel and sskel.get_path_name() != skel.get_path_name():
                    node.set_editor_property("sequence", jump_loop or idle)
                    remapped += 1
                    L("  skeleton mismatch remapped {}".format(name))
            except Exception:
                pass
    except Exception as e:
        L("SP ERR {}".format(e))
L("remapped={}".format(remapped))

# Compile ABP
compiled = False
try:
    unreal.KismetEditorUtilities.compile_blueprint(abp)
    compiled = True
    L("compile_blueprint called")
except Exception as e:
    L("compile_blueprint ERR {}".format(e))
try:
    status = abp.status
    L("abp.status={}".format(status))
except Exception as e:
    L("abp.status ERR {}".format(e))
try:
    gen = abp.generated_class()
    L("abp.generated_class={}".format(gen))
except Exception as e:
    L("abp.generated_class ERR {}".format(e))

unreal.EditorAssetLibrary.save_asset(abp_path, only_if_is_dirty=False)
L("abp saved")

# Assign to BP_KayKitKnight mesh
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
L("abp_cls={}".format(abp_cls))
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
meshc.set_editor_property("anim_class", abp_cls)
# also set skeletal mesh just in case
meshc.set_editor_property("skeletal_mesh", mesh)
L("mesh mode={} anim={} sk={}".format(
    meshc.get_editor_property("animation_mode"),
    meshc.get_editor_property("anim_class"),
    meshc.get_editor_property("skeletal_mesh").get_name() if meshc.get_editor_property("skeletal_mesh") else None
))

# Compile character BP (no SCS ctypes changes)
bp_asset = unreal.EditorAssetLibrary.load_asset(bp_path)
try:
    unreal.KismetEditorUtilities.compile_blueprint(bp_asset)
    L("BP compile called")
except Exception as e:
    L("BP compile ERR {}".format(e))
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)

# Re-check compatibility warning by reading target skeleton again
try:
    ts = abp.get_editor_property("target_skeleton")
    L("FINAL target_skeleton={}".format(ts.get_path_name() if ts else None))
except Exception as e:
    L("FINAL target ERR {}".format(e))
try:
    L("FINAL BS skel={}".format(bs.get_editor_property("skeleton").get_path_name()))
except Exception as e:
    L("FINAL BS ERR {}".format(e))

# Also sync ABP_KayKitKnight target skeleton so it doesn't confuse later
abp2 = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight")
if abp2:
    try:
        abp2.set_editor_property("target_skeleton", skel)
        unreal.KismetEditorUtilities.compile_blueprint(abp2)
        unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight", only_if_is_dirty=False)
        L("ABP_KayKitKnight synced status={}".format(getattr(abp2, "status", "?")))
    except Exception as e:
        L("ABP_KayKitKnight sync ERR {}".format(e))

flush()
L("FIX_DONE")
