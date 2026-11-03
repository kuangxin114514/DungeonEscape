# -*- coding: utf-8 -*-
"""Import KayKit Knight + replace Hub playable pawn (UE4.27)."""
import unreal
import os

FBX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\Knight.fbx"
TEX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\knight_texture.png"
DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
DEST_ANIM = DEST + "/Animations"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Materials"
DEST_BP = DEST
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"

SK_NAME = "SK_KayKitKnight"
SKEL_NAME = "SKEL_KayKitKnight"
TEX_NAME = "T_KayKitKnight"
MAT_NAME = "M_KayKitKnight"
BP_NAME = "BP_KayKitKnight"
ABP_NAME = "ABP_KayKitKnight"

IDLE_KEYS = ("Idle", "Idle_Rig")
WALK_KEYS = ("Walking_A", "Walking_A_Rig", "Walking_B", "Walking_B_Rig")
RUN_KEYS = ("Running_A", "Running_A_Rig", "Running_B", "Running_B_Rig")


def log(msg):
    unreal.log("PLAYER: " + str(msg))


def warn(msg):
    unreal.log_warning("PLAYER: " + str(msg))


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def save(asset):
    if asset:
        unreal.EditorAssetLibrary.save_loaded_asset(asset)


def find_pins(node):
    try:
        return list(node.pins)
    except Exception:
        try:
            return list(node.get_editor_property("pins"))
        except Exception:
            return []


def pin_named(node, *names):
    pins = find_pins(node)
    lower = [n.lower() for n in names]
    for p in pins:
        try:
            n = str(p.get_editor_property("pin_name")).lower()
        except Exception:
            n = ""
        for t in lower:
            if t == n or t in n:
                return p
    return None


def pin_exec_out(node):
    for prefer in ("then", "execute", ""):
        for p in find_pins(node):
            try:
                d = p.get_editor_property("direction")
                n = str(p.get_editor_property("pin_name"))
                if d == unreal.EdGraphPinDirection.EGPD_OUTPUT and (n == prefer or (prefer == "" and n in ("then", ""))):
                    return p
            except Exception:
                continue
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                return p
        except Exception:
            continue
    return None


def pin_exec_in(node):
    for p in find_pins(node):
        try:
            d = p.get_editor_property("direction")
            n = str(p.get_editor_property("pin_name"))
            if d == unreal.EdGraphPinDirection.EGPD_INPUT and n in ("execute", ""):
                return p
        except Exception:
            continue
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_INPUT:
                return p
        except Exception:
            continue
    return None


def try_link(a, b):
    if not a or not b:
        return False
    try:
        a.make_link_to(b)
        return True
    except Exception:
        try:
            unreal.EdGraphSchema_K2().try_create_connection(a, b)
            return True
        except Exception as e:
            warn("link fail: " + str(e))
            return False


def set_call_func(node, owner_cls, func_name):
    try:
        mr = node.get_editor_property("function_reference")
        mr.set_editor_property("member_name", func_name)
        mr.set_editor_property("member_parent", owner_cls)
        node.set_editor_property("function_reference", mr)
        return True
    except Exception as e:
        warn("set_call_func %s: %s" % (func_name, e))
        return False


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
    log("texture=" + str(tex))
    return tex


def make_material(tex):
    ensure_dir(DEST_MAT)
    full = DEST_MAT + "/" + MAT_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(MAT_NAME, DEST_MAT, unreal.Material, factory)
    if not mat:
        warn("material create failed")
        return None
    try:
        # UE4.27 MaterialEditingLibrary
        ts = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -350, 0)
        if tex and ts:
            ts.set_editor_property("texture", tex)
            unreal.MaterialEditingLibrary.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        # Slightly toon-friendly: low roughness
        const_r = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 200)
        if const_r:
            const_r.set_editor_property("r", 0.85)
            unreal.MaterialEditingLibrary.connect_material_property(const_r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    except Exception as e:
        warn("material wire: " + str(e))
    save(mat)
    log("material=" + full)
    return unreal.EditorAssetLibrary.load_asset(full)


def import_knight_fbx():
    ensure_dir(DEST_MESH)
    ensure_dir(DEST_ANIM)
    # wipe previous
    for folder in (DEST_MESH, DEST_ANIM):
        try:
            assets = unreal.EditorAssetLibrary.list_assets(folder, True, False)
            for a in assets:
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
        warn("sk_data: " + str(e))

    anim_data = options.get_editor_property("anim_sequence_import_data")
    try:
        anim_data.set_editor_property("import_uniform_scale", 1.0)
        anim_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        anim_data.set_editor_property("convert_scene", True)
    except Exception as e:
        warn("anim_data: " + str(e))

    task.options = options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    if task.result:
        for p in task.result:
            log("imported: " + str(p))

    sk_path = DEST_MESH + "/" + SK_NAME
    sk = unreal.EditorAssetLibrary.load_asset(sk_path)
    if not sk:
        # sometimes named after file
        cands = unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False)
        log("mesh folder assets: " + str(cands))
        for c in cands:
            a = unreal.EditorAssetLibrary.load_asset(c)
            if isinstance(a, unreal.SkeletalMesh):
                sk = a
                sk_path = c
                break
    log("skeletal_mesh=" + str(sk_path) + " -> " + str(sk))
    return sk


