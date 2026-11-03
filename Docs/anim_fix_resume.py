# -*- coding: utf-8 -*-
import unreal
import time
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_fix_resume.txt"
lines = []
def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("[ANIMFIX] " + s)
    except Exception:
        pass
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

MESH = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
SKEL_ORIG = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
SKEL_ALIAS = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
BS = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
ABP = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
IDLE = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig"
WALK = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig"
RUN = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig"
JUMP_START = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig"
JUMP_LOOP = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig"
JUMP_LAND = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig"
JUMP_FULL = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig"

L("exists orig_skel={}".format(unreal.EditorAssetLibrary.does_asset_exist(SKEL_ORIG)))
L("exists alias_skel={}".format(unreal.EditorAssetLibrary.does_asset_exist(SKEL_ALIAS)))
L("exists mesh={}".format(unreal.EditorAssetLibrary.does_asset_exist(MESH)))
L("exists bs={}".format(unreal.EditorAssetLibrary.does_asset_exist(BS)))
L("exists abp={}".format(unreal.EditorAssetLibrary.does_asset_exist(ABP)))

mesh = unreal.EditorAssetLibrary.load_asset(MESH)
skel_orig = unreal.EditorAssetLibrary.load_asset(SKEL_ORIG)
L("loaded mesh={} skel_orig={}".format(mesh, skel_orig))
if mesh:
    try:
        cur = mesh.get_editor_property("skeleton")
        L("mesh.skeleton before={}".format(cur.get_path_name() if cur else None))
    except Exception as e:
        L("mesh.skeleton read ERR {}".format(e))

# Create / refresh alias skeleton so 146 assets that reference it resolve
if skel_orig is None:
    L("FATAL: restored skeleton failed to load")
    flush()
    raise SystemExit(1)

if unreal.EditorAssetLibrary.does_asset_exist(SKEL_ALIAS):
    # reload existing
    skel_alias = unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
    L("alias already exists -> {}".format(skel_alias))
else:
    # ensure directory
    unreal.EditorAssetLibrary.make_directory("/Game/Mannequin/Character/Mesh")
    skel_alias = unreal.EditorAssetLibrary.duplicate_asset(SKEL_ORIG, SKEL_ALIAS)
    L("duplicated alias -> {}".format(skel_alias))
    if skel_alias is None:
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        skel_alias = tools.duplicate_asset("KayKitKnightSkelXXXXXX", "/Game/Mannequin/Character/Mesh", skel_orig)
        L("tools.duplicate alias -> {}".format(skel_alias))

skel_alias = unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
L("skel_alias final={}".format(skel_alias.get_path_name() if skel_alias else None))
if skel_alias is None:
    L("FATAL: could not create alias skeleton")
    flush()
    raise SystemExit(2)

# Point mesh at alias (what all anims already use) and save
try:
    mesh.set_editor_property("skeleton", skel_alias)
    unreal.EditorAssetLibrary.save_asset(MESH, only_if_is_dirty=False)
    L("mesh.skeleton after={}".format(mesh.get_editor_property("skeleton").get_path_name()))
except Exception as e:
    L("mesh set skeleton ERR {}".format(e))

# Load loco anims
idle = unreal.EditorAssetLibrary.load_asset(IDLE)
walk = unreal.EditorAssetLibrary.load_asset(WALK)
run = unreal.EditorAssetLibrary.load_asset(RUN)
jump_start = unreal.EditorAssetLibrary.load_asset(JUMP_START)
jump_loop = unreal.EditorAssetLibrary.load_asset(JUMP_LOOP)
jump_land = unreal.EditorAssetLibrary.load_asset(JUMP_LAND)
jump_full = unreal.EditorAssetLibrary.load_asset(JUMP_FULL)
L("anims idle={} walk={} run={} js={} jl={} jland={} jf={}".format(
    bool(idle), bool(walk), bool(run), bool(jump_start), bool(jump_loop), bool(jump_land), bool(jump_full)))

