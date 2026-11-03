# -*- coding: utf-8 -*-
"""Minimal KayKit Knight fix: reimport skinned FBX, material, SingleNode anim, GM_Hub pawn."""
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
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
# FBX already in cm ~245 tall; scale to ~180cm
MESH_SCALE = 0.75


def log(m): unreal.log("FIXKNIGHT: " + str(m))
def warn(m): unreal.log_warning("FIXKNIGHT: " + str(m))
def save(a):
    if a:
        try: unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e: warn("save " + str(e))


def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)


def load_cls(path_c):
    try:
        return unreal.load_class(None, path_c)
    except Exception as e:
        warn("load_class " + str(e))
        return None


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
    opts.anim_sequence_import_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    opts.anim_sequence_import_data.set_editor_property("import_meshes_in_bone_hierarchy", False)
    task.options = opts
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    sk_asset = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    if not sk_asset:
        # sometimes name is Knight_UE
        for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, False, False):
            a = unreal.EditorAssetLibrary.load_asset(p)
            if a and a.get_class().get_name() == "SkeletalMesh":
                log("found_sk " + p)
                if "Knight" in p or "KayKit" in p:
                    sk_asset = a
                    break
    log("sk=" + str(sk_asset))
    return sk_asset


def ensure_material(sk):
    ensure_dir(DEST_TEX)
    ensure_dir(DEST_MAT)
    tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    if not tex:
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
            # UE4.27 MaterialEditingLibrary
            unreal.MaterialEditingLibrary.connect_material_property(
                unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -350, 0),
                "",
                unreal.MaterialProperty.MP_BASE_COLOR,
            )
        except Exception as e:
            warn("mat_expr_path " + str(e))
        # simpler: use MaterialInstanceConstant from existing or set via constant
        try:
            # rebuild material cleanly
            unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
            ts = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -400, 0)
            ts.set_editor_property("texture", tex)
            unreal.MaterialEditingLibrary.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
            try:
                unreal.MaterialEditingLibrary.connect_material_property(ts, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
                mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
            except Exception:
                pass
            unreal.MaterialEditingLibrary.recompile_material(mat)
            save(mat)
        except Exception as e:
            warn("mat_build " + str(e))
    # apply to all slots
    if sk and mat:
        try:
            mats = sk.get_editor_property("materials")
            log("slot_count=" + str(len(list(mats)) if mats else 0))
            for i, slot in enumerate(list(mats) if mats else []):
                try:
                    slot.set_editor_property("material_interface", mat)
                except Exception:
                    try:
                        unreal.EditorAssetLibrary.set_property(slot, "MaterialInterface", mat)  # noop
                    except Exception:
                        pass
            # preferred API
            try:
                n = sk.get_num_sections(0) if hasattr(sk, "get_num_sections") else 16
            except Exception:
                n = 16
            for i in range(0, 32):
                try:
                    sk.set_material(i, mat)
                except Exception:
                    break
            save(sk)
            log("materials_applied")
        except Exception as e:
            warn("apply_mat " + str(e))
    return mat


def list_anims():
    found = {}
    for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
        a = unreal.EditorAssetLibrary.load_asset(p)
        if a and a.get_class().get_name() == "AnimSequence":
            found[a.get_name()] = a
    log("anim_count=%d" % len(found))
    return found


def pick_idle(anims):
    prefer = []
    for n, a in anims.items():
        nl = n.lower()
        if "idle" in nl and "melee" not in nl and "unarmed" not in nl and "chair" not in nl and "lie" not in nl and "2h" not in nl:
            prefer.append((0 if nl.endswith("idle") or "idle_rig" in nl else 1, n, a))
    prefer.sort()
    return prefer[0][2] if prefer else None


def pick_walk(anims):
    for n, a in anims.items():
        nl = n.lower()
        if "walk" in nl and "back" not in nl and "left" not in nl and "right" not in nl:
            return a
    return None


def ensure_bp(sk, idle):
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if not bp:
        # duplicate ThirdPersonCharacter
        ensure_dir(DEST)
        ok = unreal.EditorAssetLibrary.duplicate_asset(TP_CHAR, BP_PATH)
        log("dup_tp=" + str(ok))
        bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    cls = load_cls(BP_PATH + ".BP_KayKitKnight_C")
    if not cls:
        # after dup name may differ
        a = unreal.EditorAssetLibrary.load_asset(BP_PATH)
        if a:
            try:
                gen = a.generated_class()
                cls = gen
                log("gen_class=" + str(cls))
            except Exception as e:
                warn("gen " + str(e))
    if not cls:
        warn("no BP class")
        return bp
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    try:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception as e:
        warn("anim_mode " + str(e))
    try:
        mesh.set_editor_property("anim_class", None)
    except Exception:
        pass
    mesh.set_editor_property("relative_scale3d", unreal.Vector(MESH_SCALE, MESH_SCALE, MESH_SCALE))
    # FBX exported Z-up -Y forward; typically Yaw -90 for UE character facing
    mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
    half = 90.0
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -half))
    try:
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", half)
        cap.set_editor_property("capsule_radius", 34.0)
    except Exception as e:
        warn("capsule " + str(e))
    if idle:
        try:
            mesh.set_editor_property("animation_data", None)
        except Exception:
            pass
        try:
            # Single node animation to play
            mesh.set_editor_property("override_animation_data", True)  # may not exist
        except Exception:
            pass
        try:
            unreal.EditorSkeletalMeshLibrary  # touch
        except Exception:
            pass
        # UE4 Character mesh: Animation to play when Single Node
        try:
            mesh.set_animation(idle)
            log("set_animation idle=" + idle.get_name())
        except Exception as e:
            warn("set_animation " + str(e))
            try:
                mesh.set_editor_property("animation", idle)
                log("prop animation set")
            except Exception as e2:
                warn("prop anim " + str(e2))
    save(bp)
    # compile
    try:
        unreal.KismetSystemLibrary.compile_blueprint(bp)  # may not exist
    except Exception:
        pass
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass
    log("bp_configured")
    return bp