def mesh_height(sk):
    try:
        bb = sk.get_bounding_box()
        return abs(bb.max.z - bb.min.z), bb
    except Exception as e:
        warn("bbox: " + str(e))
        return 0.0, None


def apply_material(sk, mat):
    if not sk or not mat:
        return
    try:
        mats = sk.get_editor_property("materials")
        # materials is array of SkeletalMaterial
        new_list = []
        count = 0
        try:
            count = len(mats)
        except Exception:
            count = sk.get_num_sections(0) if hasattr(sk, "get_num_sections") else 8
        # Use EditorAssetLibrary / SkeletalMesh API
        for i in range(max(count, 1)):
            try:
                unreal.SkeletalMeshEditorLibrary.set_material_slot(sk, i, mat)  # may not exist
            except Exception:
                pass
        # Fallback: set materials property
        try:
            slots = sk.materials
            for i, slot in enumerate(list(slots)):
                try:
                    slot.set_editor_property("material_interface", mat)
                except Exception:
                    try:
                        slot.material_interface = mat
                    except Exception:
                        pass
            sk.set_editor_property("materials", slots)
        except Exception as e:
            warn("apply mat slots: " + str(e))
        # Another fallback used often:
        try:
            for i in range(16):
                sk.set_material(i, mat)
        except Exception:
            pass
        save(sk)
        log("materials applied")
    except Exception as e:
        warn("apply_material: " + str(e))


def list_anims():
    """Return dict name->asset for anim sequences under KayKit folders."""
    found = {}
    for folder in (DEST_MESH, DEST_ANIM, DEST):
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            continue
        for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                found[a.get_name()] = a
                found[path] = a
    log("anim_count=" + str(len([k for k in found.keys() if not str(k).startswith("/")])))
    return found


def pick_anim(anims, keys):
    names = [k for k in anims.keys() if not str(k).startswith("/")]
    for key in keys:
        for n in names:
            if n == key or n.endswith("_" + key) or key in n:
                return anims[n]
    # fuzzy
    for key in keys:
        kl = key.lower().replace("_rig", "")
        for n in names:
            if kl in n.lower():
                return anims[n]
    return None


def create_anim_bp(skeleton):
    ensure_dir(DEST)
    full = DEST + "/" + ABP_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.AnimBlueprintFactory()
    try:
        factory.set_editor_property("TargetSkeleton", skeleton)
        factory.set_editor_property("ParentClass", unreal.AnimInstance)
    except Exception as e:
        warn("abp factory props: " + str(e))
    abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(ABP_NAME, DEST, unreal.AnimBlueprint, factory)
    if not abp:
        abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(ABP_NAME, DEST, None, factory)
    save(abp)
    log("AnimBP shell=" + full + " -> " + str(abp))
    return unreal.EditorAssetLibrary.load_asset(full)


def duplicate_character_bp():
    ensure_dir(DEST_BP)
    full = DEST_BP + "/" + BP_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    if unreal.EditorAssetLibrary.does_asset_exist(TP_CHAR):
        unreal.EditorAssetLibrary.duplicate_asset(BP_NAME, DEST_BP, TP_CHAR)
        log("duplicated ThirdPersonCharacter -> " + full)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", unreal.Character)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, DEST_BP, None, factory)
        save(bp)
        warn("ThirdPersonCharacter missing; created bare Character BP")
    return unreal.EditorAssetLibrary.load_asset(full)


