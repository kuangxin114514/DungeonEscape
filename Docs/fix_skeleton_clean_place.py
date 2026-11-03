# -*- coding: utf-8 -*-
"""Replace NaN skeleton anims with clean FBX; build BP_Enemy_Skeleton; place in Map_Dungeon."""
from __future__ import print_function
import os
import unreal

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "fix_skeleton_clean_place.txt")
FBX = os.path.join(ROOT, "RawAssets", "KayKitSkeletons", "fbx", "Skeleton_Minion_Clean.fbx")
DEST = "/Game/Characters/Enemies/Skeleton"
DEST_MESH = DEST + "/Mesh"
DEST_ANIM = DEST + "/Animations"
DEST_MAT = DEST + "/Materials"
BP_PATH = DEST + "/BP_Enemy_Skeleton"
SK_PATH = DEST_MESH + "/SK_SkeletonMinion"
SKEL_PATH = DEST_MESH + "/SK_SkeletonMinion_Skeleton"
MAT_PATH = DEST_MAT + "/M_SkeletonMinion"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
KNIGHT = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
DUNGEON = "/Game/Maps/Dungeon/Map_Dungeon"
HUB = "/Game/Maps/Hub/Map_Hub"


def L(m):
    s = "CLEANSKEL: " + str(m)
    try:
        unreal.log(s)
    except Exception:
        pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")


def W(m):
    s = "CLEANSKEL WARN: " + str(m)
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


def compile_bp(bp):
    for fn in (
        lambda: unreal.KismetEditorUtilities.compile_blueprint(bp),
        lambda: unreal.BlueprintEditorLibrary.compile_blueprint(bp),
    ):
        try:
            fn()
            return True
        except Exception as e:
            W("compile: " + str(e))
    return False


def delete_anim_sequences():
    deleted = 0
    for folder in (DEST_MESH, DEST_ANIM, DEST):
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            continue
        for path in list(unreal.EditorAssetLibrary.list_assets(folder, True, False)):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                try:
                    unreal.EditorAssetLibrary.delete_asset(path)
                    deleted += 1
                except Exception as e:
                    W("del anim " + path + " " + str(e))
    L("deleted_anims=" + str(deleted))


def reimport_clean(skel):
    if not os.path.isfile(FBX):
        W("missing clean fbx")
        return None
    task = unreal.AssetImportTask()
    task.filename = FBX
    task.destination_path = DEST_MESH
    task.destination_name = "SK_SkeletonMinion"
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
    options.set_editor_property("create_physics_asset", False)
    if skel:
        try:
            options.set_editor_property("skeleton", skel)
        except Exception as e:
            W("set skeleton: " + str(e))
    try:
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    except Exception:
        pass

    sk_data = options.get_editor_property("skeletal_mesh_import_data")
    try:
        sk_data.set_editor_property("import_uniform_scale", 1.0)
        sk_data.set_editor_property("use_t0_as_ref_pose", True)
        sk_data.set_editor_property("convert_scene", True)
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
    L("reimport clean FBX...")
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if task.result:
        L("imported=" + str(len(list(task.result))))
        for p in list(task.result)[:20]:
            L("  " + str(p))
    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    L("sk=" + str(sk))
    return sk


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
    for n in sorted(found.keys()):
        L("anim:" + n)
    return found


def pick_idle(anims):
    prefer = [
        "SK_SkeletonMinion_Anim_Rig_Idle_Rig",
        "SK_SkeletonMinion_Anim_Idle_Rig",
        "SK_SkeletonMinion_Anim_Rig_Idle",
    ]
    for p in prefer:
        if p in anims:
            return anims[p], p
    for n, a in anims.items():
        if n.endswith("_Idle_Rig") and "Melee_Idle" not in n and "Jump_Idle" not in n and "Lie_Idle" not in n and "Chair_Idle" not in n and "Floor_Idle" not in n and "Unarmed" not in n and "Combat" not in n:
            return a, n
    for n, a in anims.items():
        if "Walking_A" in n:
            return a, n
    return None, None


def get_gen(bp):
    if not bp:
        return None
    compile_bp(bp)
    for getter in (
        lambda: bp.generated_class(),
        lambda: bp.get_editor_property("generated_class"),
        lambda: unreal.load_class(None, BP_PATH + ".BP_Enemy_Skeleton_C"),
    ):
        try:
            g = getter()
            if g:
                return g
        except Exception as e:
            W("get_gen: " + str(e))
    return None