def set_default_pawn():
    for path in (GM_HUB, TP_GM):
        gm = unreal.EditorAssetLibrary.load_asset(path)
        if not gm:
            warn("no gm " + path)
            continue
        cls = load_cls(path + "." + path.rsplit("/", 1)[-1] + "_C")
        if not cls:
            try:
                cls = gm.generated_class()
            except Exception:
                cls = None
        if not cls:
            warn("no gm class " + path)
            continue
        cdo = unreal.get_default_object(cls)
        pawn_cls = load_cls(BP_PATH + ".BP_KayKitKnight_C")
        if not pawn_cls:
            bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
            try:
                pawn_cls = bp.generated_class()
            except Exception as e:
                warn("pawn gen " + str(e))
        if pawn_cls:
            try:
                cdo.set_editor_property("default_pawn_class", pawn_cls)
                save(gm)
                log("default_pawn set on " + path)
            except Exception as e:
                warn("set pawn " + str(e))


def main():
    log("begin")
    if not os.path.isfile(FBX):
        warn("missing fbx")
        return
    sk = import_fbx()
    if not sk:
        warn("import failed")
        return
    # skeleton check
    try:
        skel = sk.get_editor_property("skeleton")
        log("skeleton=" + str(skel))
    except Exception as e:
        warn("skel " + str(e))
    ensure_material(sk)
    anims = list_anims()
    idle = pick_idle(anims)
    walk = pick_walk(anims)
    log("idle=" + (idle.get_name() if idle else "None"))
    log("walk=" + (walk.get_name() if walk else "None"))
    ensure_bp(sk, idle)
    set_default_pawn()
    # final material re-apply after import may have wiped slots
    ensure_material(sk)
    log("DONE")


main()
