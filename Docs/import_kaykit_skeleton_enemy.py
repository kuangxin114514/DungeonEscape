# -*- coding: utf-8 -*-
"""Import KayKit Skeleton Minion enemy + place preview in Map_Dungeon (UE4.27)."""
import unreal
import os

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "import_kaykit_skeleton_enemy.txt")
FBX = os.path.join(ROOT, "RawAssets", "KayKitSkeletons", "fbx", "Skeleton_Minion.fbx")
TEX = os.path.join(ROOT, "RawAssets", "KayKitSkeletons", "fbx", "skeleton_texture.png")

DEST = "/Game/Characters/Enemies/Skeleton"
DEST_MESH = DEST + "/Mesh"
DEST_ANIM = DEST + "/Animations"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Materials"

SK_NAME = "SK_SkeletonMinion"
TEX_NAME = "T_SkeletonMinion"
MAT_NAME = "M_SkeletonMinion"
BP_NAME = "BP_Enemy_Skeleton"
ABP_NAME = "ABP_SkeletonMinion"

DUNGEON = "/Game/Maps/Dungeon/Map_Dungeon"
HUB = "/Game/Maps/Hub/Map_Hub"

IDLE_KEYS = ("Idle_Rig", "Idle", "Idle_Combat_Rig", "Unarmed_Idle_Rig")
WALK_KEYS = ("Walking_A_Rig", "Walking_A", "Walking_D_Skeletons_Rig", "Walking_B_Rig")
ATTACK_KEYS = (
    "1H_Melee_Attack_Chop_Rig",
    "1H_Melee_Attack_Chop",
    "1H_Melee_Attack_Slice_Horizontal_Rig",
    "Unarmed_Melee_Attack_Punch_A_Rig",
)


def L(msg):
    line = "SKEL: " + str(msg)
    try:
        unreal.log(line)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def W(msg):
    line = "SKEL WARN: " + str(msg)
    try:
        unreal.log_warning(line)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def save(asset):
    if not asset:
        return
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(asset, False)
    except Exception:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception as e:
            W("save " + str(e))


def import_texture():
    ensure_dir(DEST_TEX)
    full = DEST_TEX + "/" + TEX_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    task = unreal.AssetImportTask()
    task.filename = TEX
    task.destination_path = DEST_TEX
    task.destination_name = TEX_NAME
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = unreal.EditorAssetLibrary.load_asset(full)
    L("texture=" + str(tex))
    return tex


def make_material(tex):
    ensure_dir(DEST_MAT)
    full = DEST_MAT + "/" + MAT_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(MAT_NAME, DEST_MAT, unreal.Material, factory)
    if not mat:
        W("material create failed")
        return None
    try:
        ts = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -350, 0)
        if tex and ts:
            ts.set_editor_property("texture", tex)
            unreal.MaterialEditingLibrary.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        const_r = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 200)
        if const_r:
            const_r.set_editor_property("r", 0.85)
            unreal.MaterialEditingLibrary.connect_material_property(const_r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    except Exception as e:
        W("material wire: " + str(e))
    save(mat)
    L("material=" + full)
    return unreal.EditorAssetLibrary.load_asset(full)


def import_minion_fbx():
    ensure_dir(DEST_MESH)
    ensure_dir(DEST_ANIM)
    if not os.path.isfile(FBX):
        W("FBX missing: " + FBX)
        return None

    # wipe previous skeleton enemy mesh/anims only
    for folder in (DEST_MESH, DEST_ANIM):
        try:
            for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
                unreal.EditorAssetLibrary.delete_asset(a)
        except Exception:
            pass

    task = unreal.AssetImportTask()
    task.filename = FBX
    task.destination_path = DEST_MESH
    task.destination_name = SK_NAME
    task.replace_existing = True
    task.automated = True
    task.save = True

    options = unreal.FbxImportUI()
    options.set_editor_property("automated_import_should_detect_type", False)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("create_physics_asset", True)
    options.set_editor_property("skeleton", None)
    try:
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    except Exception:
        pass

    sk_data = options.get_editor_property("skeletal_mesh_import_data")
    try:
        sk_data.set_editor_property("import_uniform_scale", 1.0)
        sk_data.set_editor_property("use_t0_as_ref_pose", True)
        sk_data.set_editor_property("convert_scene", True)
        sk_data.set_editor_property("force_front_x_axis", False)
        sk_data.set_editor_property("transform_vertex_to_absolute", True)
        sk_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)
    except Exception as e:
        W("sk_data: " + str(e))

    anim_data = options.get_editor_property("anim_sequence_import_data")
    try:
        anim_data.set_editor_property("import_uniform_scale", 1.0)
        anim_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        anim_data.set_editor_property("convert_scene", True)
    except Exception as e:
        W("anim_data: " + str(e))

    task.options = options
    L("importing FBX (mesh+anims) ...")
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if task.result:
        L("imported_count=" + str(len(list(task.result))))
        for p in list(task.result)[:12]:
            L("imported: " + str(p))

    sk_path = DEST_MESH + "/" + SK_NAME
    sk = unreal.EditorAssetLibrary.load_asset(sk_path)
    if not sk:
        for c in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
            a = unreal.EditorAssetLibrary.load_asset(c)
            if isinstance(a, unreal.SkeletalMesh):
                sk = a
                sk_path = c
                break
    L("skeletal_mesh=" + str(sk_path) + " -> " + str(sk))
    return sk