def configure_character(bp, sk, idle_anim, walk_anim, run_anim, abp=None):
    if not bp:
        return False
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
        warn("no generated_class")
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
        warn("no mesh component on CDO")
        return False

    # Scale already baked; actor scale 1
    try:
        mesh.set_editor_property("skeletal_mesh", sk)
    except Exception:
        try:
            mesh.set_skeletal_mesh(sk)
        except Exception as e:
            warn("set skeletal_mesh: " + str(e))

    # Animation: prefer AnimBP if present; else Single Node + Tick switch
    use_abp = False
    if abp:
        try:
            abp_class = abp.generated_class()
            mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.set_editor_property("anim_class", abp_class)
            use_abp = True
            log("mesh AnimClass=" + str(abp_class))
        except Exception as e:
            warn("set abp: " + str(e))
            use_abp = False

    if not use_abp:
        try:
            mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        except Exception:
            pass
        # Set default animation asset on mesh (Idle)
        if idle_anim:
            try:
                mesh.set_editor_property("animation_data", None)
            except Exception:
                pass
            try:
                # UE4: OverrideAnimationData / SetAnimation
                mesh.override_animation_data(idle_anim, True, True, 0.0, 1.0)
            except Exception:
                try:
                    ad = mesh.get_editor_property("animation_data")
                    ad.set_editor_property("anim_to_play", idle_anim)
                    ad.set_editor_property("saved_looping", True)
                    ad.set_editor_property("saved_playing", True)
                    mesh.set_editor_property("animation_data", ad)
                except Exception as e:
                    warn("set idle anim data: " + str(e))

    # Relative transform: UE character mesh usually yaw -90
    try:
        mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
    except Exception:
        try:
            mesh.set_relative_rotation(unreal.Rotator(0.0, -90.0, 0.0))
        except Exception as e:
            warn("mesh rot: " + str(e))

    # Feet on ground: capsule half-height ~88, mesh Z often -90
    h, bb = mesh_height(sk)
    log("mesh_height_z=" + str(h))
    half = 88.0
    radius = 34.0
    if h > 50:
        half = max(40.0, h * 0.48)
        radius = max(20.0, h * 0.18)
    try:
        cap = cdo.get_editor_property("capsule_component")
        if cap:
            cap.set_editor_property("capsule_half_height", half)
            cap.set_editor_property("capsule_radius", min(radius, half - 5.0))
            log("capsule half=%.1f radius=%.1f" % (half, min(radius, half - 5.0)))
    except Exception as e:
        warn("capsule: " + str(e))

    # Mesh relative Z so feet near capsule bottom
    try:
        z_off = -half
        if bb is not None:
            # if mesh pivot at feet, z_off = -half; if at center, different
            z_off = -half - float(bb.min.z) * 0.0
            # KayKit/Blender export usually pivot at feet after scale
            z_off = -half
        mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, z_off))
    except Exception as e:
        warn("mesh loc: " + str(e))

    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass

    # Wire tick-based anim switch if not using working AnimBP graph
    if not use_abp:
        wire_locomotion_tick(bp, idle_anim, walk_anim, run_anim)
    else:
        # Still wire tick as fallback if AnimBP has empty graph (most likely)
        # Detect empty: always wire tick AND set mode to single node for reliability
        log("AnimBP present but graph likely empty; wiring SingleNode tick locomotion")
        try:
            mesh2 = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh")
            mesh2.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            mesh2.set_editor_property("anim_class", None)
        except Exception:
            pass
        wire_locomotion_tick(bp, idle_anim, walk_anim, run_anim)

    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception as e:
        warn("compile: " + str(e))
    return True


def add_bool_member(bp, name):
    """Try to add a bool member variable on the Blueprint."""
    try:
        pin = unreal.EdGraphPinType()
        pin.set_editor_property("pin_category", "bool")
        try:
            pin.set_editor_property("pin_sub_category", "None")
        except Exception:
            pass
        ok = unreal.BlueprintEditorLibrary.add_member_variable(bp, name, pin)
        log("add_member_variable %s -> %s" % (name, ok))
        return True
    except Exception as e:
        warn("add_bool_member: " + str(e))
    # Fallback: NewBlueprintVariable via AssetEditor? skip
    return False


