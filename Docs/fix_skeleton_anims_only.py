# -*- coding: utf-8 -*-
"""Import clean skeleton anims only + assign mesh/idle on BP_Enemy_Skeleton."""
from __future__ import print_function
import os
import unreal

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "fix_skeleton_anims_only.txt")
FBX = os.path.join(ROOT, "RawAssets", "KayKitSkeletons", "fbx", "Skeleton_Minion_Clean.fbx")
DEST = "/Game/Characters/Enemies/Skeleton"
DEST_MESH = DEST + "/Mesh"
DEST_ANIM = DEST + "/Animations"
BP_PATH = DEST + "/BP_Enemy_Skeleton"
SK_PATH = DEST_MESH + "/SK_SkeletonMinion"
SKEL_PATH = DEST_MESH + "/SK_SkeletonMinion_Skeleton"
MAT_PATH = DEST + "/Materials/M_SkeletonMinion"


def L(m):
    s = "ANIMONLY: " + str(m)
    try:
        unreal.log(s)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def W(m):
    s = "ANIMONLY WARN: " + str(m)
    try:
        unreal.log_warning(s)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def save(a):
    if not a:
        return
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(a, False)
    except Exception:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e:
            W("save " + str(e))


def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)


def list_anims():
    found = {}
    for folder in (DEST_MESH, DEST_ANIM, DEST):
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            continue
        for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                found[a.get_name()] = (a, path)
    return found


def import_anims(skel):
    ensure_dir(DEST_ANIM)
    task = unreal.AssetImportTask()
    task.filename = FBX
    task.destination_path = DEST_ANIM
    task.destination_name = "SK_SkeletonMinion"
    task.replace_existing = True
    task.automated = True
    task.save = True

    options = unreal.FbxImportUI()
    options.set_editor_property("automated_import_should_detect_type", False)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("import_mesh", False)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("create_physics_asset", False)
    if skel:
        options.set_editor_property("skeleton", skel)
    try:
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    except Exception as e:
        W("mesh_type: " + str(e))
    try:
        options.set_editor_property("original_import_type", unreal.FBXImportType.FBXIT_ANIMATION)
    except Exception:
        pass

    anim_data = options.get_editor_property("anim_sequence_import_data")
    try:
        anim_data.set_editor_property("import_uniform_scale", 1.0)
        anim_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        anim_data.set_editor_property("convert_scene", True)
    except Exception as e:
        W("anim_data: " + str(e))

    task.options = options
    L("import anims only -> " + DEST_ANIM)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if task.result:
        L("result_count=" + str(len(list(task.result))))
        for p in list(task.result)[:30]:
            L("imported " + str(p))
    else:
        W("task.result empty")


def pick_idle(anims):
    prefer = [
        "SK_SkeletonMinion_Anim_Rig_Idle_Rig",
        "SK_SkeletonMinion_Anim_Idle_Rig",
        "Idle_Rig",
    ]
    names = list(anims.keys())
    for p in prefer:
        for n in names:
            if n == p or n.endswith(p) or p in n:
                if "Melee_Idle" in n or "Jump_Idle" in n:
                    continue
                return anims[n][0], n
    for n in names:
        if n.endswith("Idle_Rig") and "Melee_Idle" not in n and "Jump_Idle" not in n and "Lie_Idle" not in n:
            return anims[n][0], n
    for n in names:
        if "Walking_A" in n:
            return anims[n][0], n
    return None, None


