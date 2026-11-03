# -*- coding: utf-8 -*-
"""Finish KayKit player BP wiring (mesh already imported)."""
import unreal

DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
MAT_PATH = DEST + "/Materials/M_KayKitKnight"
TEX_PATH = DEST + "/Textures/T_KayKitKnight"
BP_NAME = "BP_KayKitKnight"
ABP_PATH = DEST + "/ABP_KayKitKnight"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"


def log(m): unreal.log("PLAYER: " + str(m))
def warn(m): unreal.log_warning("PLAYER: " + str(m))


def save(a):
    if a: unreal.EditorAssetLibrary.save_loaded_asset(a)


def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)


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
    for prefer in ("then", "execute", ""):
        for p in find_pins(node):
            try:
                d = p.get_editor_property("direction")
                n = str(p.get_editor_property("pin_name"))
                if d == unreal.EdGraphPinDirection.EGPD_OUTPUT and (n == prefer or prefer == ""):
                    if prefer == "" or n == prefer:
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
            warn("link: " + str(e))
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


def mesh_height(sk):
    # Try several UE4.27 APIs
    for attr in ("get_imported_bounds", "get_bounds", "get_bounding_box"):
        try:
            fn = getattr(sk, attr, None)
            if callable(fn):
                b = fn()
                # BoxSphereBounds has box_extent
                try:
                    ext = b.get_editor_property("box_extent")
                    return abs(ext.z) * 2.0, b
                except Exception:
                    pass
                try:
                    return abs(b.max.z - b.min.z), b
                except Exception:
                    pass
        except Exception:
            continue
    try:
        b = sk.get_editor_property("imported_bounds")
        ext = b.get_editor_property("box_extent")
        return abs(ext.z) * 2.0, b
    except Exception as e:
        warn("height fail: " + str(e))
    return 0.0, None


def list_anims():
    found = {}
    for folder in (DEST_MESH, DEST):
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            continue
        for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                found[a.get_name()] = a
    return found


def pick_exact(anims, prefer_substrings):
    """Prefer names that end with the key; avoid substring false positives like 2H_Melee_Idle."""
    names = list(anims.keys())
    for key in prefer_substrings:
        # exact end match
        for n in names:
            if n.endswith(key) or n == key:
                return anims[n]
        # contains _Key_ or _Key at end after Anim_Rig_
        for n in names:
            if ("_" + key) in n or n.endswith(key):
                # reject if another word before Idle like Melee_Idle when key is Idle_Rig
                if key.startswith("Idle") and ("Melee_Idle" in n or "Unarmed_Idle" in n or "Chair_Idle" in n or "Floor_Idle" in n or "Lie_Idle" in n):
                    continue
                return anims[n]
    return None


def apply_material(sk, mat):
    if not sk or not mat:
        return
    try:
        slots = sk.materials
        for slot in list(slots):
            try:
                slot.set_editor_property("material_interface", mat)
            except Exception:
                try:
                    slot.material_interface = mat
                except Exception:
                    pass
        sk.set_editor_property("materials", slots)
        save(sk)
        log("materials applied count~%d" % len(list(slots)))
    except Exception as e:
        warn("mat: " + str(e))


def duplicate_character_bp():
    ensure_dir(DEST)
    full = DEST + "/" + BP_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    # UE4.27: duplicate_asset(source_asset_path, destination_asset_path)
    src = TP_CHAR
    dst = full
    if unreal.EditorAssetLibrary.does_asset_exist(src):
        try:
            bp = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
            log("duplicated via (src,dst) -> " + str(bp))
            if bp:
                return unreal.EditorAssetLibrary.load_asset(full)
        except Exception as e:
            warn("dup2: " + str(e))
        try:
            # AssetTools duplicate
            at = unreal.AssetToolsHelpers.get_asset_tools()
            data = unreal.AssetDuplicateData()  # may not exist
        except Exception:
            pass
        try:
            at = unreal.AssetToolsHelpers.get_asset_tools()
            assets = [unreal.EditorAssetLibrary.load_asset(src)]
            # duplicate_loaded_asset
            dup = at.duplicate_asset(BP_NAME, DEST, unreal.EditorAssetLibrary.load_asset(src))
            log("duplicate_asset tools -> " + str(dup))
            if dup:
                save(dup)
                return unreal.EditorAssetLibrary.load_asset(full)
        except Exception as e:
            warn("dup tools: " + str(e))
    # Fallback: create Character child (no ThirdPerson input!)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", unreal.Character)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, DEST, None, factory)
    save(bp)
    warn("created bare Character BP (may lack WASD - check ThirdPersonCharacter)")
    return unreal.EditorAssetLibrary.load_asset(full)


def add_bool_member(bp, name):
    try:
        pin = unreal.EdGraphPinType()
        pin.set_editor_property("pin_category", "bool")
        ok = unreal.BlueprintEditorLibrary.add_member_variable(bp, name, pin)
        log("add_member %s -> %s" % (name, ok))
        return True
    except Exception as e:
        warn("add_bool: " + str(e))
        return False


