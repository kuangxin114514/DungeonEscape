# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_abp_t382.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T382: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
ABP="/Game/Characters/Enemies/Skeleton/ABP_SkeletonMinion"
# also search other folders
cands=[ABP,
"/Game/Characters/Enemies/Skeleton/Animations/ABP_SkeletonMinion",
"/Game/Characters/Enemies/ABP_SkeletonMinion"]

# Clear AnimClass on skeleton BP mesh templates
bp=unreal.load_asset(BP)
L("bp=%s"%bp)
cleared=0
for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    try:
        ac=o.get_editor_property("anim_class")
    except Exception:
        ac=None
    L("mesh %s anim_class=%s mode=%s"%(o.get_name(), ac, None))
    try:
        o.set_editor_property("anim_class", None)
        cleared+=1
        L("  cleared anim_class")
    except Exception as e:
        L("  clear fail "+str(e))
    try:
        o.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        L("  mode SingleNode")
    except Exception as e:
        L("  mode "+str(e))

# Also CDO
try:
    gen=unreal.load_object(None, BP+".BP_Enemy_Skeleton_C")
    L("gen=%s"%gen)
except Exception as e:
    gen=None; L("gen "+str(e))

try:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    L("bp compiled")
except Exception as e:
    L("bp compile "+str(e))
try:
    unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")
except Exception as e:
    L("bp save "+str(e))

# Delete broken ABP so Play doesn't warn
deleted=False
for path in cands:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        L("found ABP "+path)
        try:
            ok=unreal.EditorAssetLibrary.delete_asset(path)
            L("delete %s -> %s"%(path, ok))
            deleted=bool(ok) or deleted
        except Exception as e:
            L("delete fail "+str(e))
    else:
        L("no asset "+path)

# Asset registry search
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    arr=ar.get_assets_by_class("AnimBlueprint", True)
    for a in arr:
        try:
            name=str(a.asset_name)
            if "SkeletonMinion" in name or "ABP_Skeleton" in name:
                p="/"+str(a.package_name)+"/"+name if False else str(a.object_path)
                L("reg %s path=%s"%(name, a.object_path))
                try:
                    # object_path like /Game/.../ABP.ABP
                    pkg=str(a.package_name)
                    upath=pkg
                    if unreal.EditorAssetLibrary.does_asset_exist(upath):
                        ok=unreal.EditorAssetLibrary.delete_asset(upath)
                        L("delete reg %s -> %s"%(upath, ok))
                        deleted=True
                except Exception as e:
                    L("reg del "+str(e))
        except Exception:
            pass
except Exception as e:
    L("registry "+str(e))

L("cleared=%d deleted=%s"%(cleared, deleted))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
