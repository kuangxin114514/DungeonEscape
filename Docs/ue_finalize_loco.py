# -*- coding: utf-8 -*-
import unreal

abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
mat_path = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"

abp = unreal.EditorAssetLibrary.load_asset(abp_path)
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
sk_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
mat = unreal.EditorAssetLibrary.load_asset(mat_path)

# Compile via BlueprintEditorLibrary if present
compiled = False
for cls_name in ["BlueprintEditorLibrary", "KismetSystemLibrary"]:
    if hasattr(unreal, cls_name):
        mod = getattr(unreal, cls_name)
        unreal.log("{} methods {}".format(cls_name, [n for n in dir(mod) if "compile" in n.lower() or "Blueprint" in n][:20]))
        if hasattr(mod, "compile_blueprint"):
            try:
                mod.compile_blueprint(abp)
                unreal.log("compiled via {}".format(cls_name))
                compiled = True
            except Exception as e:
                unreal.log("compile via {} ERR {}".format(cls_name, e))

# Also try EditorAssetLibrary / AssetTools
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
except Exception:
    at = None

# Force-set every non-world CharacterMesh0 under the BP package
updated = 0
for obj in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    p = obj.get_path_name()
    if "BP_KayKitKnight" not in p:
        continue
    # Skip live world actors (Transient.World)
    if "/Engine/Transient" in p or "PersistentLevel" in p:
        unreal.log("skip world {}".format(p))
        continue
    try:
        obj.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        obj.set_editor_property("anim_class", abp_cls)
        obj.set_editor_property("skeletal_mesh", sk_mesh)
        try:
            obj.set_editor_property("override_materials", [mat])
        except Exception:
            pass
        updated += 1
        unreal.log("UPDATED {} mode={} anim={}".format(
            p, obj.get_editor_property("animation_mode"), obj.get_editor_property("anim_class")))
    except Exception as e:
        unreal.log("update ERR {} {}".format(p, e))

unreal.log("updated_count={}".format(updated))

# Also set on CDO explicitly again
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
mesh_comp = cdo.get_editor_property("mesh")
mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh_comp.set_editor_property("anim_class", abp_cls)
mesh_comp.set_editor_property("skeletal_mesh", sk_mesh)
mesh_comp.set_editor_property("override_materials", [mat])
unreal.log("CDO mode={} anim={}".format(mesh_comp.get_editor_property("animation_mode"), mesh_comp.get_editor_property("anim_class")))

# Ensure sword/shield materials too
for obj in unreal.ObjectIterator(unreal.StaticMeshComponent):
    p = obj.get_path_name()
    if "BP_KayKitKnight" not in p:
        continue
    if "/Engine/Transient" in p or "PersistentLevel" in p:
        continue
    try:
        sm = obj.get_editor_property("static_mesh")
        if sm and ("Sword" in sm.get_name() or "Shield" in sm.get_name()):
            try:
                obj.set_editor_property("override_materials", [mat])
            except Exception:
                pass
            # ensure sockets
            try:
                sock = obj.get_editor_property("attach_socket_name")
                unreal.log("weapon {} socket={} mesh={}".format(obj.get_name(), sock, sm.get_name()))
            except Exception as e:
                unreal.log("weapon {} sock ERR {}".format(obj.get_name(), e))
    except Exception as e:
        unreal.log("sm ERR {}".format(e))

# Mark ABP dirty and save; try recompile by touching target_skeleton
skel = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX")
abp.set_editor_property("target_skeleton", skel)
unreal.EditorAssetLibrary.save_asset(abp_path)
unreal.EditorAssetLibrary.save_asset(bp_path)

# Reload abp class after save
abp_cls2 = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
unreal.log("abp_cls2={}".format(abp_cls2))

# Consistency
bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
unreal.log("match mesh={} abp={} bs={}".format(
    sk_mesh.get_editor_property("skeleton").get_name(),
    abp.get_editor_property("target_skeleton").get_name(),
    bs.get_editor_property("skeleton").get_name()))

unreal.log("FINALIZE_DONE")