# -*- coding: utf-8 -*-
import unreal

OUT = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\abp_fix_result.txt"
lines = []

def L(m):
    s = str(m)
    lines.append(s)
    unreal.log(s)

def flush():
    open(OUT, "w", encoding="utf-8").write("\\n".join(lines) + "\\n")

mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = mesh.get_editor_property("skeleton")
abp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
jump_loop = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_land = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
jump_full = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig")

L("skel={} abp_target={}".format(skel.get_path_name(), abp.get_editor_property("target_skeleton").get_path_name()))
L("bs_skel={} samples={}".format(
    bs.get_editor_property("skeleton").get_path_name(),
    [(s.get_editor_property("animation").get_name(), round(s.get_editor_property("sample_value").x,2)) for s in bs.get_editor_property("sample_data")]
))

# Update BS samples without touching read-only skeleton (already correct)
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
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion", only_if_is_dirty=False)
L("BS samples updated")

# Ensure ABP target skeleton
abp.set_editor_property("target_skeleton", skel)
L("set target_skeleton OK")

# Inspect / fix graph nodes
BSPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer")
SPCls = unreal.load_class(None, "/Script/AnimGraph.AnimGraphNode_SequencePlayer")
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")

mapping = {
    "ThirdPersonIdle": idle,
    "ThirdPersonWalk": walk,
    "ThirdPersonRun": run,
    "ThirdPersonJump_Start": jump_start,
    "ThirdPersonJump_Loop": jump_loop,
    "ThirdPersonJump_End": jump_land,
    "ThirdPerson_Jump": jump_full,
}

# List all edgraph nodes under this ABP
for obj in unreal.ObjectIterator(EdGraphNode):
    pn = obj.get_path_name()
    if "ABP_KayKitFromTP" not in pn:
        continue
    if "Default__" in pn or "ANIM_PREVIEW" in pn.upper() or "AnimPreview" in pn:
        continue
    cn = obj.get_class().get_name()
    extra = ""
    try:
        if cn == "AnimGraphNode_BlendSpacePlayer":
            node = obj.get_editor_property("node")
            bsa = None
            for n in ["blend_space_asset", "BlendSpaceAsset", "blend_space", "BlendSpace"]:
                try:
                    bsa = node.get_editor_property(n)
                    if bsa:
                        break
                except Exception:
                    pass
            extra = " bs={}".format(bsa.get_path_name() if bsa else None)
            # force set
            for n in ["blend_space_asset", "BlendSpaceAsset", "blend_space", "BlendSpace"]:
                try:
                    node.set_editor_property(n, bs)
                    extra += " SET:" + n
                except Exception:
                    pass
        elif cn == "AnimGraphNode_SequencePlayer":
            node = obj.get_editor_property("node")
            seq = node.get_editor_property("sequence")
            name = seq.get_name() if seq else None
            extra = " seq={}".format(name)
            if name in mapping and mapping[name]:
                node.set_editor_property("sequence", mapping[name])
                extra += " -> {}".format(mapping[name].get_name())
            elif seq:
                try:
                    sskel = seq.get_editor_property("skeleton")
                    if (not sskel) or (sskel.get_path_name() != skel.get_path_name()):
                        node.set_editor_property("sequence", jump_loop)
                        extra += " mismatch->Jump_Idle_Rig"
                except Exception as e:
                    extra += " skelERR:{}".format(e)
        elif cn == "AnimGraphNode_StateMachine":
            extra = " SM"
        elif cn == "AnimGraphNode_TransitionResult":
            extra = " TR"
    except Exception as e:
        extra = " ERR:{}".format(e)
    L("NODE {} {}{}".format(cn, obj.get_name(), extra))

# Try compile via several APIs
compile_ok = False
# 1) load C++ KismetEditorUtilities default object
for path in [
    "/Script/UnrealEd.Default__KismetEditorUtilities",
    "/Script/UnrealEd.KismetEditorUtilities",
]:
    try:
        obj = unreal.load_object(None, path)
        L("load {} -> {}".format(path, obj))
    except Exception as e:
        L("load {} ERR {}".format(path, e))

# 2) find compile methods on unreal module
compile_names = [n for n in dir(unreal) if "ompil" in n.lower() or "KismetEditor" in n or "BlueprintEditor" in n]
L("compile-ish names: {}".format(compile_names))

# 3) try EditorAssetLibrary methods
eal = [n for n in dir(unreal.EditorAssetLibrary) if "ompil" in n.lower() or "save" in n.lower()]
L("EAL: {}".format(eal))

# 4) call_method on AnimBlueprint
for meth in ["CompileBlueprint", "compile_blueprint", "Recompile", "OnCompiled", "Status", "GetBlueprintStatus", "GeneratedClass"]:
    try:
        r = abp.call_method(meth)
        L("abp.call_method({})={}".format(meth, r))
    except Exception as e:
        L("abp.call_method({}) ERR {}".format(meth, e))

