# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_skel_persist.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("[SKELPER] "+str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

SKEL_ALIAS="/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
SKEL_ORIG="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
MESH="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
NEW_SKEL_PATH="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skel42"
DEST_PKG="/Game/Characters/Player/KayKit/Mesh"

def bones(sk):
    if not sk: return None
    try:
        return len(sk.get_editor_property("bone_tree"))
    except Exception as e:
        return "ERR:"+str(e)

sa=unreal.EditorAssetLibrary.load_asset(SKEL_ALIAS)
so=unreal.EditorAssetLibrary.load_asset(SKEL_ORIG)
mesh=unreal.EditorAssetLibrary.load_asset(MESH)
L("alias bones={} orig bones={}".format(bones(sa), bones(so)))
L("mesh skeleton={}".format(mesh.get_editor_property("skeleton") if mesh else None))

abl=[n for n in dir(unreal.AnimationLibrary) if not n.startswith("_")]
L("AnimationLibrary ALL={}".format(abl))

# Delete if exists then duplicate
if unreal.EditorAssetLibrary.does_asset_exist(NEW_SKEL_PATH):
    unreal.EditorAssetLibrary.delete_asset(NEW_SKEL_PATH)
    L("deleted existing new skel")

ok=unreal.EditorAssetLibrary.duplicate_asset(SKEL_ALIAS, NEW_SKEL_PATH)
L("duplicate_asset alias->Skel42 = {}".format(ok))
newsa=unreal.EditorAssetLibrary.load_asset(NEW_SKEL_PATH)
L("newsa={} bones={}".format(newsa, bones(newsa)))

# AssetTools duplicate as well
try:
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    dup=tools.duplicate_asset("SK_KayKitKnight_Skel42_AT", DEST_PKG, sa)
    L("tools.duplicate_asset -> {} bones={}".format(dup, bones(dup)))
except Exception as e:
    L("tools.duplicate ERR {}".format(e))

# SkeletonFactory
try:
    factory=unreal.SkeletonFactory()
    L("SkeletonFactory props={}".format([p for p in dir(factory) if not p.startswith("_")][:50]))
    for prop in ["target_skeletal_mesh","TargetSkeletalMesh","preview_skeletal_mesh","PreviewSkeletalMesh"]:
        try:
            factory.set_editor_property(prop, mesh)
            L("factory set {} OK".format(prop))
        except Exception as e:
            L("factory set {} ERR {}".format(prop,e))
    created=tools.create_asset("SK_KayKitKnight_SkelFromMesh", DEST_PKG, unreal.Skeleton, factory)
    L("create_asset Skeleton -> {} bones={}".format(created, bones(created)))
except Exception as e:
    L("SkeletonFactory/create ERR {}".format(e))

# Save
for a in [newsa]:
    if a:
        try:
            r=unreal.EditorAssetLibrary.save_loaded_asset(a)
            L("save_loaded {} -> {}".format(a.get_name(), r))
        except Exception as e:
            L("save ERR {}".format(e))

# Try set mesh skeleton
for target_name, target in [("ORIG", so), ("NEW42", newsa), ("ALIAS", sa)]:
    if not target: continue
    try:
        mesh.set_editor_property("skeleton", target)
        L("mesh.set skeleton {} OK now={}".format(target_name, mesh.get_editor_property("skeleton")))
    except Exception as e:
        L("mesh.set skeleton {} ERR {}".format(target_name, e))

L("mesh skel methods={}".format([n for n in dir(mesh) if "skel" in n.lower() or "Skeleton" in n]))
L("has EditorSkeletalMeshLibrary={}".format(hasattr(unreal,"EditorSkeletalMeshLibrary")))

# List anims with null skeleton under KayKit
anim_paths=unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit", recursive=True, include_folder=False)
nulls=[]; with_skel=[]; other=[]
for p in anim_paths:
    a=unreal.EditorAssetLibrary.load_asset(p)
    if not a: continue
    cn=a.get_class().get_name()
    if cn in ("AnimSequence","AnimSequenceBase","AnimMontage","BlendSpace","BlendSpace1D","AimOffsetBlendSpace","AimOffsetBlendSpace1D"):
        try:
            sk=a.get_editor_property("skeleton")
        except Exception:
            sk="N/A"
        if sk is None:
            nulls.append((p,cn))
        else:
            with_skel.append((p,cn,str(sk)))
    elif "Anim" in cn or "Blend" in cn:
        other.append((p,cn))
L("NULL skeleton anims count={}".format(len(nulls)))
for p,cn in nulls[:40]:
    L("  NULL {} {}".format(cn,p))
L("WITH skeleton count={}".format(len(with_skel)))
for p,cn,sk in with_skel[:20]:
    L("  WITH {} {} -> {}".format(cn,p,sk))
L("other={}".format(other[:20]))
flush()
print("SKELPER_DONE")