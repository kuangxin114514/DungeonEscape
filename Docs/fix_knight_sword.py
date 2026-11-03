# -*- coding: utf-8 -*-
"""Reimport Knight_UE.fbx with fixed handslot skinning; refresh material + BP idle."""
import unreal
import os

FBX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\Knight_UE.fbx"
TEX_FILE = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\knight_texture.png"
DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Materials"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
TEX_PATH = DEST_TEX + "/T_KayKitKnight"
MAT_PATH = DEST_MAT + "/M_KayKitKnight"
BP_PATH = DEST + "/BP_KayKitKnight"
IDLE_PATH = DEST_MESH + "/SK_KayKitKnight_Anim_Rig_Idle_Rig"

def log(m): unreal.log("FIXSWORD: " + str(m))
def warn(m): unreal.log_warning("FIXSWORD: " + str(m))
def save(a):
    if a:
        try: unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e: warn("save " + str(e))

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def import_fbx():
    ensure_dir(DEST_MESH)
    task = unreal.AssetImportTask()
    task.filename = FBX
    task.destination_path = DEST_MESH
    task.destination_name = "SK_KayKitKnight"
    task.replace_existing = True
    task.automated = True
    task.save = True
    opts = unreal.FbxImportUI()
    opts.import_mesh = True
    opts.import_as_skeletal = True
    opts.import_animations = True
    opts.import_materials = False
    opts.import_textures = False
    opts.create_physics_asset = True
    opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    sk = opts.skeletal_mesh_import_data
    sk.set_editor_property("import_translation", unreal.Vector(0, 0, 0))
    sk.set_editor_property("import_rotation", unreal.Rotator(0, 0, 0))
    sk.set_editor_property("import_uniform_scale", 1.0)
    sk.set_editor_property("convert_scene", True)
    sk.set_editor_property("force_front_x_axis", False)
    sk.set_editor_property("transform_vertex_to_absolute", True)
    try:
        sk.set_editor_property("use_t0_as_ref_pose", True)
    except Exception:
        pass
    try:
        sk.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)
    except Exception:
        pass
    # Keep nested bone meshes if any still present
    try:
        opts.skeletal_mesh_import_data.set_editor_property("import_meshes_in_bone_hierarchy", True)
    except Exception:
        pass
    try:
        opts.anim_sequence_import_data.set_editor_property("import_meshes_in_bone_hierarchy", True)
    except Exception:
        pass
    opts.anim_sequence_import_data.set_editor_property(
        "animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME
    )
    task.options = opts
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sk_asset = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    log("sk=" + str(sk_asset))
    return sk_asset

def ensure_material(sk):
    ensure_dir(DEST_TEX)
    ensure_dir(DEST_MAT)
    tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    if not tex or True:
        task = unreal.AssetImportTask()
        task.filename = TEX_FILE
        task.destination_path = DEST_TEX
        task.destination_name = "T_KayKitKnight"
        task.replace_existing = True
        task.automated = True
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    log("tex=" + str(tex))
    mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    if not mat:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "M_KayKitKnight", DEST_MAT, unreal.Material, unreal.MaterialFactoryNew()
        )
    if mat and tex:
        try:
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            ts = unreal.MaterialEditingLibrary.create_material_expression(
                mat, unreal.MaterialExpressionTextureSample, -400, 0
            )
            ts.set_editor_property("texture", tex)
            unreal.MaterialEditingLibrary.connect_material_property(
                ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
            )
            # Stylized: slight unlit boost via emissive so not charcoal under bad light
            unreal.MaterialEditingLibrary.connect_material_property(
                ts, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR
            )
            try:
                mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
            except Exception:
                pass
            unreal.MaterialEditingLibrary.recompile_material(mat)
            save(mat)
            log("mat_rebuilt")
        except Exception as e:
            warn("mat_build " + str(e))
    if sk and mat:
        try:
            old = list(sk.get_editor_property("materials") or [])
            new_list = []
            for slot in (old if old else [None]):
                sm = unreal.SkeletalMaterial()
                sm.set_editor_property("material_interface", mat)
                try:
                    if slot is not None:
                        sn = slot.get_editor_property("material_slot_name")
                        if sn:
                            sm.set_editor_property("material_slot_name", sn)
                except Exception:
                    pass
                new_list.append(sm)
            if not new_list:
                sm = unreal.SkeletalMaterial()
                sm.set_editor_property("material_interface", mat)
                new_list = [sm]
            sk.set_editor_property("materials", new_list)
            for i in range(16):
                try:
                    sk.set_material(i, mat)
                except Exception:
                    break
            save(sk)
            log("materials_applied slots=%d" % len(new_list))
        except Exception as e:
            warn("apply_mat " + str(e))
    return mat

def pick_idle():
    idle = unreal.EditorAssetLibrary.load_asset(IDLE_PATH)
    if idle:
        return idle
    for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
        a = unreal.EditorAssetLibrary.load_asset(p)
        if not a or a.get_class().get_name() != "AnimSequence":
            continue
        n = a.get_name().lower()
        if "idle" in n and "unarmed" not in n and "chair" not in n and "lie" not in n and "2h" not in n and "melee" not in n:
            return a
    return None

def touch_bp(sk, idle):
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if not bp:
        warn("no bp")
        return
    cls = None
    try:
        cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    except Exception:
        pass
    if not cls:
        try:
            cls = bp.generated_class()
        except Exception as e:
            warn("gen " + str(e))
            return
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    mesh.set_editor_property("relative_rotation", unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0))
    mesh.set_editor_property("relative_scale3d", unreal.Vector(0.75, 0.75, 0.75))
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -90.0))
    if idle:
        try:
            mesh.set_animation(idle)
            log("idle=" + idle.get_name())
        except Exception as e:
            warn("idle " + str(e))
    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass
    log("bp_ok")

def main():
    log("begin")
    if not os.path.isfile(FBX):
        warn("missing fbx")
        return
    sk = import_fbx()
    if not sk:
        warn("import failed")
        return
    ensure_material(sk)
    idle = pick_idle()
    log("idle_asset=" + (idle.get_name() if idle else "None"))
    touch_bp(sk, idle)
    ensure_material(sk)
    log("DONE")

main()