# 5) try unreal.find_object / importlib style via Blueprint
try:
    # UE4.27 sometimes exposes through EditorPythonExecuter only
    ue = unreal
    if hasattr(ue, "EditorLoadingAndSavingUtils"):
        L("has EditorLoadingAndSavingUtils")
except Exception as e:
    L("ELSU ERR {}".format(e))

# 6) Console command compile
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, "KE * CompileBlueprint")
    L("console KE tried")
except Exception as e:
    L("console ERR {}".format(e))

# Mark dirty and save - editor often recompiles on open/save
try:
    abp.modify()
except Exception as e:
    L("modify ERR {}".format(e))

# Use AssetRegistry / PackageTools?
for name in ["PackageTools", "BlueprintEditorUtils", "FKismetEditorUtilities", "AnimBlueprintExtension"]:
    L("hasattr {} {}".format(name, hasattr(unreal, name)))

# Try loading BlueprintEditorUtils via load_class and static call - unlikely from Python

# Force regenerate by setting target skeleton again and saving
abp.set_editor_property("target_skeleton", skel)
saved = unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP", only_if_is_dirty=False)
L("save abp -> {}".format(saved))

# Assign anim class on pawn again
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
meshc = cdo.get_editor_property("mesh")
abp_cls = None
# generated class path
gen_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP.ABP_KayKitFromTP_C"
abp_cls = unreal.load_object(None, gen_path)
L("loaded gen class {}".format(abp_cls))
if abp_cls is None:
    abp_cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
    L("load_blueprint_class {}".format(abp_cls))

meshc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
if abp_cls:
    meshc.set_editor_property("anim_class", abp_cls)
meshc.set_editor_property("skeletal_mesh", mesh)
unreal.EditorAssetLibrary.save_asset(bp_path, only_if_is_dirty=False)
L("BP mesh anim_class={} mode={}".format(meshc.get_editor_property("anim_class"), meshc.get_editor_property("animation_mode")))

# Capture recent compile errors from log? Write our own validation by checking node skeletons
bad = []
for obj in unreal.ObjectIterator(BSPCls):
    if "ABP_KayKitFromTP" not in obj.get_path_name():
        continue
    try:
        node = obj.get_editor_property("node")
        bsa = None
        for n in ["blend_space_asset", "BlendSpaceAsset", "blend_space", "BlendSpace"]:
            try:
                bsa = node.get_editor_property(n)
                if bsa:
                    break
            except Exception:
                pass
        if not bsa:
            bad.append("BSP missing blendspace")
        else:
            bskel = bsa.get_editor_property("skeleton")
            if bskel.get_path_name() != skel.get_path_name():
                bad.append("BSP skel mismatch {} vs {}".format(bskel.get_path_name(), skel.get_path_name()))
            else:
                L("BSP OK {}".format(bsa.get_name()))
    except Exception as e:
        bad.append("BSP check ERR {}".format(e))

for obj in unreal.ObjectIterator(SPCls):
    if "ABP_KayKitFromTP" not in obj.get_path_name():
        continue
    if "AnimPreview" in obj.get_path_name() or "Default__" in obj.get_path_name():
        continue
    try:
        node = obj.get_editor_property("node")
        seq = node.get_editor_property("sequence")
        if not seq:
            bad.append("SP {} null sequence".format(obj.get_name()))
            continue
        sskel = seq.get_editor_property("skeleton")
        if (not sskel) or sskel.get_path_name() != skel.get_path_name():
            bad.append("SP {} skel {}".format(obj.get_name(), sskel.get_path_name() if sskel else None))
        else:
            L("SP OK {} -> {}".format(obj.get_name(), seq.get_name()))
    except Exception as e:
        bad.append("SP check ERR {}".format(e))

L("BAD={}".format(bad))

# Try open then close asset editor which triggers compile in many UE versions
try:
    subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    L("AssetEditorSubsystem={}".format(subsystem))
except Exception as e:
    L("get_editor_subsystem ERR {}".format(e))
    subsystem = None

if subsystem is None:
    try:
        # UE4.27
        aes = unreal.AssetToolsHelpers.get_asset_tools()
        L("asset_tools={}".format(aes))
    except Exception as e:
        L("asset_tools ERR {}".format(e))

# Open asset via EditorAssetLibrary - no open method. Use AssetEditorSubsystem in UE5 only.
# Try:
try:
    unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
    # AssetRegistry
except Exception:
    pass

# Use Python Editor Scripting open_editor_for_assets if present
for n in dir(unreal):
    if "AssetEditor" in n or "open_editor" in n.lower():
        L("found {}".format(n))

try:
    # In 4.27 Python plugin:
    unreal.AssetEditorSubsystem
except Exception as e:
    L("AssetEditorSubsystem class ERR {}".format(e))

# Last resort: duplicate a clean ABP from ThirdPerson with correct skeleton via factory
# Only if current remains broken - probe compile messages by re-setting and saving BS into player nodes again

flush()
L("COMPILE_PASS_DONE")