def apply_material(sk, mat):
    if not sk or not mat:
        return
    try:
        for i in range(16):
            try:
                sk.set_material(i, mat)
            except Exception:
                break
        save(sk)
        L("materials applied")
    except Exception as e:
        W("apply_material: " + str(e))


def list_anims():
    found = {}
    for folder in (DEST_MESH, DEST_ANIM, DEST):
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            continue
        for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                found[a.get_name()] = a
    L("anim_count=" + str(len(found)))
    return found


def pick_anim(anims, keys):
    names = list(anims.keys())
    for key in keys:
        for n in names:
            if n == key or n.endswith("_" + key) or key in n:
                return anims[n], n
    for key in keys:
        kl = key.lower().replace("_rig", "")
        for n in names:
            if kl in n.lower():
                return anims[n], n
    return None, None


def create_character_bp(sk, idle_anim):
    ensure_dir(DEST)
    full = DEST + "/" + BP_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", unreal.Character)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, DEST, None, factory)
    if not bp:
        W("BP create failed")
        return None
    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass

    gen = None
    try:
        gen = bp.generated_class()
    except Exception:
        try:
            gen = bp.get_editor_property("generated_class")
        except Exception:
            pass
    if not gen:
        W("no generated_class")
        return unreal.EditorAssetLibrary.load_asset(full)

    cdo = unreal.get_default_object(gen)
    mesh = None
    try:
        mesh = cdo.get_editor_property("mesh")
    except Exception:
        try:
            mesh = cdo.mesh
        except Exception:
            pass
    if not mesh:
        W("no mesh component")
        return unreal.EditorAssetLibrary.load_asset(full)

    try:
        mesh.set_editor_property("skeletal_mesh", sk)
    except Exception:
        try:
            mesh.set_skeletal_mesh(sk)
        except Exception as e:
            W("set skeletal_mesh: " + str(e))

    # Minion is already small; slight extra shrink vs knight if still tall
    try:
        mesh.set_editor_property("relative_scale3d", unreal.Vector(0.85, 0.85, 0.85))
    except Exception:
        try:
            mesh.set_relative_scale3d(unreal.Vector(0.85, 0.85, 0.85))
        except Exception as e:
            W("scale: " + str(e))

    try:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        pass
    if idle_anim:
        try:
            mesh.override_animation_data(idle_anim, True, True, 0.0, 1.0)
            L("idle override ok")
        except Exception as e:
            W("override_animation_data: " + str(e))
            try:
                mesh.set_animation(idle_anim)
            except Exception as e2:
                W("set_animation: " + str(e2))

    # Capsule a bit smaller for minion
    try:
        cap = cdo.get_editor_property("capsule_component")
        if cap:
            try:
                cap.set_editor_property("capsule_half_height", 55.0)
                cap.set_editor_property("capsule_radius", 28.0)
            except Exception:
                pass
    except Exception:
        pass

    # No player control
    try:
        cdo.set_editor_property("ai_controller_class", None)
    except Exception:
        pass
    try:
        cdo.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
    except Exception:
        pass

    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass
    save(bp)
    L("BP=" + full)
    return unreal.EditorAssetLibrary.load_asset(full)