def ensure_bp(sk, idle, mat):
    if unreal.EditorAssetLibrary.does_asset_exist(BP_PATH):
        try:
            unreal.EditorAssetLibrary.delete_asset(BP_PATH)
            L("deleted old BP")
        except Exception as e:
            W("del bp: " + str(e))

    src = None
    for cand in (TP_CHAR, KNIGHT):
        if unreal.EditorAssetLibrary.does_asset_exist(cand):
            src = cand
            break
    if not src:
        W("no source BP")
        return None

    ok = None
    try:
        ok = unreal.EditorAssetLibrary.duplicate_asset(src, BP_PATH)
        L("dup=" + str(ok))
    except Exception as e:
        W("dup: " + str(e))
    if not unreal.EditorAssetLibrary.does_asset_exist(BP_PATH):
        try:
            tools = unreal.AssetToolsHelpers.get_asset_tools()
            src_obj = unreal.EditorAssetLibrary.load_asset(src)
            tools.duplicate_asset("BP_Enemy_Skeleton", DEST, src_obj)
        except Exception as e:
            W("tools dup: " + str(e))

    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if not bp:
        W("BP missing after dup")
        return None

    compile_bp(bp)
    gen = get_gen(bp)
    L("generated_class=" + str(gen))
    if not gen:
        return bp

    cdo = unreal.get_default_object(gen)
    mesh = None
    try:
        mesh = cdo.get_editor_property("mesh")
    except Exception:
        try:
            mesh = cdo.mesh
        except Exception:
            pass
    if mesh and sk:
        try:
            mesh.set_editor_property("skeletal_mesh", sk)
        except Exception:
            try:
                mesh.set_skeletal_mesh(sk)
            except Exception as e:
                W("set sk: " + str(e))
        try:
            mesh.set_editor_property("relative_scale3d", unreal.Vector(0.85, 0.85, 0.85))
        except Exception:
            try:
                mesh.set_relative_scale3d(unreal.Vector(0.85, 0.85, 0.85))
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
                L("idle override ok")
            except Exception as e:
                W("override: " + str(e))
        if mat:
            for i in range(16):
                try:
                    mesh.set_material(i, mat)
                except Exception:
                    break

    try:
        cap = cdo.get_editor_property("capsule_component")
        if cap:
            cap.set_editor_property("capsule_half_height", 55.0)
            cap.set_editor_property("capsule_radius", 28.0)
    except Exception:
        pass
    try:
        cdo.set_editor_property("auto_possess_player", unreal.AutoReceiveInput.DISABLED)
    except Exception:
        pass

    save(bp)
    compile_bp(bp)
    save(bp)
    L("BP ready")
    return unreal.EditorAssetLibrary.load_asset(BP_PATH)


def place(bp, sk, idle):
    prev = None
    try:
        w = unreal.EditorLevelLibrary.get_editor_world()
        if w:
            prev = w.get_path_name()
    except Exception:
        pass

    unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON)
    L("loaded dungeon")

    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            label = a.get_actor_label() or ""
        except Exception:
            label = ""
        if label.startswith("Preview_Skeleton"):
            unreal.EditorLevelLibrary.destroy_actor(a)
            L("removed " + label)

    base = unreal.Vector(-970.0, -30.0, 150.0)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if isinstance(a, unreal.PlayerStart):
            base = a.get_actor_location()
            L("PlayerStart @ " + str(base))
            break

    gen = get_gen(bp)
    offsets = [(250.0, 80.0, 0.0), (420.0, -120.0, 0.0)]
    rots = [180.0, 120.0]

    if gen:
        for i, (ox, oy, oz) in enumerate(offsets):
            loc = unreal.Vector(base.x + ox, base.y + oy, max(float(base.z), 150.0) + oz)
            rot = unreal.Rotator(0.0, rots[i], 0.0)
            act = None
            try:
                sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                act = sub.spawn_actor_from_class(gen, loc, rot)
            except Exception:
                act = unreal.EditorLevelLibrary.spawn_actor_from_class(gen, loc, rot)
            if not act:
                W("spawn BP fail %d" % (i + 1))
                continue
            try:
                act.set_actor_label("Preview_Skeleton_%d" % (i + 1))
            except Exception:
                pass
            L("placed BP Preview_Skeleton_%d @ %s" % (i + 1, loc))
    else:
        W("fallback SkeletalMeshActor")
        for i, (ox, oy, oz) in enumerate(offsets):
            loc = unreal.Vector(base.x + ox, base.y + oy, max(float(base.z), 150.0) + oz)
            act = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.SkeletalMeshActor, loc, unreal.Rotator(0.0, rots[i], 0.0)
            )
            if not act:
                continue
            act.set_actor_label("Preview_Skeleton_%d" % (i + 1))
            try:
                comp = act.skeletal_mesh_component
                if sk:
                    try:
                        comp.set_editor_property("skeletal_mesh", sk)
                    except Exception:
                        comp.set_skeletal_mesh(sk)
                try:
                    comp.set_editor_property("relative_scale3d", unreal.Vector(0.85, 0.85, 0.85))
                except Exception:
                    pass
                if idle:
                    try:
                        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
                        comp.override_animation_data(idle, True, True, 0.0, 1.0)
                    except Exception as e:
                        W("sma anim: " + str(e))
            except Exception as e:
                W("sma: " + str(e))
            L("placed SMA Preview_Skeleton_%d @ %s" % (i + 1, loc))

    try:
        unreal.EditorLevelLibrary.save_current_level()
        L("dungeon saved")
    except Exception as e:
        W("save level: " + str(e))

    try:
        if prev and "Map_Hub" in prev:
            unreal.EditorLoadingAndSavingUtils.load_map(HUB)
            L("hub restored")
    except Exception as e:
        W("restore: " + str(e))


def main():
    open(LOG, "w", encoding="utf-8").write("=== clean skeleton place ===\n")
    L("fbx_exists=" + str(os.path.isfile(FBX)))
    skel = unreal.EditorAssetLibrary.load_asset(SKEL_PATH)
    if not skel:
        # discover skeleton asset next to mesh
        for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, False, False):
            a = unreal.EditorAssetLibrary.load_asset(p)
            if isinstance(a, unreal.Skeleton):
                skel = a
                L("found skeleton " + p)
                break
    L("skel=" + str(skel))

    delete_anim_sequences()
    sk = reimport_clean(skel)
    mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    if sk and mat:
        for i in range(16):
            try:
                sk.set_material(i, mat)
            except Exception:
                break
        save(sk)

    anims = list_anims()
    idle, idle_n = pick_idle(anims)
    L("idle=" + str(idle_n))
    bp = ensure_bp(sk, idle, mat)
    place(bp, sk, idle)
    try:
        unreal.EditorAssetLibrary.save_directory(DEST, True, True)
    except Exception:
        pass
    L("DONE")


main()
