# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_fix_bs.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

BS="/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
ABP="/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
BP="/Game/Characters/Player/KayKit/Blueprints/BP_KayKitKnight"
IDLE="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle"
WALK="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A"
RUN="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A"
SKEL_ALIAS="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"

idle=unreal.EditorAssetLibrary.load_asset(IDLE)
walk=unreal.EditorAssetLibrary.load_asset(WALK)
run=unreal.EditorAssetLibrary.load_asset(RUN)
bs=unreal.EditorAssetLibrary.load_asset(BS)
abp=unreal.EditorAssetLibrary.load_asset(ABP)
bp=unreal.EditorAssetLibrary.load_asset(BP)
sa=unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)

L("idle.skel={}".format(idle.get_editor_property("skeleton")))
L("walk.skel={}".format(walk.get_editor_property("skeleton")))
L("run.skel={}".format(run.get_editor_property("skeleton")))
L("bs.class={} bs.skel={}".format(bs.get_class().get_name(), bs.get_editor_property("skeleton")))

# Read current sample data
try:
    sd=bs.get_editor_property("sample_data")
    L("sample_data type={} len={}".format(type(sd).__name__, len(sd) if sd is not None else None))
    for i,s in enumerate(list(sd) if sd else []):
        try:
            anim=s.get_editor_property("animation")
        except Exception:
            anim=getattr(s,"animation",None)
        try:
            params=s.get_editor_property("sample_value") if hasattr(s,"get_editor_property") else None
        except Exception:
            params=None
        try:
            params2=s.get_editor_property("data") 
        except Exception:
            params2=None
        L(" sample[{}] anim={} sample_value={} data={} raw={}".format(i,anim,params,params2,s))
except Exception as e:
    L("sample_data ERR {}".format(e))

# BlendSpace sample API via EditorAssetLibrary / BlendSpace
# In UE4.27 BlendSpaceBase has sample_data as array of BlendSample
# BlendSample: animation, sample_value (Vector), rate_scale
# Clear and re-add samples

def clear_and_add_1d(bs_asset, samples):
    # samples: list of (anim_asset, speed_float)
    # Try remove existing
    try:
        sd=list(bs_asset.get_editor_property("sample_data") or [])
        L("before clear n={}".format(len(sd)))
    except Exception as e:
        L("read sd ERR {}".format(e)); sd=[]
    # Prefer add_sample / delete via methods
    methods=[n for n in dir(bs_asset) if "sample" in n.lower() or "Sample" in n]
    L("bs sample methods={}".format(methods))
    # Try unreal.BlendSpace methods - often not exposed
    # Direct set sample_data
    new_samples=[]
    for anim_asset, speed in samples:
        try:
            bsamp=unreal.BlendSample()
            bsamp.set_editor_property("animation", anim_asset)
            # sample_value is Vector (X=speed for 1D)
            bsamp.set_editor_property("sample_value", unreal.Vector(speed, 0.0, 0.0))
            bsamp.set_editor_property("rate_scale", 1.0)
            new_samples.append(bsamp)
            L("built sample anim={} speed={}".format(anim_asset.get_name(), speed))
        except Exception as e:
            L("BlendSample build ERR {}".format(e))
            # try struct differently
            try:
                bsamp=unreal.BlendSample(animation=anim_asset, sample_value=unreal.Vector(speed,0,0), rate_scale=1.0)
                new_samples.append(bsamp)
                L("built via ctor")
            except Exception as e2:
                L("ctor ERR {}".format(e2))
    try:
        bs_asset.set_editor_property("sample_data", new_samples)
        L("set sample_data OK n={}".format(len(new_samples)))
    except Exception as e:
        L("set sample_data ERR {}".format(e))
    # Verify
    sd2=bs_asset.get_editor_property("sample_data")
    L("after set n={}".format(len(sd2) if sd2 else None))
    for i,s in enumerate(list(sd2) if sd2 else []):
        L("  [{}] anim={} val={}".format(i, s.get_editor_property("animation"), s.get_editor_property("sample_value")))

clear_and_add_1d(bs, [(idle,0.0),(walk,200.0),(run,500.0)])

# Check blend parameters - should be 1 axis for BlendSpace1D
try:
    params=bs.get_editor_property("blend_parameters")
    L("blend_parameters n={} -> {}".format(len(params) if params else None, params))
    for i,p in enumerate(list(params) if params else []):
        try:
            L("  param[{}] name={} min={} max={} grid={}".format(
                i, p.get_editor_property("display_name"), p.get_editor_property("min"),
                p.get_editor_property("max"), p.get_editor_property("grid_num")))
        except Exception as e:
            L("  param[{}] ERR {} raw={}".format(i,e,p))
except Exception as e:
    L("blend_parameters ERR {}".format(e))

# If 3 params, try to fix to 1D Speed only
try:
    # BlendParameter struct
    bp0=unreal.BlendParameter()
    bp0.set_editor_property("display_name", "Speed")
    bp0.set_editor_property("min", 0.0)
    bp0.set_editor_property("max", 600.0)
    bp0.set_editor_property("grid_num", 4)
    # For BlendSpace1D only one parameter matters; property may still be size 3 in base
    cur=list(bs.get_editor_property("blend_parameters") or [])
    if len(cur)>=1:
        cur[0]=bp0
        try:
            bs.set_editor_property("blend_parameters", cur)
            L("updated blend_parameters[0]=Speed 0..600")
        except Exception as e:
            L("set blend_parameters ERR {}".format(e))
except Exception as e:
    L("fix params ERR {}".format(e))

# ABP: ensure target skeleton and preview
L("abp target_skeleton={}".format(abp.get_editor_property("target_skeleton")))
try:
    abp.set_editor_property("target_skeleton", sa)
    L("set abp target_skeleton OK")
except Exception as e:
    L("set abp skel ERR {}".format(e))

# BP mesh anim class
try:
    # Compiled BP CDO
    gen=abp.generated_class if hasattr(abp,"generated_class") else abp.get_editor_property("generated_class")
    L("abp generated_class={}".format(gen))
except Exception as e:
    L("gen class ERR {}".format(e))

cdo=unreal.get_default_object(bp.generated_class()) if hasattr(bp,"generated_class") else None
try:
    cdo=bp.generated_class().get_default_object()
except Exception:
    try:
        cdo=unreal.get_default_object(bp.get_editor_property("generated_class"))
    except Exception as e:
        L("cdo ERR {}".format(e)); cdo=None

# Find mesh component and check animation mode
if cdo:
    L("cdo={}".format(cdo))
    # SCS components hard; try get_components / simple property
    for prop in ["mesh","Mesh","character_mesh","CharacterMesh0"]:
        try:
            m=cdo.get_editor_property(prop)
            L("cdo.{}={}".format(prop,m))
        except Exception:
            pass

# Save assets
for a,n in [(bs,"BS"),(abp,"ABP"),(idle,"idle"),(walk,"walk"),(run,"run")]:
    try:
        r=unreal.EditorAssetLibrary.save_loaded_asset(a)
        L("save {} -> {}".format(n,r))
    except Exception as e:
        L("save {} ERR {}".format(n,e))

# Final verify samples skels
bs2=unreal.EditorAssetLibrary.load_asset(BS)
sd=bs2.get_editor_property("sample_data")
L("FINAL samples:")
for i,s in enumerate(list(sd) if sd else []):
    anim=s.get_editor_property("animation")
    sk=anim.get_editor_property("skeleton") if anim else None
    L("  [{}] {} skel={} val={}".format(i, anim.get_path_name() if anim else None, sk, s.get_editor_property("sample_value")))

flush()
print("FIXBS_DONE")