# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_assign3.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("[ASN3] "+str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

SKEL_ALIAS="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
SKEL42="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skel42"
NULLS=[
"/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig",
"/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig",
"/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig",
]
CHOP="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop"

sa=unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
s42=unreal.EditorAssetLibrary.load_asset(SKEL42)
chop=unreal.EditorAssetLibrary.load_asset(CHOP)
idle=unreal.EditorAssetLibrary.load_asset(NULLS[0])
L("alias={} s42={} chop.skel={}".format(sa,s42,chop.get_editor_property("skeleton")))

# EditorSkeletalMeshLibrary methods
esml=[n for n in dir(unreal.EditorSkeletalMeshLibrary) if not n.startswith("_")]
L("ESML={}".format(esml))

# Try call_method SetSkeleton on idle
for meth,args in [
    ("SetSkeleton",(sa,)),
    ("SetSkeleton",(s42,)),
    ("set_skeleton",(sa,)),
]:
    try:
        r=idle.call_method(meth, args)
        L("call_method {} -> {} skel={}".format(meth,r,idle.get_editor_property("skeleton")))
    except Exception as e:
        L("call_method {} ERR {}".format(meth,e))

# Try AnimationLibrary.set_editor_property on sequence? 
try:
    unreal.AnimationLibrary.set_editor_property(idle, "skeleton", sa)
    L("AL.set_editor_property skeleton OK -> {}".format(idle.get_editor_property("skeleton")))
except Exception as e:
    L("AL.set_editor_property ERR {}".format(e))

# Try duplicate chop as template then... no
# Try AssetRegistry force

# Persist alias: rename Skel42 to Mannequin path via rename_asset
ALIAS_PATH="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
# Does alias package file exist?
L("does_asset_exist alias={}".format(unreal.EditorAssetLibrary.does_asset_exist(ALIAS_PATH)))
L("does_asset_exist s42={}".format(unreal.EditorAssetLibrary.does_asset_exist(SKEL42)))

# Save alias package explicitly via save_asset
try:
    r=unreal.EditorAssetLibrary.save_asset(ALIAS_PATH, only_if_is_dirty=False)
    L("save_asset alias -> {}".format(r))
except Exception as e:
    L("save_asset alias ERR {}".format(e))

# Try rename soft object paths: point nulls? can't rename None

# Inspect asset import data on idle for reimport filename
try:
    aid=idle.get_editor_property("asset_import_data")
    L("idle asset_import_data={}".format(aid))
    if aid:
        L("aid props={}".format([p for p in dir(aid) if not p.startswith("_")][:40]))
        try:
            L("source_filenames={}".format(aid.get_editor_property("source_data") if hasattr(aid,"source_data") else "n/a"))
        except Exception as e:
            L("source_data ERR {}".format(e))
        try:
            # FbxAssetImportData
            for p in ["source_file_path","SourceFilePath","file_path","extract_filenames"]:
                try:
                    if hasattr(aid,p):
                        L("aid.{}={}".format(p,getattr(aid,p)))
                    else:
                        L("aid.get {}={}".format(p,aid.get_editor_property(p)))
                except Exception as e:
                    L("aid {} ERR {}".format(p,e))
            if hasattr(aid,"extract_filenames"):
                L("extract_filenames={}".format(aid.extract_filenames()))
            if hasattr(aid,"get_first_filename"):
                L("get_first_filename={}".format(aid.get_first_filename()))
        except Exception as e:
            L("aid detail ERR {}".format(e))
except Exception as e:
    L("aid top ERR {}".format(e))

# Try get_editor_property on all writable-looking anim props
try:
    # list editor properties via unreal
    pass
except Exception:
    pass

# Check if we can use unreal.EditorAssetLibrary.duplicate then replace - 
# Alternative: create AnimSequence via factory with skeleton, copy raw tracks via AnimationLibrary
L("idle num_frames try AL={}".format(unreal.AnimationLibrary.get_num_frames(idle) if hasattr(unreal.AnimationLibrary,"get_num_frames") else "n/a"))
try:
    L("idle frames={}".format(unreal.AnimationLibrary.get_num_frames(idle)))
    L("idle len={}".format(unreal.AnimationLibrary.get_sequence_length(idle)))
    tracks=unreal.AnimationLibrary.get_animation_track_names(idle)
    L("idle tracks count={} sample={}".format(len(tracks), list(tracks)[:10]))
except Exception as e:
    L("idle track ERR {}".format(e))

# Can finalize_bone_animation somehow attach skeleton?
# Try modify + force property via ObjectRedirector

# Soft object path replace from a DUMMY path into anim? 
# First inject by loading as package and...

# Try: duplicate a WORKING locomotion-like anim that HAS skeleton - is there Idle without _Rig?
anims=unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Mesh", recursive=False, include_folder=False)
idle_like=[p for p in anims if "Idle" in p or "Walking" in p or "Running" in p]
L("idle_like={}".format(idle_like))
for p in idle_like:
    a=unreal.EditorAssetLibrary.load_asset(p)
    try:
        sk=a.get_editor_property("skeleton")
    except Exception:
        sk="?"
    L("  {} class={} skel={}".format(p, a.get_class().get_name(), sk))

flush()
print("ASN3_DONE")