def configure_bp(sk, idle, mat):
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if not bp:
        W("no BP")
        return False
    gen = unreal.load_class(None, BP_PATH + ".BP_Enemy_Skeleton_C")
    if not gen:
        W("no generated class")
        return False
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
        W("no mesh comp")
        return False
    if sk:
        try:
            mesh.set_editor_property("skeletal_mesh", sk)
            L("set skeletal_mesh ok")
        except Exception as e:
            W("set sk: " + str(e))
            try:
                mesh.set_skeletal_mesh(sk)
            except Exception as e2:
                W("set_skeletal_mesh: " + str(e2))
    try:
        mesh.set_editor_property("relative_scale3d", unreal.Vector(0.85, 0.85, 0.85))
    except Exception:
        pass
    try:
        mesh.set_editor_property("anim_class", None)
    except Exception:
        pass
    try:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        pass
    if idle:
        try:
            mesh.override_animation_data(idle, True, True, 0.0, 1.0)
            L("idle set ok")
        except Exception as e:
            W("idle: " + str(e))
    if mat:
        for i in range(16):
            try:
                mesh.set_material(i, mat)
            except Exception:
                break
    try:
        cdo.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
    except Exception:
        pass
    save(bp)
    # also update placed actors in dungeon if currently open
    try:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try:
                label = a.get_actor_label() or ""
            except Exception:
                label = ""
            if not label.startswith("Preview_Skeleton"):
                continue
            try:
                m = a.get_editor_property("mesh")
            except Exception:
                m = None
            if m is None:
                try:
                    m = a.mesh
                except Exception:
                    m = None
            if m and sk:
                try:
                    m.set_editor_property("skeletal_mesh", sk)
                except Exception:
                    try:
                        m.set_skeletal_mesh(sk)
                    except Exception:
                        pass
                if idle:
                    try:
                        m.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
                        m.override_animation_data(idle, True, True, 0.0, 1.0)
                    except Exception as e:
                        W("actor idle: " + str(e))
                L("updated placed " + label)
    except Exception as e:
        W("update placed: " + str(e))
    return True


def main():
    open(LOG, "w", encoding="utf-8").write("=== anims only ===\n")
    skel = unreal.EditorAssetLibrary.load_asset(SKEL_PATH)
    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    L("skel=%s sk=%s" % (skel, sk))
    before = list_anims()
    L("before=" + str(len(before)))
    import_anims(skel)
    # also try mesh folder import as animation if still empty
    after = list_anims()
    L("after_first=" + str(len(after)))
    if len(after) == 0:
        W("retry import into Mesh folder as animation")
        task = unreal.AssetImportTask()
        task.filename = FBX
        task.destination_path = DEST_MESH
        task.destination_name = "A_SkeletonMinion"
        task.replace_existing = True
        task.automated = True
        task.save = True
        options = unreal.FbxImportUI()
        options.set_editor_property("automated_import_should_detect_type", False)
        options.set_editor_property("import_as_skeletal", True)
        options.set_editor_property("import_mesh", False)
        options.set_editor_property("import_animations", True)
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        options.set_editor_property("create_physics_asset", False)
        options.set_editor_property("skeleton", skel)
        try:
            options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
        except Exception:
            pass
        task.options = options
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        if task.result:
            for p in list(task.result)[:30]:
                L("retry imported " + str(p))
        after = list_anims()
        L("after_retry=" + str(len(after)))

    for n in sorted(after.keys()):
        L("anim:" + n)
    idle, idle_n = pick_idle(after)
    L("idle=" + str(idle_n))
    if sk and mat:
        for i in range(16):
            try:
                sk.set_material(i, mat)
            except Exception:
                break
        save(sk)
    configure_bp(sk, idle[0] if isinstance(idle, tuple) else idle, mat)
    # fix pick return
    idle_asset = after.get(idle_n, (None, None))[0] if idle_n else None
    if idle_asset is None and idle_n and idle_n in after:
        idle_asset = after[idle_n][0]
    if idle_n and idle_n in after:
        configure_bp(sk, after[idle_n][0], mat)
    try:
        unreal.EditorAssetLibrary.save_directory(DEST, True, True)
    except Exception:
        pass
    # if dungeon open, save
    try:
        w = unreal.EditorLevelLibrary.get_editor_world()
        if w and "Map_Dungeon" in w.get_path_name():
            unreal.EditorLevelLibrary.save_current_level()
            L("dungeon resaved")
    except Exception:
        pass
    L("DONE")


main()
