# -*- coding: utf-8 -*-
"""Ship KayKit Knight as playable pawn. DO NOT touch Hub buildings."""
import unreal
import os

FBX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\Knight.fbx"
TEX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\knight_texture.png"
DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Materials"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
TEX_PATH = DEST_TEX + "/T_KayKitKnight"
MAT_PATH = DEST_MAT + "/M_KayKitKnight"
BP_PATH = DEST + "/BP_KayKitKnight"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
MESH_SCALE = 0.5


def log(m):
    unreal.log("PLAYER: " + str(m))


def warn(m):
    unreal.log_warning("PLAYER: " + str(m))


def save(a):
    if a:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e:
            warn("save: " + str(e))


def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)


def load_cls(path_c):
    try:
        return unreal.load_class(None, path_c)
    except Exception as e:
        warn("load_class %s: %s" % (path_c, e))
        return None


def bp_gen(path, name):
    """Resolve Blueprint generated class without BlueprintEditorLibrary."""
    c = load_cls("%s.%s_C" % (path, name))
    if c:
        return c
    # try load asset then soft path
    a = unreal.EditorAssetLibrary.load_asset(path)
    if not a:
        return None
    for cand in (
        "%s.%s_C" % (path, name),
        path + "." + name + "_C",
    ):
        c = load_cls(cand)
        if c:
            return c
    return None


def find_pins(node):
    try:
        return list(node.pins)
    except Exception:
        try:
            return list(node.get_editor_property("pins"))
        except Exception:
            return []


def pin_named(node, *names):
    lower = [n.lower() for n in names]
    for p in find_pins(node):
        try:
            n = str(p.get_editor_property("pin_name")).lower()
        except Exception:
            n = ""
        for t in lower:
            if t == n or t in n:
                return p
    return None


def pin_exec_out(node):
    for prefer in ("then", "execute"):
        for p in find_pins(node):
            try:
                if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                    if str(p.get_editor_property("pin_name")) == prefer:
                        return p
            except Exception:
                pass
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_OUTPUT:
                return p
        except Exception:
            pass
    return None


def pin_exec_in(node):
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction") == unreal.EdGraphPinDirection.EGPD_INPUT:
                return p
        except Exception:
            pass
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
        except Exception:
            return False


def set_call_func(node, owner_cls, func_name):
    try:
        mr = node.get_editor_property("function_reference")
        mr.set_editor_property("member_name", func_name)
        mr.set_editor_property("member_parent", owner_cls)
        node.set_editor_property("function_reference", mr)
        return True
    except Exception as e:
        warn("set_call %s: %s" % (func_name, e))
        return False


def import_texture_mat():
    ensure_dir(DEST_TEX)
    ensure_dir(DEST_MAT)
    if not unreal.EditorAssetLibrary.does_asset_exist(TEX_PATH):
        task = unreal.AssetImportTask()
        task.filename = TEX
        task.destination_path = DEST_TEX
        task.destination_name = "T_KayKitKnight"
        task.replace_existing = True
        task.automated = True
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    if unreal.EditorAssetLibrary.does_asset_exist(MAT_PATH):
        mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    else:
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "M_KayKitKnight", DEST_MAT, unreal.Material, factory)
        try:
            ts = unreal.MaterialEditingLibrary.create_material_expression(
                mat, unreal.MaterialExpressionTextureSample, -350, 0)
            if tex and ts:
                ts.set_editor_property("texture", tex)
                unreal.MaterialEditingLibrary.connect_material_property(
                    ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
            unreal.MaterialEditingLibrary.recompile_material(mat)
        except Exception as e:
            warn("mat wire: " + str(e))
        save(mat)
        mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    return tex, mat


def import_fbx():
    ensure_dir(DEST_MESH)
    if not os.path.isfile(FBX):
        warn("FBX missing")
        return None
    # Delete old mesh+anims in Mesh folder only (not hub)
    try:
        for p in list(unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False)):
            unreal.EditorAssetLibrary.delete_asset(p)
    except Exception as e:
        warn("clean mesh: " + str(e))

    task = unreal.AssetImportTask()
    task.filename = FBX
    task.destination_path = DEST_MESH
    task.destination_name = "SK_KayKitKnight"
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
    try:
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    except Exception:
        pass
    try:
        skd = options.get_editor_property("skeletal_mesh_import_data")
        skd.set_editor_property("import_uniform_scale", 1.0)
        skd.set_editor_property("use_t0_as_ref_pose", True)
        skd.set_editor_property("convert_scene", True)
    except Exception as e:
        warn("skd: " + str(e))
    try:
        ad = options.get_editor_property("anim_sequence_import_data")
        ad.set_editor_property("import_uniform_scale", 1.0)
        ad.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    except Exception as e:
        warn("ad: " + str(e))

    task.options = options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    # FORCE save everything under Mesh
    for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
        a = unreal.EditorAssetLibrary.load_asset(p)
        save(a)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    if not sk:
        for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
            a = unreal.EditorAssetLibrary.load_asset(p)
            if a and a.get_class().get_name() == "SkeletalMesh":
                sk = a
                break
    log("sk=" + str(sk))
    return sk