def place_in_dungeon(bp):
    if not bp:
        return
    # remember current map to restore (prefer Hub if that was open)
    prev = None
    try:
        w = unreal.EditorLevelLibrary.get_editor_world()
        if w:
            prev = w.get_path_name()
    except Exception:
        pass

    L("loading Map_Dungeon")
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON)
    except Exception as e:
        W("load_map: " + str(e))
        return

    # remove old preview skeletons
    try:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in actors:
            try:
                label = a.get_actor_label()
            except Exception:
                label = ""
            if label.startswith("Preview_Skeleton"):
                unreal.EditorLevelLibrary.destroy_actor(a)
                L("removed " + label)
    except Exception as e:
        W("cleanup: " + str(e))

    # find PlayerStart
    base = unreal.Vector(-700.0, -30.0, 100.0)
    try:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if isinstance(a, unreal.PlayerStart):
                base = a.get_actor_location()
                L("PlayerStart @ " + str(base))
                break
    except Exception as e:
        W("PlayerStart: " + str(e))

    gen = None
    try:
        gen = bp.generated_class()
    except Exception:
        try:
            gen = bp.get_editor_property("generated_class")
        except Exception:
            pass
    if not gen:
        W("no bp class for spawn")
        return

    offsets = [
        unreal.Vector(250.0, 80.0, 0.0),
        unreal.Vector(420.0, -120.0, 0.0),
    ]
    for i, off in enumerate(offsets):
        loc = unreal.Vector(base.x + off.x, base.y + off.y, base.z + off.z)
        rot = unreal.Rotator(0.0, 180.0 if i == 0 else 120.0, 0.0)
        try:
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(gen, loc, rot)
        except Exception as e:
            W("spawn fail: " + str(e))
            actor = None
        if not actor:
            continue
        try:
            actor.set_actor_label("Preview_Skeleton_%d" % (i + 1))
        except Exception:
            pass
        try:
            actor.set_actor_location(loc, False, False)
        except Exception:
            pass
        L("placed Preview_Skeleton_%d @ %s" % (i + 1, loc))

    try:
        unreal.EditorLevelLibrary.save_current_level()
        L("dungeon saved")
    except Exception as e:
        W("save level: " + str(e))

    # restore previous map if it was Hub
    try:
        if prev and ("Map_Hub" in prev):
            unreal.EditorLoadingAndSavingUtils.load_map(HUB)
            L("hub restored")
    except Exception as e:
        W("restore hub: " + str(e))


def main():
    open(LOG, "w", encoding="utf-8").write("=== import kaykit skeleton enemy ===\n")
    L("FBX exists=" + str(os.path.isfile(FBX)))
    L("TEX exists=" + str(os.path.isfile(TEX)))

    tex = import_texture()
    mat = make_material(tex)
    sk = import_minion_fbx()
    if not sk:
        L("FAIL no skeletal mesh")
        return
    apply_material(sk, mat)

    anims = list_anims()
    idle, idle_n = pick_anim(anims, IDLE_KEYS)
    walk, walk_n = pick_anim(anims, WALK_KEYS)
    atk, atk_n = pick_anim(anims, ATTACK_KEYS)
    L("idle=%s walk=%s attack=%s" % (idle_n, walk_n, atk_n))
    sample = sorted([n for n in anims.keys()])[:25]
    L("anim_sample=" + ", ".join(sample))

    bp = create_character_bp(sk, idle)
    place_in_dungeon(bp)

    # save all under DEST
    try:
        unreal.EditorAssetLibrary.save_directory(DEST, True, True)
    except Exception:
        pass
    L("DONE DEST=" + DEST)
    L("BP=/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton")


main()