def wire_locomotion_tick(bp, idle_anim, walk_anim, run_anim):
    """BeginPlay: play idle. Tick: only switch anim when move-state changes."""
    if not idle_anim and not walk_anim:
        warn("no anims to wire")
        return False
    walk_to_use = walk_anim or run_anim or idle_anim
    idle_to_use = idle_anim or walk_anim
    add_bool_member(bp, "KayKit_bMoving")
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass
    try:
        pages = list(bp.ubergraph_pages)
        if not pages:
            warn("no ubergraph")
            return False
        graph = pages[0]

        # ---- BeginPlay -> Play Idle ----
        begin = unreal.new_object(unreal.K2Node_Event, graph)
        try:
            ref = begin.get_editor_property("event_reference")
            ref.set_editor_property("member_name", "ReceiveBeginPlay")
            begin.set_editor_property("event_reference", ref)
        except Exception:
            pass
        begin.node_pos_x = -800
        begin.node_pos_y = 900
        graph.add_node(begin, False, False)

        get_mesh_bp = unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr = get_mesh_bp.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", "Mesh")
            get_mesh_bp.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        get_mesh_bp.node_pos_x = -500
        get_mesh_bp.node_pos_y = 1000
        graph.add_node(get_mesh_bp, False, False)

        play_idle0 = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(play_idle0, unreal.SkeletalMeshComponent.static_class(), "PlayAnimation")
        play_idle0.node_pos_x = -200
        play_idle0.node_pos_y = 900
        graph.add_node(play_idle0, False, False)

        try_link(pin_exec_out(begin), pin_exec_in(play_idle0))
        try_link(pin_named(get_mesh_bp, "Mesh", "ReturnValue"), pin_named(play_idle0, "self", "Target"))
        ap = pin_named(play_idle0, "NewAnimToPlay", "AnimToPlay", "New Anim To Play")
        if ap and idle_to_use:
            try:
                ap.set_editor_property("default_object", idle_to_use)
            except Exception:
                pass
        lp = pin_named(play_idle0, "bLooping", "Looping")
        if lp:
            try:
                lp.set_editor_property("default_value", "true")
            except Exception:
                pass

        # ---- Tick locomotion with state ----
        tick = unreal.new_object(unreal.K2Node_Event, graph)
        try:
            ref = tick.get_editor_property("event_reference")
            ref.set_editor_property("member_name", "ReceiveTick")
            tick.set_editor_property("event_reference", ref)
        except Exception:
            pass
        tick.node_pos_x = -800
        tick.node_pos_y = 1300
        graph.add_node(tick, False, False)

        get_vel = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(get_vel, unreal.Actor.static_class(), "GetVelocity")
        get_vel.node_pos_x = -550
        get_vel.node_pos_y = 1550
        graph.add_node(get_vel, False, False)

        vsize = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(vsize, unreal.KismetMathLibrary.static_class(), "VSize")
        vsize.node_pos_x = -300
        vsize.node_pos_y = 1550
        graph.add_node(vsize, False, False)

        gt = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(gt, unreal.KismetMathLibrary.static_class(), "Greater_FloatFloat")
        gt.node_pos_x = -80
        gt.node_pos_y = 1550
        graph.add_node(gt, False, False)
        bpin = pin_named(gt, "B")
        if bpin:
            try:
                bpin.set_editor_property("default_value", "20.0")
            except Exception:
                pass

        branch_spd = unreal.new_object(unreal.K2Node_IfThenElse, graph)
        branch_spd.node_pos_x = 150
        branch_spd.node_pos_y = 1300
        graph.add_node(branch_spd, False, False)

        # get KayKit_bMoving
        get_moving = unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr = get_moving.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", "KayKit_bMoving")
            get_moving.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        get_moving.node_pos_x = 150
        get_moving.node_pos_y = 1600
        graph.add_node(get_moving, False, False)

        # when speed high: if NOT already moving -> play walk, set true
        branch_not_moving = unreal.new_object(unreal.K2Node_IfThenElse, graph)
        branch_not_moving.node_pos_x = 420
        branch_not_moving.node_pos_y = 1180
        graph.add_node(branch_not_moving, False, False)

        not_node = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(not_node, unreal.KismetMathLibrary.static_class(), "Not_PreBool")
        not_node.node_pos_x = 280
        not_node.node_pos_y = 1500
        graph.add_node(not_node, False, False)

        # when speed low: if already moving -> play idle, set false
        branch_is_moving = unreal.new_object(unreal.K2Node_IfThenElse, graph)
        branch_is_moving.node_pos_x = 420
        branch_is_moving.node_pos_y = 1550
        graph.add_node(branch_is_moving, False, False)

        get_mesh = unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr = get_mesh.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", "Mesh")
            get_mesh.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        get_mesh.node_pos_x = 420
        get_mesh.node_pos_y = 1800
        graph.add_node(get_mesh, False, False)

        play_walk = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(play_walk, unreal.SkeletalMeshComponent.static_class(), "PlayAnimation")
        play_walk.node_pos_x = 720
        play_walk.node_pos_y = 1100
        graph.add_node(play_walk, False, False)

        play_idle = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(play_idle, unreal.SkeletalMeshComponent.static_class(), "PlayAnimation")
        play_idle.node_pos_x = 720
        play_idle.node_pos_y = 1500
        graph.add_node(play_idle, False, False)

        set_moving_true = unreal.new_object(unreal.K2Node_VariableSet, graph)
        try:
            vr = set_moving_true.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", "KayKit_bMoving")
            set_moving_true.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        set_moving_true.node_pos_x = 1000
        set_moving_true.node_pos_y = 1100
        graph.add_node(set_moving_true, False, False)

        set_moving_false = unreal.new_object(unreal.K2Node_VariableSet, graph)
        try:
            vr = set_moving_false.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", "KayKit_bMoving")
            set_moving_false.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        set_moving_false.node_pos_x = 1000
        set_moving_false.node_pos_y = 1500
        graph.add_node(set_moving_false, False, False)

        # data links
        try_link(pin_named(get_vel, "ReturnValue", "Return Value"), pin_named(vsize, "A"))
        try_link(pin_named(vsize, "ReturnValue", "Return Value"), pin_named(gt, "A"))
        try_link(pin_named(gt, "ReturnValue", "Return Value"), pin_named(branch_spd, "Condition"))
        try_link(pin_named(get_moving, "KayKit_bMoving", "ReturnValue"), pin_named(not_node, "A"))
        try_link(pin_named(not_node, "ReturnValue", "Return Value"), pin_named(branch_not_moving, "Condition"))
        try_link(pin_named(get_moving, "KayKit_bMoving", "ReturnValue"), pin_named(branch_is_moving, "Condition"))

        mesh_out = pin_named(get_mesh, "Mesh", "ReturnValue")
        try_link(mesh_out, pin_named(play_walk, "self", "Target"))
        try_link(mesh_out, pin_named(play_idle, "self", "Target"))

        for node, anim in ((play_walk, walk_to_use), (play_idle, idle_to_use)):
            apin = pin_named(node, "NewAnimToPlay", "AnimToPlay", "New Anim To Play")
            if apin and anim:
                try:
                    apin.set_editor_property("default_object", anim)
                except Exception:
                    pass
            lpin = pin_named(node, "bLooping", "Looping")
            if lpin:
                try:
                    lpin.set_editor_property("default_value", "true")
                except Exception:
                    pass

        # set bool defaults on set nodes
        tpin = pin_named(set_moving_true, "KayKit_bMoving")
        if tpin:
            try:
                tpin.set_editor_property("default_value", "true")
            except Exception:
                pass
        fpin = pin_named(set_moving_false, "KayKit_bMoving")
        if fpin:
            try:
                fpin.set_editor_property("default_value", "false")
            except Exception:
                pass

        # exec links
        try_link(pin_exec_out(tick), pin_exec_in(branch_spd))
        try_link(pin_named(branch_spd, "then", "True"), pin_exec_in(branch_not_moving))
        try_link(pin_named(branch_spd, "else", "False"), pin_exec_in(branch_is_moving))
        try_link(pin_named(branch_not_moving, "then", "True"), pin_exec_in(play_walk))
        try_link(pin_exec_out(play_walk), pin_exec_in(set_moving_true))
        try_link(pin_named(branch_is_moving, "then", "True"), pin_exec_in(play_idle))
        try_link(pin_exec_out(play_idle), pin_exec_in(set_moving_false))

        save(bp)
        log("wired BeginPlay+Tick state locomotion")
        return True
    except Exception as e:
        warn("wire_locomotion_tick: " + str(e))
        return False