def configure_and_wire(bp, sk, idle, walk, run):
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass
    gen = bp.generated_class()
    cdo = unreal.get_default_object(gen)
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
    if idle:
        try:
            mesh.override_animation_data(idle, True, True, 0.0, 1.0)
        except Exception as e:
            warn("override anim: " + str(e))

    # Rotation & location
    h, bb = mesh_height(sk)
    log("mesh_height=%.2f" % h)
    half = 88.0
    radius = 34.0
    if h > 50:
        half = max(40.0, h * 0.48)
        radius = max(20.0, min(h * 0.18, half - 5))
    else:
        # unknown size: assume human after 100x bake
        half = 90.0
        radius = 35.0
        warn("using default capsule (height unknown)")
    try:
        mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
        mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -half))
    except Exception as e:
        warn("mesh xform: " + str(e))
    try:
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", half)
        cap.set_editor_property("capsule_radius", radius)
        log("capsule half=%.1f radius=%.1f" % (half, radius))
    except Exception as e:
        warn("capsule: " + str(e))

    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass

    add_bool_member(bp, "KayKit_bMoving")
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception:
        pass

    wire_locomotion(bp, idle, walk, run)
    save(bp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception as e:
        warn("compile: " + str(e))


def wire_locomotion(bp, idle_anim, walk_anim, run_anim):
    walk_to_use = walk_anim or run_anim or idle_anim
    idle_to_use = idle_anim or walk_anim
    if not idle_to_use:
        warn("no idle/walk")
        return
    pages = list(bp.ubergraph_pages)
    if not pages:
        warn("no graph")
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

    def add_var_get(varname, x, y):
        n = unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr = n.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", varname)
            n.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        n.node_pos_x = x
        n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def add_var_set(varname, x, y):
        n = unreal.new_object(unreal.K2Node_VariableSet, graph)
        try:
            vr = n.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", varname)
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

    def set_anim_pin(play_node, anim, looping=True):
        ap = pin_named(play_node, "NewAnimToPlay", "AnimToPlay", "New Anim To Play")
        if ap and anim:
            try:
                ap.set_editor_property("default_object", anim)
            except Exception:
                pass
        lp = pin_named(play_node, "bLooping", "Looping")
        if lp and looping:
            try:
                lp.set_editor_property("default_value", "true")
            except Exception:
                pass

    # BeginPlay -> Play Idle
    begin = add_event("ReceiveBeginPlay", -800, 900)
    mesh0 = add_var_get("Mesh", -500, 1000)
    play0 = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", -200, 900)
    try_link(pin_exec_out(begin), pin_exec_in(play0))
    try_link(pin_named(mesh0, "Mesh", "ReturnValue"), pin_named(play0, "self", "Target"))
    set_anim_pin(play0, idle_to_use)

    # Tick
    tick = add_event("ReceiveTick", -800, 1300)
    get_vel = add_call(unreal.Actor.static_class(), "GetVelocity", -550, 1550)
    vsize = add_call(unreal.KismetMathLibrary.static_class(), "VSize", -300, 1550)
    gt = add_call(unreal.KismetMathLibrary.static_class(), "Greater_FloatFloat", -80, 1550)
    bpin = pin_named(gt, "B")
    if bpin:
        try: bpin.set_editor_property("default_value", "20.0")
        except Exception: pass

    branch_spd = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    branch_spd.node_pos_x = 150
    branch_spd.node_pos_y = 1300
    graph.add_node(branch_spd, False, False)

    get_moving = add_var_get("KayKit_bMoving", 150, 1600)
    not_node = add_call(unreal.KismetMathLibrary.static_class(), "Not_PreBool", 280, 1480)

    branch_not = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    branch_not.node_pos_x = 420
    branch_not.node_pos_y = 1180
    graph.add_node(branch_not, False, False)

    branch_is = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    branch_is.node_pos_x = 420
    branch_is.node_pos_y = 1550
    graph.add_node(branch_is, False, False)

    mesh = add_var_get("Mesh", 420, 1800)
    play_walk = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 720, 1100)
    play_idle = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 720, 1500)
    set_true = add_var_set("KayKit_bMoving", 1000, 1100)
    set_false = add_var_set("KayKit_bMoving", 1000, 1500)

    try_link(pin_named(get_vel, "ReturnValue", "Return Value"), pin_named(vsize, "A"))
    try_link(pin_named(vsize, "ReturnValue", "Return Value"), pin_named(gt, "A"))
    try_link(pin_named(gt, "ReturnValue", "Return Value"), pin_named(branch_spd, "Condition"))
    try_link(pin_named(get_moving, "KayKit_bMoving", "ReturnValue"), pin_named(not_node, "A"))
    try_link(pin_named(not_node, "ReturnValue", "Return Value"), pin_named(branch_not, "Condition"))
    try_link(pin_named(get_moving, "KayKit_bMoving", "ReturnValue"), pin_named(branch_is, "Condition"))

    mout = pin_named(mesh, "Mesh", "ReturnValue")
    try_link(mout, pin_named(play_walk, "self", "Target"))
    try_link(mout, pin_named(play_idle, "self", "Target"))
    set_anim_pin(play_walk, walk_to_use)
    set_anim_pin(play_idle, idle_to_use)

    tpin = pin_named(set_true, "KayKit_bMoving")
    if tpin:
        try: tpin.set_editor_property("default_value", "true")
        except Exception: pass
    fpin = pin_named(set_false, "KayKit_bMoving")
    if fpin:
        try: fpin.set_editor_property("default_value", "false")
        except Exception: pass

    try_link(pin_exec_out(tick), pin_exec_in(branch_spd))
    try_link(pin_named(branch_spd, "then", "True"), pin_exec_in(branch_not))
    try_link(pin_named(branch_spd, "else", "False"), pin_exec_in(branch_is))
    try_link(pin_named(branch_not, "then", "True"), pin_exec_in(play_walk))
    try_link(pin_exec_out(play_walk), pin_exec_in(set_true))
    try_link(pin_named(branch_is, "then", "True"), pin_exec_in(play_idle))
    try_link(pin_exec_out(play_idle), pin_exec_in(set_false))

    log("wired locomotion graph")


