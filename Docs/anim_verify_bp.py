# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_verify_bp.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

# Find BP_KayKitKnight
found=[]
for folder in ["/Game/Characters/Player/KayKit","/Game/Characters","/Game"]:
    try:
        assets=unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
        for a in assets:
            if "BP_KayKit" in a or "KayKitKnight" in a and "BP_" in a:
                found.append(a)
    except Exception as e:
        L("list {} ERR {}".format(folder,e))
L("found BP-like={}".format(found[:50]))

# Also filter unique BP
bps=[a for a in found if a.split(".")[-1].startswith("BP_") or "/BP_" in a]
L("bps={}".format(bps))

for path in bps:
    # strip .ObjectName
    soft=path.split(".")[0]
    bp=unreal.EditorAssetLibrary.load_asset(soft)
    L("load {} -> {} class={}".format(soft, bp, bp.get_class().get_name() if bp else None))
    bc=unreal.EditorAssetLibrary.load_blueprint_class(soft)
    L("  blueprint_class={}".format(bc))
    if not bc:
        continue
    cdo=unreal.get_default_object(bc)
    try:
        m=cdo.get_editor_property("mesh")
        L("  mesh={}".format(m))
        if m:
            L("  anim_mode={}".format(m.get_editor_property("animation_mode")))
            L("  anim_class={}".format(m.get_editor_property("anim_class")))
            L("  skel_mesh={}".format(m.get_editor_property("skeletal_mesh")))
    except Exception as e:
        L("  mesh ERR {}".format(e))

# Inspect ABP for node graph - use AnimationBlueprintLibrary if any; else export
abp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion")
# Try get all editor properties somehow
# Check parent class
L("abp parent={}".format(abp.get_editor_property("parent_class") if abp else None))
try:
    L("abp parent_class={}".format(abp.get_editor_property("parent_class")))
except Exception as e:
    L("parent ERR {}".format(e))

# Look at AnimBlueprint's "TargetSkeleton" and compile status
# Dump asset tags
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    ad=ar.get_asset_by_object_path("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion.ABP_KayKitLocomotion")
    L("asset_data={}".format(ad))
except Exception as e:
    L("ar ERR {}".format(e))

# Check if ABP has UbergraphPages / FunctionGraphs via protected - try call_method
for meth in ["GetAllGraphs","GetEventGraphs","GetAnimBlueprintGeneratedClass"]:
    try:
        L("call {} -> {}".format(meth, abp.call_method(meth)))
    except Exception as e:
        L("call {} ERR {}".format(meth,e))

# Read ABP uasset ASCII for Speed VariableSet / BlendSpace / GetVelocity
import re
uasset=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitLocomotion.uasset"
data=open(uasset,"rb").read()
text="".join(chr(b) if 32<=b<127 else " " for b in data)
# extract interesting tokens
keys=["Speed","Direction","IsInAir","BlendSpace","GetVelocity","GetOwningActor","TryGetPawnOwner","VSize","CalculateDirection","BS_KayKit","StateMachine","Locomotion","Idle","Jump"]
for k in keys:
    L("ABP contains '{}': {}".format(k, k in text))

# Find nearby strings around Speed
idx=text.find("Speed")
if idx>=0:
    L("Speed context: {}".format(repr(text[max(0,idx-40):idx+60])))

# Also check BP path from previous sessions - Blueprints folder
assets=unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit", recursive=True, include_folder=False)
L("all kaykit assets count={}".format(len(assets)))
for a in assets:
    if "Blueprint" in a or "/BP_" in a or "AnimBlueprint" in a or "BlendSpace" in a:
        L("  "+a)

flush()
print("VERIFYBP_DONE")