def set_default_pawn(gm_path, pawn_bp):
    if not unreal.EditorAssetLibrary.does_asset_exist(gm_path):
        warn("missing GM " + gm_path)
        return False
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    except Exception:
        pass
    try:
        gen = gm.generated_class()
        cdo = unreal.get_default_object(gen)
        pawn_class = pawn_bp.generated_class()
        cdo.set_editor_property("default_pawn_class", pawn_class)
        save(gm)
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(gm)
        except Exception:
            pass
        log("DefaultPawnClass on %s = %s" % (gm_path, pawn_class))
        return True
    except Exception as e:
        warn("set_default_pawn %s: %s" % (gm_path, e))
        return False


def fix_hub_level(pawn_bp):
    if not unreal.EditorAssetLibrary.does_asset_exist(HUB_MAP):
        warn("no hub map")
        return
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    removed = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label()
        cls = a.get_class().get_name()
        if "ThirdPersonCharacter" in lab or "ThirdPersonCharacter" in cls or lab.startswith("BP_KayKit"):
            try:
                unreal.EditorLevelLibrary.destroy_actor(a)
                removed += 1
            except Exception:
                pass
    log("removed placed pawns: %d" % removed)

    # Ensure PlayerStart
    starts = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if "PlayerStart" in a.get_class().get_name()]
    if not starts:
        ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 120), unreal.Rotator(0, 0, 0))
        if ps:
            ps.set_actor_label("PlayerStart_Hub")
            log("spawned PlayerStart")
    else:
        log("PlayerStart ok: " + starts[0].get_actor_label())

    # World settings game mode -> ThirdPersonGameMode (has movement defaults) with our pawn
    try:
        ws = None
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if "WorldSettings" in a.get_class().get_name():
                ws = a
                break
        if ws is None:
            try:
                ws = unreal.EditorLevelLibrary.get_game_mode()  # wrong
            except Exception:
                pass
        # Use EditorLevelLibrary API
        world = unreal.EditorLevelLibrary.get_editor_world()
        if world:
            wsettings = world.get_editor_property("world_settings") if hasattr(world, "get_editor_property") else None
            try:
                wsettings = unreal.GameplayStatics.get_world_settings(world)
            except Exception:
                pass
            # Direct from actors
            for a in unreal.EditorLevelLibrary.get_all_level_actors():
                if a.get_class().get_name().startswith("WorldSettings"):
                    tp_gm_cls = unreal.load_class(None, TP_GM + ".ThirdPersonGameMode_C")
                    if tp_gm_cls:
                        try:
                            a.set_editor_property("default_game_mode", tp_gm_cls)
                            log("Hub WorldSettings DefaultGameMode=ThirdPersonGameMode")
                        except Exception as e:
                            warn("set gm on ws: " + str(e))
    except Exception as e:
        warn("worldsettings: " + str(e))

    try:
        unreal.EditorLevelLibrary.save_current_level()
    except Exception:
        pass
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)