def set_default_pawn(gm_path, pawn_bp):
    if not unreal.EditorAssetLibrary.does_asset_exist(gm_path):
        warn("no " + gm_path)
        return
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    except Exception:
        pass
    try:
        cdo = unreal.get_default_object(gm.generated_class())
        cdo.set_editor_property("default_pawn_class", pawn_bp.generated_class())
        save(gm)
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
        log("DefaultPawn on %s = %s" % (gm_path, pawn_bp.generated_class()))
    except Exception as e:
        warn("set pawn: " + str(e))


def fix_hub():
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    removed = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label()
        cls = a.get_class().get_name()
        if "ThirdPersonCharacter" in lab or "ThirdPersonCharacter" in cls or "KayKitKnight" in lab or "KayKitKnight" in cls:
            try:
                unreal.EditorLevelLibrary.destroy_actor(a)
                removed += 1
            except Exception:
                pass
    log("removed pawns=%d" % removed)
    starts = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if "PlayerStart" in a.get_class().get_name()]
    if not starts:
        ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 120), unreal.Rotator(0, 0, 0))
        if ps:
            ps.set_actor_label("PlayerStart_Hub")
            log("spawned PlayerStart")
    else:
        log("PlayerStart=" + starts[0].get_actor_label())

    tp_gm_cls = unreal.load_class(None, TP_GM + ".ThirdPersonGameMode_C")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name().startswith("WorldSettings"):
            if tp_gm_cls:
                try:
                    a.set_editor_property("default_game_mode", tp_gm_cls)
                    log("Hub GM=ThirdPersonGameMode")
                except Exception as e:
                    warn("ws gm: " + str(e))
    try:
        unreal.EditorLevelLibrary.save_current_level()
    except Exception:
        pass


def main():
    log("==== FINISH player setup ====")
    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    if not sk:
        warn("missing SK")
        return
    mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    apply_material(sk, mat)
    h, bb = mesh_height(sk)
    log("BOUNDS height=%.2f bb=%s" % (h, bb))

    anims = list_anims()
    log("anims=%d" % len(anims))
    idle = pick_exact(anims, ["Idle_Rig", "_Idle_Rig", "Anim_Rig_Idle_Rig"])
    # Prefer the plain Idle specifically
    for n, a in anims.items():
        if n.endswith("Anim_Rig_Idle_Rig") or n.endswith("_Idle_Rig") and "Melee" not in n and "Unarmed" not in n and "Chair" not in n and "Floor" not in n and "Lie" not in n and "2H" not in n:
            idle = a
            break
    walk = pick_exact(anims, ["Walking_A_Rig", "Walking_A", "Walking_B_Rig"])
    run = pick_exact(anims, ["Running_A_Rig", "Running_A", "Running_B_Rig"])
    log("idle=%s walk=%s run=%s" % (
        idle.get_name() if idle else None,
        walk.get_name() if walk else None,
        run.get_name() if run else None))

    bp = duplicate_character_bp()
    if not bp:
        warn("no bp")
        return
    configure_and_wire(bp, sk, idle, walk, run)
    set_default_pawn(TP_GM, bp)
    set_default_pawn(GM_HUB, bp)
    fix_hub()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    log("PLAYER READY mesh=%s bp=%s abp=%s scale=1.0(baked100) height=%.2f default_pawn=%s" % (
        SK_PATH, DEST + "/" + BP_NAME, ABP_PATH, h, DEST + "/" + BP_NAME))
    log("==== END ====")


main()
