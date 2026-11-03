# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_verify_final.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

ABP="/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
BP="/Game/Characters/Player/KayKit/Blueprints/BP_KayKitKnight"
BS="/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
MESH="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
GM="/Game/Core/GM_Hub"

abp=unreal.EditorAssetLibrary.load_asset(ABP)
bp=unreal.EditorAssetLibrary.load_asset(BP)
bs=unreal.EditorAssetLibrary.load_asset(BS)
mesh=unreal.EditorAssetLibrary.load_asset(MESH)

L("mesh.skel={}".format(mesh.get_editor_property("skeleton")))
L("bs.skel={}".format(bs.get_editor_property("skeleton")))
L("abp.target_skeleton={}".format(abp.get_editor_property("target_skeleton")))

# ABP skeleton match mesh?
L("skel match mesh/abp={}".format(mesh.get_editor_property("skeleton")==abp.get_editor_property("target_skeleton")))
L("skel match mesh/bs={}".format(mesh.get_editor_property("skeleton")==bs.get_editor_property("skeleton")))

# Find generated class for ABP - property might be Skeleton or TargetSkeleton; GeneratedClass on UBlueprint
for prop in ["generated_class","GeneratedClass","skeleton_generated_class","SkeletonGeneratedClass"]:
    try:
        L("abp.{}={}".format(prop, abp.get_editor_property(prop)))
    except Exception as e:
        L("abp.{} ERR {}".format(prop,e))

# Blueprint get_editor_property GeneratedClass is often protected - try:
try:
    gc=abp.get_editor_property("generated_class")
except Exception:
    gc=None
# Use unreal.SystemLibrary or load _C
abp_c=unreal.EditorAssetLibrary.load_blueprint_class(ABP)
L("load_blueprint_class ABP={}".format(abp_c))
bp_c=unreal.EditorAssetLibrary.load_blueprint_class(BP)
L("load_blueprint_class BP={}".format(bp_c))

if abp_c:
    cdo=unreal.get_default_object(abp_c)
    L("abp cdo={}".format(cdo))
    # List variables of interest
    for v in ["Speed","Direction","IsInAir","Velocity","GroundSpeed","should_move","ShouldMove"]:
        try:
            L("  abp.{}={}".format(v, cdo.get_editor_property(v)))
        except Exception as e:
            # try camel
            try:
                L("  abp.{} missing ({})".format(v,e))
            except Exception:
                pass

# BP character: mesh anim class
if bp_c:
    pcdo=unreal.get_default_object(bp_c)
    L("bp cdo={}".format(pcdo))
    # Character has Mesh component as property "mesh"
    try:
        mcomp=pcdo.get_editor_property("mesh")
        L("bp.mesh={}".format(mcomp))
        if mcomp:
            for p in ["animation_mode","anim_class","skeletal_mesh","animation_data","override_materials","visibility_based_anim_tick_option"]:
                try:
                    L("  mesh.{}={}".format(p, mcomp.get_editor_property(p)))
                except Exception as e:
                    L("  mesh.{} ERR {}".format(p,e))
            # Force AnimClass if wrong
            try:
                cur=mcomp.get_editor_property("anim_class")
                L("  current anim_class={}".format(cur))
                if abp_c and cur != abp_c:
                    mcomp.set_editor_property("anim_class", abp_c)
                    L("  SET anim_class to ABP")
                # animation mode Blueprint
                mcomp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
                L("  SET animation_mode BLUEPRINT")
            except Exception as e:
                L("  set anim ERR {}".format(e))
    except Exception as e:
        L("bp.mesh ERR {}".format(e))
    try:
        L("bp.MaxWalkSpeed via cmc:")
        cmc=pcdo.get_editor_property("character_movement")
        if cmc:
            L("  MaxWalkSpeed={}".format(cmc.get_editor_property("max_walk_speed")))
    except Exception as e:
        L("cmc ERR {}".format(e))

# Compile ABP
try:
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    L("saved bp")
except Exception as e:
    L("save bp ERR {}".format(e))

# Try KismetEditorUtilities compile
try:
    if hasattr(unreal,"KismetEditorUtilities"):
        unreal.KismetEditorUtilities.compile_blueprint(abp)
        L("compile abp OK")
        unreal.KismetEditorUtilities.compile_blueprint(bp)
        L("compile bp OK")
    else:
        L("no KismetEditorUtilities")
except Exception as e:
    L("compile ERR {}".format(e))

# Inspect ABP ubergraph for Speed VariableSet via find nodes - limited in UE4 python
# Check BS samples one more time
sd=bs.get_editor_property("sample_data")
for i,s in enumerate(list(sd)):
    anim=s.get_editor_property("animation")
    L("BS[{}] {} skelOK={} val={}".format(i, anim.get_name() if anim else None,
        anim.get_editor_property("skeleton") is not None if anim else False,
        s.get_editor_property("sample_value")))

# GM default pawn
try:
    gm=unreal.EditorAssetLibrary.load_asset(GM)
    if gm:
        L("GM={}".format(gm))
        for p in ["default_pawn_class","DefaultPawnClass"]:
            try:
                L("  GM.{}={}".format(p, gm.get_editor_property(p)))
            except Exception as e:
                L("  GM.{} ERR {}".format(p,e))
except Exception as e:
    L("GM ERR {}".format(e))

# Search GM path
for folder in ["/Game/Core","/Game/Maps","/Game/GameModes","/Game"]:
    try:
        assets=unreal.EditorAssetLibrary.list_assets(folder, recursive=False, include_folder=False)
        gms=[a for a in assets if "GM_" in a or "GameMode" in a]
        if gms:
            L("gms in {} = {}".format(folder, gms[:20]))
    except Exception:
        pass

flush()
print("VERIFY_DONE")