def main():
    log("==== BEGIN KayKit player import ====")
    if not os.path.isfile(FBX):
        warn("FBX missing: " + FBX)
        return

    for d in (DEST, DEST_MESH, DEST_ANIM, DEST_TEX, DEST_MAT):
        ensure_dir(d)

    tex = import_texture()
    mat = make_material(tex)
    sk = import_knight_fbx()
    if not sk:
        warn("FAILED: no skeletal mesh")
        return

    h, bb = mesh_height(sk)
    log("BOUNDS height=%.1f bb=%s" % (h, bb))
    if h < 80:
        warn("mesh still tiny (h<80); consider re-export scale")
    elif h > 400:
        warn("mesh huge (h>400)")

    apply_material(sk, mat)

    # skeleton
    skeleton = None
    try:
        skeleton = sk.get_editor_property("skeleton")
    except Exception:
        try:
            skeleton = sk.skeleton
        except Exception:
            pass
    log("skeleton=" + str(skeleton))

    anims = list_anims()
    # Move anims into Animations folder for cleanliness (optional skip)
    idle = pick_anim(anims, IDLE_KEYS)
    walk = pick_anim(anims, WALK_KEYS)
    run = pick_anim(anims, RUN_KEYS)
    log("idle=%s walk=%s run=%s" % (idle, walk, run))

    abp = None
    if skeleton:
        try:
            abp = create_anim_bp(skeleton)
        except Exception as e:
            warn("create abp: " + str(e))

    bp = duplicate_character_bp()
    configure_character(bp, sk, idle, walk, run, abp)

    set_default_pawn(TP_GM, bp)
    set_default_pawn(GM_HUB, bp)
    fix_hub_level(bp)

    # Save all
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    sk_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(sk) if sk else "?"
    abp_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(abp) if abp else "none"
    bp_path = unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(bp) if bp else "?"
    log("PLAYER READY mesh=%s abp=%s bp=%s scale=1.0 (baked 100x in FBX) height=%.1f default_pawn=%s" % (
        sk_path, abp_path, bp_path, h, bp_path))
    log("==== END ====")


main()

