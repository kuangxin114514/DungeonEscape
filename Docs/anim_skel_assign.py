# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_skel_assign.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("[SKELASN] "+str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

SKEL_ALIAS="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
IDLE="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig"
sa=unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
idle=unreal.EditorAssetLibrary.load_asset(IDLE)
L("alias={} bones={}".format(sa, len(sa.get_editor_property("bone_tree")) if sa else None))
L("idle skel before={}".format(idle.get_editor_property("skeleton") if idle else None))

# Probe APIs
L("anim methods with skel/Skeleton: "+str([n for n in dir(idle) if "skel" in n.lower() or "Skeleton" in n]))
L("has AnimationLibrary={}".format(hasattr(unreal,"AnimationLibrary")))
L("has EditorAnimUtils={}".format(hasattr(unreal,"EditorAnimUtils")))
L("has AnimBlueprintLibrary={}".format(hasattr(unreal,"AnimBlueprintLibrary")))
for name in ["AnimationBlueprintLibrary","AnimSequenceExtensions","AnimationEditorUtils","EditorAssetLibrary","AssetToolsHelpers","AnimationLibrary"]:
    if hasattr(unreal,name):
        mod=getattr(unreal,name)
        hits=[n for n in dir(mod) if "skel" in n.lower() or "Skeleton" in n or "assign" in n.lower()]
        L("{} hits={}".format(name, hits[:40]))

# Try package save for alias
pkg=sa.get_outer()
L("alias outer={} class={}".format(pkg, pkg.get_class().get_name() if pkg else None))
try:
    pkg.mark_package_dirty()
    L("mark dirty OK")
except Exception as e:
    L("mark dirty ERR {}".format(e))
try:
    ok=unreal.EditorLoadingAndSavingUtils.save_packages([pkg], only_dirty=False)
    L("save_packages -> {}".format(ok))
except Exception as e:
    L("save_packages ERR {}".format(e))
try:
    ok=unreal.EditorLoadingAndSavingUtils.save_dirty_packages(save_map_packages=False, save_content_packages=True)
    L("save_dirty -> {}".format(ok))
except Exception as e:
    L("save_dirty ERR {}".format(e))

# Try assign skeleton via possible APIs
assigned=False
if hasattr(unreal,"AnimationLibrary"):
    try:
        unreal.AnimationLibrary.set_animation_skeleton(idle, sa)  # guess
        L("AnimationLibrary.set_animation_skeleton OK")
        assigned=True
    except Exception as e:
        L("AnimationLibrary guess ERR {}".format(e))

# Try call on object
for meth in ["set_skeleton","SetSkeleton","assign_skeleton"]:
    if hasattr(idle, meth):
        try:
            getattr(idle,meth)(sa)
            L("idle.{} OK".format(meth)); assigned=True
        except Exception as e:
            L("idle.{} ERR {}".format(meth,e))

# Try EditorAssetLibrary duplicate with skeleton? 
# Use AssetImport for nothing

# Try unreal.AnimSequence -> property via _set / private
try:
    # some builds allow via
    idle.set_editor_property("Skeleton", sa)
    L("set Skeleton capped OK"); assigned=True
except Exception as e:
    L("set Skeleton capped ERR {}".format(e))

# Check AnimationBlueprintLibrary methods containing 'Replace' or 'Retarget'
if hasattr(unreal,"AnimationBlueprintLibrary"):
    hits=[n for n in dir(unreal.AnimationBlueprintLibrary) if not n.startswith("_")]
    L("ABL methods sample={}".format([h for h in hits if any(k in h.lower() for k in ["skel","retarget","notify","curve","bone","assign","set_"])])[:50])

# Try consolidate / replace references from None? can't

# Use IAssetTools fixup
try:
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    L("AssetTools dir skel={}".format([n for n in dir(tools) if "skel" in n.lower() or "rename" in n.lower() or "fix" in n.lower()][:30]))
except Exception as e:
    L("tools ERR {}".format(e))

# Try loading C++ exposed EditorScripting
for name in dir(unreal):
    if "Anim" in name and ("Util" in name or "Library" in name or "Editor" in name):
        L("unreal."+name)

L("idle skel after={}".format(idle.get_editor_property("skeleton")))
flush()
print("SKELASN_DONE")