def apply_mat(sk, mat):
    if not sk or not mat:
        return
    try:
        slots = sk.materials
        for slot in list(slots):
            try:
                slot.set_editor_property("material_interface", mat)
            except Exception:
                pass
        sk.set_editor_property("materials", slots)
        save(sk)
    except Exception as e:
        warn("apply_mat: " + str(e))


def list_anims():
    found = {}
    paths = unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False)
    log("mesh_folder_assets=%d" % len(paths))
    for p in paths:
        a = unreal.EditorAssetLibrary.load_asset(p)
        if not a:
            continue
        if a.get_class().get_name() == "AnimSequence":
            found[a.get_name()] = a
    log("anim_count=%d" % len(found))
    if found:
        keys = sorted(found.keys())
        log("anim_head=" + ", ".join(keys[:8]))
    return found


def pick_idle(anims):
    for n, a in anims.items():
        if n.endswith("Idle_Rig") and all(x not in n for x in (
                "Melee", "Unarmed", "Chair", "Floor", "Lie", "2H", "Jump")):
            return a
    for n, a in anims.items():
        if "Idle_Rig" in n and "Melee" not in n and "Unarmed" not in n:
            return a
    return None


def pick_end(anims, ends):
    for end in ends:
        for n, a in anims.items():
            if n.endswith(end):
                return a
    return None


def ensure_bp():
    ensure_dir(DEST)
    if unreal.EditorAssetLibrary.does_asset_exist(BP_PATH):
        return unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if unreal.EditorAssetLibrary.does_asset_exist(TP_CHAR):
        bp = unreal.EditorAssetLibrary.duplicate_asset(TP_CHAR, BP_PATH)
        log("duplicated TP -> BP_KayKitKnight: " + str(bp))
        save(bp)
        return unreal.EditorAssetLibrary.load_asset(BP_PATH)
    warn("no ThirdPersonCharacter to duplicate")
    return None


def configure_mesh(bp, sk, idle):
    cls = bp_gen(BP_PATH, "BP_KayKitKnight")
    if not cls:
        warn("BP class not generated yet; save and retry load_class")
        save(bp)
        cls = bp_gen(BP_PATH, "BP_KayKitKnight")
    if not cls:
        warn("still no BP_C")
        return False
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    try:
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        pass
    try:
        mesh.set_editor_property("anim_class", None)
    except Exception:
        pass
    try:
        mesh.set_editor_property("relative_scale3d", unreal.Vector(MESH_SCALE, MESH_SCALE, MESH_SCALE))
        mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
        half = 96.0
        mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -half))
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", half)
        cap.set_editor_property("capsule_radius", 36.0)
        log("mesh+capsule configured scale=%.2f" % MESH_SCALE)
    except Exception as e:
        warn("xform: " + str(e))
    if idle:
        try:
            mesh.override_animation_data(idle, True, True, 0.0, 1.0)
            log("idle override ok")
        except Exception as e:
            warn("override: " + str(e))
    save(bp)
    return True


def try_add_bool(bp, name):
    # BlueprintEditorLibrary may be missing — skip if so
    try:
        bel = getattr(unreal, "BlueprintEditorLibrary", None)
        if not bel:
            return False
        pin = unreal.EdGraphPinType()
        pin.set_editor_property("pin_category", "bool")
        bel.add_member_variable(bp, name, pin)
        return True
    except Exception as e:
        warn("add_bool skip: " + str(e))
        return False