# Ensure anim sequences use alias skeleton
anim_paths = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Mesh", recursive=False)
fixed_anims = 0
failed_anims = 0
for p in anim_paths:
    if "Anim_Rig" not in p:
        continue
    try:
        a = unreal.EditorAssetLibrary.load_asset(p)
        if not a or not isinstance(a, unreal.AnimSequence):
            # some may load as AnimSequence
            if a is None:
                continue
            if a.get_class().get_name() not in ("AnimSequence", "AnimSequenceBase"):
                continue
        try:
            a.set_editor_property("skeleton", skel_alias)
            fixed_anims += 1
        except Exception as e:
            failed_anims += 1
            if failed_anims < 5:
                L("anim skel set ERR {} {}".format(p, e))
    except Exception as e:
        failed_anims += 1
        if failed_anims < 5:
            L("anim load ERR {} {}".format(p, e))
L("anim skeleton assign fixed={} failed_or_skip~={}".format(fixed_anims, failed_anims))

# Fix BlendSpace samples + skeleton
bs = unreal.EditorAssetLibrary.load_asset(BS)
L("bs class={}".format(bs.get_class().get_name() if bs else None))
if bs:
    try:
        bs.set_editor_property("skeleton", skel_alias)
    except Exception as e:
        L("bs set skel ERR {}".format(e))
    # samples: idle@0, walk@200, run@500; axis max 600 to match typical MaxWalkSpeed
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
    try:
        bs.set_editor_property("sample_data", new_samples)
        L("bs sample_data set n={}".format(len(new_samples)))
    except Exception as e:
        L("bs sample_data ERR {}".format(e))
    try:
        params = list(bs.get_editor_property("blend_parameters"))
        if params:
            p0 = params[0]
            p0.set_editor_property("display_name", "Speed")
            p0.set_editor_property("min", 0.0)
            p0.set_editor_property("max", 600.0)
            try:
                p0.set_editor_property("grid_num", 4)
            except Exception:
                pass
            params[0] = p0
            # If 2D blend space, keep Direction axis as-is
            bs.set_editor_property("blend_parameters", params)
            L("bs params0 Speed 0..600; nparams={}".format(len(params)))
    except Exception as e:
        L("bs params ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(BS, only_if_is_dirty=False)
    # verify
    try:
        sd = bs.get_editor_property("sample_data")
        for i, s in enumerate(sd):
            a = s.get_editor_property("animation")
            v = s.get_editor_property("sample_value")
            L("bs sample[{}] {} @ {}".format(i, a.get_name() if a else None, v))
        L("bs.skeleton={}".format(bs.get_editor_property("skeleton").get_path_name()))
    except Exception as e:
        L("bs verify ERR {}".format(e))

# Fix ABP
abp = unreal.EditorAssetLibrary.load_asset(ABP)
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
if abp:
    try:
        abp.set_editor_property("target_skeleton", skel_alias)
        L("abp target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))
    except Exception as e:
        L("abp target ERR {}".format(e))
    try:
        abp.set_editor_property("preview_skeletal_mesh", mesh)
    except Exception as e:
        L("abp preview ERR {}".format(e))

    # Ensure BlendSpacePlayer uses our BS; SequencePlayers use KayKit jumps
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    bsp_n = 0
    sp_n = 0
    for obj in unreal.ObjectIterator(EdGraphNode):
        pn = obj.get_path_name()
        if "ABP_KayKitLocomotion" not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn:
            continue
        cn = obj.get_class().get_name()
        try:
            if cn == "AnimGraphNode_BlendSpacePlayer":
                node = obj.get_editor_property("node")
                ok = False
                for n in ["blend_space", "BlendSpace"]:
                    try:
                        node.set_editor_property(n, bs)
                        ok = True
                    except Exception:
                        pass
                bsp_n += 1
                L("BSP {} set={}".format(obj.get_name(), ok))
            elif cn == "AnimGraphNode_SequencePlayer":
                node = obj.get_editor_property("node")
                seq = node.get_editor_property("sequence")
                name = (seq.get_name() if seq else "") or ""
                nl = name.lower()
                new_seq = None
                if "jump_start" in nl or ("jump" in nl and "start" in nl):
                    new_seq = jump_start
                elif "jump_land" in nl or "jump_end" in nl or "land" in nl:
                    new_seq = jump_land
                elif "jump_loop" in nl or ("jump" in nl and "idle" in nl):
                    new_seq = jump_loop
                elif "jump" in nl:
                    new_seq = jump_full
                elif "idle" in nl:
                    new_seq = idle
                elif "walk" in nl:
                    new_seq = walk
                elif "run" in nl:
                    new_seq = run
                if new_seq:
                    node.set_editor_property("sequence", new_seq)
                    sp_n += 1
                    L("SP {} {} -> {}".format(obj.get_name(), name, new_seq.get_name()))
        except Exception as e:
            L("node ERR {} {}".format(obj.get_name(), e))
    L("remapped bsp={} sp={}".format(bsp_n, sp_n))
    unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False)

    # Open to compile
    try:
        aes.open_editor_for_assets([abp])
        time.sleep(3.0)
        unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False)
        aes.close_all_editors_for_asset(abp)
        L("abp open/save/close compile pass")
    except Exception as e:
        L("abp compile-open ERR {}".format(e))

abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(ABP)
L("abp_cls={}".format(abp_cls))

# Assign to BP mesh CDO + any SMC templates
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
meshc.set_editor_property("skeletal_mesh", mesh)
meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
if abp_cls:
    meshc.set_editor_property("anim_class", abp_cls)
L("BP CDO mode={} anim_class={}".format(
    meshc.get_editor_property("animation_mode"),
    meshc.get_editor_property("anim_class")))

# Max walk speed align with BS
try:
    move = cdo.get_editor_property("character_movement")
    if move:
        mws = move.get_editor_property("max_walk_speed")
        L("MaxWalkSpeed before={}".format(mws))
        # keep around 600; BS max 600
        if mws is None or float(mws) < 100:
            move.set_editor_property("max_walk_speed", 600.0)
            L("MaxWalkSpeed set 600")
except Exception as e:
    L("move ERR {}".format(e))

updated_smc = 0
for obj in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    p = obj.get_path_name()
    if "BP_KayKitKnight" not in p:
        continue
    if "/Engine/Transient" in p or "PersistentLevel" in p:
        continue
    try:
        obj.set_editor_property("skeletal_mesh", mesh)
        obj.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        if abp_cls:
            obj.set_editor_property("anim_class", abp_cls)
        updated_smc += 1
    except Exception as e:
        L("SMC update ERR {} {}".format(p, e))
L("updated_smc_templates={}".format(updated_smc))
unreal.EditorAssetLibrary.save_asset(BP, only_if_is_dirty=False)

# GM_Hub pawn
gm_path = "/Game/Core/GameFlow/GM_Hub"
if unreal.EditorAssetLibrary.does_asset_exist(gm_path):
    gm_cls = unreal.EditorAssetLibrary.load_blueprint_class(gm_path)
    gm_cdo = unreal.get_default_object(gm_cls)
    pawn = gm_cdo.get_editor_property("default_pawn_class")
    L("GM_Hub pawn={}".format(pawn))
    if pawn is None or "KayKit" not in str(pawn):
        gm_cdo.set_editor_property("default_pawn_class", bp_cls)
        unreal.EditorAssetLibrary.save_asset(gm_path, only_if_is_dirty=False)
        L("GM_Hub pawn set to BP_KayKitKnight")

# Final consistency
L("FINAL mesh.skel={}".format(mesh.get_editor_property("skeleton").get_path_name() if mesh.get_editor_property("skeleton") else None))
L("FINAL abp.target={}".format(abp.get_editor_property("target_skeleton").get_path_name() if abp else None))
L("FINAL bs.skel={}".format(bs.get_editor_property("skeleton").get_path_name() if bs else None))
L("FINAL alias_exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(SKEL_ALIAS)))
L("FINAL orig_exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(SKEL_ORIG)))
L("SUCCESS_SKELETON_RESTORED=1")
flush()
