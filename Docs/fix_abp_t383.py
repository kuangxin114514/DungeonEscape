# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_abp_t383.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T383: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
ABP="/Game/Characters/Enemies/Skeleton/Animations/ABP_SkeletonMinion"

bp=unreal.load_asset(BP)
L("bp=%s"%bp)
for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    try:
        L("before %s anim_class=%s"%(o.get_name(), o.get_editor_property("anim_class")))
    except Exception as e:
        L("before "+str(e))
    try:
        o.set_editor_property("anim_class", None); L("cleared anim_class on "+o.get_name())
    except Exception as e:
        L("clear "+str(e))
    try:
        o.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE); L("SingleNode")
    except Exception as e:
        L("mode "+str(e))

try:
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); L("compile bp ok")
except Exception as e:
    L("compile bp "+str(e))
try:
    unreal.EditorAssetLibrary.save_asset(BP); L("save bp ok")
except Exception as e:
    L("save bp "+str(e))

exists=unreal.EditorAssetLibrary.does_asset_exist(ABP)
L("abp exists=%s"%exists)
if exists:
    try:
        ok=unreal.EditorAssetLibrary.delete_asset(ABP)
        L("delete_asset -> %s"%ok)
    except Exception as e:
        L("delete_asset "+str(e))
        try:
            ok=unreal.EditorAssetLibrary.delete_loaded_asset(unreal.load_asset(ABP))
            L("delete_loaded -> %s"%ok)
        except Exception as e2:
            L("delete_loaded "+str(e2))

# verify
L("abp still=%s"%unreal.EditorAssetLibrary.does_asset_exist(ABP))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