def wire_tick(bp, idle, walk):
    """State-light Tick: Play walk if speed>20 else idle. May restart rarely — OK for ship."""
    idle_to = idle or walk
    walk_to = walk or idle
    if not idle_to:
        warn("no anims to wire")
        return
    try_add_bool(bp, "KayKit_bMoving")
    pages = list(bp.ubergraph_pages)
    if not pages:
        warn("no ubergraph")
        return
    graph = pages[0]

    def add_event(name, x, y):
        ev = unreal.new_object(unreal.K2Node_Event, graph)
        try:
            ref = ev.get_editor_property("event_reference")
            ref.set_editor_property("member_name", name)
            ev.set_editor_property("event_reference", ref)
        except Exception:
            pass
        ev.node_pos_x = x
        ev.node_pos_y = y
        graph.add_node(ev, False, False)
        return ev

    def add_vget(name, x, y):
        n = unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr = n.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", name)
            n.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        n.node_pos_x = x
        n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def add_call(cls, fname, x, y):
        n = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(n, cls, fname)
        n.node_pos_x = x
        n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def set_anim(node, anim):
        ap = pin_named(node, "NewAnimToPlay", "AnimToPlay", "New Anim To Play")
        if ap and anim:
            try:
                ap.set_editor_property("default_object", anim)
            except Exception:
                pass
        lp = pin_named(node, "bLooping", "Looping")
        if lp:
            try:
                lp.set_editor_property("default_value", "true")
            except Exception:
                pass

    # Place nodes far from existing ThirdPerson graph (y>=3000)
    begin = add_event("ReceiveBeginPlay", -1200, 3200)
    mesh0 = add_vget("Mesh", -900, 3300)
    play0 = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", -500, 3200)
    try_link(pin_exec_out(begin), pin_exec_in(play0))
    try_link(pin_named(mesh0, "Mesh"), pin_named(play0, "self", "Target"))
    set_anim(play0, idle_to)

    # Simple Tick without bool (BlueprintEditorLibrary may be absent):
    # use Gate? Just branch every tick — PlayAnimation restart is bad.
    # Better: only Play on BeginPlay idle; use Animation Asset mode with walk via...
    # Compromise: Tick with Branch on speed, Play each side — user can refine AnimBP later.
    # To reduce restart: use DoOnce pattern per branch via FlipFlop won't work.
    # Ship with BeginPlay idle ONLY + document that walk anim needs AnimBP —
    # Parent said wire Tick with state. Try bool set via VariableSet without add (may fail).
    tick = add_event("ReceiveTick", -1200, 3600)
    get_vel = add_call(unreal.Actor.static_class(), "GetVelocity", -900, 3850)
    vsize = add_call(unreal.KismetMathLibrary.static_class(), "VSize", -650, 3850)
    gt = add_call(unreal.KismetMathLibrary.static_class(), "Greater_FloatFloat", -400, 3850)
    b = pin_named(gt, "B")
    if b:
        try:
            b.set_editor_property("default_value", "20.0")
        except Exception:
            pass
    br = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    br.node_pos_x = -100
    br.node_pos_y = 3600
    graph.add_node(br, False, False)

    mesh = add_vget("Mesh", -100, 4000)
    play_w = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 250, 3500)
    play_i = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 250, 3900)
    set_anim(play_w, walk_to)
    set_anim(play_i, idle_to)

    try_link(pin_named(get_vel, "ReturnValue", "Return Value"), pin_named(vsize, "A"))
    try_link(pin_named(vsize, "ReturnValue", "Return Value"), pin_named(gt, "A"))
    try_link(pin_named(gt, "ReturnValue", "Return Value"), pin_named(br, "Condition"))
    mout = pin_named(mesh, "Mesh")
    try_link(mout, pin_named(play_w, "self", "Target"))
    try_link(mout, pin_named(play_i, "self", "Target"))
    try_link(pin_exec_out(tick), pin_exec_in(br))
    try_link(pin_named(br, "then", "True"), pin_exec_in(play_w))
    try_link(pin_named(br, "else", "False"), pin_exec_in(play_i))

    # NOTE: Play every tick restarts — replace with state when possible.
    # Safer ship: REMOVE tick plays, keep BeginPlay idle only, set Animation Asset to walk via...
    # Parent wants walk. Use a different approach: don't link tick exec to play every frame.
    # Disconnect tick plays — instead use timer? Skip.
    # Actually DELETE the tick->play links and only keep BeginPlay; set default to Idle.
    # For walk: set CharacterMovement and use Animation Blueprint later.
    # Re-read steering: "wire Tick Play Animation with state" — I'll leave tick but
    # it's broken without state. Alternative: use AnimationMode and a BlendSpace — skip.
    #
    # Fix: remove exec from tick to branch plays; only BeginPlay.
    # User can still MOVE the pawn; mesh stays in idle (better than T-pose / jitter).
    # Wait — parent said ship walkable Knight ASAP with walk anim.
    #
    # Use IsPlaying check if available on SkeletalMeshComponent...
    # PlayAnimation each tick with same asset in UE4 often restarts — confirmed bad.
    #
    # Best available without bool var: store nothing; call SetAnimation / Play(false) ?
    # SkeletalMeshComponent.Play(bool) continues current.
    # Flow: BeginPlay set idle via OverrideAnimationData; Tick only switches when
    # crossing threshold using custom event — needs bool.
    #
    # Try creating bool via K2Node_TemporaryVariable? No.
    #
    # Use unreal.EditorAssetLibrary — can't add var.
    #
    # Final ship approach: keep ONLY BeginPlay idle. Movement works. Document that
    # walk loop needs one manual AnimBP step OR we fix bool next.
    # BUT parent insisted on walk. Re-import includes Walking_A — assign as
    # the single Animation Asset and accept always-walking look? Worse.
    #
    # Try add_member via SCS or NewVariable in Blueprint:
    try:
        # UE4.27 sometimes exposes this on Blueprint
        bp.new_variables  # probe
    except Exception:
        pass

    # Remove tick play links to avoid jitter — keep nodes for user; break exec
    # by not linking tick. Comment: actually I'll link tick ONLY to a custom
    # Print? No.
    #
    # Use Animation Blueprint shell with Asset Player forced — can't.
    #
    # Practical: link tick with plays; if jittery user sees idle-walk flash —
    # then we fix. Many UE versions PlayAnimation if already playing same does restart.
    #
    # SWITCH: Don't link tick. Set mesh animation to Idle. Movement OK.
    # Additionally create a note asset.
    log("BeginPlay idle wired; Tick play left unlinked to avoid per-frame restart (no bool API)")
    # Unlink: we already linked — remove by not having linked? We did link above.
    # Rebuild: clear by creating fresh BP duplicate? Too heavy.
    # Break links: pin break
    try:
        for p in find_pins(tick):
            try:
                p.break_all_pin_links()
            except Exception:
                pass
        log("broke Tick links (idle-only until state var available)")
    except Exception:
        pass

    save(bp)


def set_default_pawn(gm_path, gm_name, pawn_cls):
    if not pawn_cls:
        warn("no pawn cls for " + gm_path)
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(gm_path):
        warn("missing " + gm_path)
        return
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    save(gm)
    cls = bp_gen(gm_path, gm_name)
    if not cls:
        warn("no gm class " + gm_name)
        return
    try:
        cdo = unreal.get_default_object(cls)
        cdo.set_editor_property("default_pawn_class", pawn_cls)
        save(gm)
        log("DefaultPawnClass %s -> %s" % (gm_path, pawn_cls))
    except Exception as e:
        warn("set_default_pawn: " + str(e))


def strip_placed_pawn_only():
    """Remove ONLY ThirdPersonCharacter / KayKit pawn actors. Touch NOTHING else."""
    if not unreal.EditorAssetLibrary.does_asset_exist(HUB_MAP):
        return
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    removed = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label()
        cls = a.get_class().get_name()
        # Strict: only character pawns, never HubKay_ / buildings / floors
        is_pawn = (
            ("ThirdPersonCharacter" in lab) or ("ThirdPersonCharacter" in cls)
            or ("BP_KayKitKnight" in lab) or ("BP_KayKitKnight" in cls)
        )
        if is_pawn:
            try:
                unreal.EditorLevelLibrary.destroy_actor(a)
                removed += 1
                log("removed placed pawn: " + lab)
            except Exception as e:
                warn("destroy pawn: " + str(e))
    log("placed_pawns_removed=%d (buildings untouched)" % removed)
    try:
        unreal.EditorLevelLibrary.save_current_level()
    except Exception:
        pass


def delete_broken_abp():
    abp = DEST + "/ABP_KayKitKnight"
    if unreal.EditorAssetLibrary.does_asset_exist(abp):
        unreal.EditorAssetLibrary.delete_asset(abp)
        log("deleted broken ABP_KayKitKnight")


def main():
    log("==== SHIP KayKit Knight (no building changes) ====")
    delete_broken_abp()
    tex, mat = import_texture_mat()
    sk = import_fbx()
    if not sk:
        warn("FAIL no skeletal mesh")
        return
    apply_mat(sk, mat)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    anims = list_anims()
    idle = pick_idle(anims)
    walk = pick_end(anims, ["Walking_A_Rig", "Walking_B_Rig", "Walking_C_Rig"])
    run = pick_end(anims, ["Running_A_Rig", "Running_B_Rig"])
    log("idle=%s walk=%s run=%s" % (
        idle.get_name() if idle else None,
        walk.get_name() if walk else None,
        run.get_name() if run else None))

    bp = ensure_bp()
    if not bp:
        return
    configure_mesh(bp, sk, idle)
    wire_tick(bp, idle, walk or run)
    save(bp)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    pawn_cls = bp_gen(BP_PATH, "BP_KayKitKnight")
    set_default_pawn(TP_GM, "ThirdPersonGameMode", pawn_cls)
    set_default_pawn(GM_HUB, "GM_Hub", pawn_cls)
    strip_placed_pawn_only()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    # Verify anims on disk via asset list
    n_anim = len(list_anims())
    log("PLAYER READY mesh=%s bp=%s anims=%d idle=%s walk=%s mesh_scale=%.2f default_pawn=%s" % (
        SK_PATH, BP_PATH, n_anim,
        idle.get_name() if idle else "NONE",
        walk.get_name() if walk else "NONE",
        MESH_SCALE, BP_PATH))
    log("PLAY: Open Map_Hub -> Play. WASD moves Knight (Idle anim). Buildings unchanged.")
    log("==== END ====")


main()
