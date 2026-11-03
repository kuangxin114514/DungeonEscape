# -*- coding: utf-8 -*-
import unreal

DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
MAT_PATH = DEST + "/Materials/M_KayKitKnight"
BP_PATH = DEST + "/BP_KayKitKnight"
ABP_PATH = DEST + "/ABP_KayKitKnight"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
# Mesh component scale: imported bounds ~392uu tall; mannequin ~180 → ~0.46
MESH_SCALE = 0.5


def log(m): unreal.log("PLAYER: " + str(m))
def warn(m): unreal.log_warning("PLAYER: " + str(m))
def save(a):
    if a: unreal.EditorAssetLibrary.save_loaded_asset(a)


def gen_class(bp):
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    except Exception as e:
        warn("compile: " + str(e))
    for getter in (
        lambda: bp.get_editor_property("generated_class"),
        lambda: getattr(bp, "generated_class", None),
        lambda: unreal.EditorAssetLibrary.load_blueprint_class(unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(bp) if False else BP_PATH),
    ):
        try:
            g = getter()
            if callable(g):
                g = g()
            if g:
                return g
        except Exception:
            continue
    # load _C class by path
    try:
        return unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    except Exception as e:
        warn("load_class: " + str(e))
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
        warn("set_call %s: %s" % (func_name, e))
        return False


def list_anims():
    found = {}
    # Asset registry filter
    try:
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        assets = ar.get_assets_by_path(DEST_MESH, recursive=True)
        for ad in assets:
            try:
                cname = str(ad.asset_class)
            except Exception:
                cname = str(ad.get_editor_property("asset_class"))
            if "AnimSequence" not in cname:
                continue
            path = "%s/%s" % (str(ad.package_path) if hasattr(ad, "package_path") else DEST_MESH, str(ad.asset_name))
            try:
                path = ad.get_editor_property("object_path")
            except Exception:
                try:
                    path = str(ad.object_path)
                except Exception:
                    path = "/Game/Characters/Player/KayKit/Mesh/" + str(ad.asset_name)
            a = unreal.EditorAssetLibrary.load_asset(str(path).split(".")[0])
            if a:
                found[a.get_name()] = a
    except Exception as e:
        warn("ar: " + str(e))
    # Fallback list_assets
    for path in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if not a:
            continue
        cn = a.get_class().get_name()
        if cn == "AnimSequence":
            found[a.get_name()] = a
    log("anim_count=%d" % len(found))
    if found:
        log("anim_sample=" + ", ".join(list(found.keys())[:5]))
    return found


def pick_idle(anims):
    for n, a in anims.items():
        # exact plain Idle
        if n.endswith("Idle_Rig") and all(x not in n for x in ("Melee", "Unarmed", "Chair", "Floor", "Lie", "2H", "Jump")):
            return a
    for n, a in anims.items():
        if n.endswith("_Idle_Rig") and "Melee" not in n and "Unarmed" not in n:
            return a
    return None


def pick_by_end(anims, ends):
    for end in ends:
        for n, a in anims.items():
            if n.endswith(end):
                return a
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
                pass
        sk.set_editor_property("materials", slots)
        save(sk)
    except Exception as e:
        warn("mat: " + str(e))


def fix_abp_skeleton(sk):
    if not unreal.EditorAssetLibrary.does_asset_exist(ABP_PATH):
        return None
    abp = unreal.EditorAssetLibrary.load_asset(ABP_PATH)
    skeleton = sk.get_editor_property("skeleton")
    try:
        abp.set_editor_property("target_skeleton", skeleton)
    except Exception:
        try:
            # older property name
            abp.set_editor_property("TargetSkeleton", skeleton)
        except Exception as e:
            warn("abp skel prop: " + str(e))
    save(abp)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(abp)
    except Exception as e:
        warn("abp compile: " + str(e))
    return abp


def add_bool(bp, name):
    try:
        pin = unreal.EdGraphPinType()
        pin.set_editor_property("pin_category", "bool")
        ok = unreal.BlueprintEditorLibrary.add_member_variable(bp, name, pin)
        log("add_bool %s -> %s" % (name, ok))
    except Exception as e:
        warn("add_bool: " + str(e))


def configure(bp, sk, idle):
    g = gen_class(bp)
    if not g:
        warn("no gen class")
        return False
    cdo = unreal.get_default_object(g)
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
    # Scale down giant
    try:
        mesh.set_editor_property("relative_scale3d", unreal.Vector(MESH_SCALE, MESH_SCALE, MESH_SCALE))
    except Exception as e:
        warn("scale: " + str(e))
    # Capsule for ~180uu after 0.5 scale on 392 → ~196
    half = 96.0
    radius = 36.0
    try:
        mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
        mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -half))
    except Exception as e:
        warn("xform: " + str(e))
    try:
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", half)
        cap.set_editor_property("capsule_radius", radius)
        log("capsule half=%.1f radius=%.1f mesh_scale=%.2f" % (half, radius, MESH_SCALE))
    except Exception as e:
        warn("capsule: " + str(e))
    if idle:
        try:
            mesh.override_animation_data(idle, True, True, 0.0, 1.0)
            log("default idle set")
        except Exception as e:
            warn("override: " + str(e))
    save(bp)
    gen_class(bp)
    return True


def wire(bp, idle, walk):
    walk_to = walk or idle
    idle_to = idle or walk
    if not idle_to:
        warn("no anims for wire")
        return
    add_bool(bp, "KayKit_bMoving")
    gen_class(bp)
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
        ev.node_pos_x = x; ev.node_pos_y = y
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
        n.node_pos_x = x; n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def add_vset(name, x, y):
        n = unreal.new_object(unreal.K2Node_VariableSet, graph)
        try:
            vr = n.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", name)
            n.set_editor_property("variable_reference", vr)
        except Exception:
            pass
        n.node_pos_x = x; n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def add_call(cls, fname, x, y):
        n = unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call_func(n, cls, fname)
        n.node_pos_x = x; n.node_pos_y = y
        graph.add_node(n, False, False)
        return n

    def set_anim(node, anim):
        ap = pin_named(node, "NewAnimToPlay", "AnimToPlay", "New Anim To Play")
        if ap and anim:
            try: ap.set_editor_property("default_object", anim)
            except Exception: pass
        lp = pin_named(node, "bLooping", "Looping")
        if lp:
            try: lp.set_editor_property("default_value", "true")
            except Exception: pass

    begin = add_event("ReceiveBeginPlay", -800, 2000)
    mesh0 = add_vget("Mesh", -500, 2100)
    play0 = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", -200, 2000)
    try_link(pin_exec_out(begin), pin_exec_in(play0))
    try_link(pin_named(mesh0, "Mesh"), pin_named(play0, "self", "Target"))
    set_anim(play0, idle_to)

    tick = add_event("ReceiveTick", -800, 2400)
    get_vel = add_call(unreal.Actor.static_class(), "GetVelocity", -550, 2650)
    vsize = add_call(unreal.KismetMathLibrary.static_class(), "VSize", -300, 2650)
    gt = add_call(unreal.KismetMathLibrary.static_class(), "Greater_FloatFloat", -80, 2650)
    bp_gt = pin_named(gt, "B")
    if bp_gt:
        try: bp_gt.set_editor_property("default_value", "20.0")
        except Exception: pass

    br = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    br.node_pos_x = 150; br.node_pos_y = 2400
    graph.add_node(br, False, False)

    get_m = add_vget("KayKit_bMoving", 150, 2700)
    notn = add_call(unreal.KismetMathLibrary.static_class(), "Not_PreBool", 300, 2580)
    br_not = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    br_not.node_pos_x = 450; br_not.node_pos_y = 2280
    graph.add_node(br_not, False, False)
    br_is = unreal.new_object(unreal.K2Node_IfThenElse, graph)
    br_is.node_pos_x = 450; br_is.node_pos_y = 2650
    graph.add_node(br_is, False, False)

    mesh = add_vget("Mesh", 450, 2900)
    play_w = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 750, 2200)
    play_i = add_call(unreal.SkeletalMeshComponent.static_class(), "PlayAnimation", 750, 2600)
    set_t = add_vset("KayKit_bMoving", 1050, 2200)
    set_f = add_vset("KayKit_bMoving", 1050, 2600)

    try_link(pin_named(get_vel, "ReturnValue", "Return Value"), pin_named(vsize, "A"))
    try_link(pin_named(vsize, "ReturnValue", "Return Value"), pin_named(gt, "A"))
    try_link(pin_named(gt, "ReturnValue", "Return Value"), pin_named(br, "Condition"))
    try_link(pin_named(get_m, "KayKit_bMoving"), pin_named(notn, "A"))
    try_link(pin_named(notn, "ReturnValue", "Return Value"), pin_named(br_not, "Condition"))
    try_link(pin_named(get_m, "KayKit_bMoving"), pin_named(br_is, "Condition"))
    mout = pin_named(mesh, "Mesh")
    try_link(mout, pin_named(play_w, "self", "Target"))
    try_link(mout, pin_named(play_i, "self", "Target"))
    set_anim(play_w, walk_to)
    set_anim(play_i, idle_to)
    tp = pin_named(set_t, "KayKit_bMoving")
    if tp:
        try: tp.set_editor_property("default_value", "true")
        except Exception: pass
    fp = pin_named(set_f, "KayKit_bMoving")
    if fp:
        try: fp.set_editor_property("default_value", "false")
        except Exception: pass

    try_link(pin_exec_out(tick), pin_exec_in(br))
    try_link(pin_named(br, "then", "True"), pin_exec_in(br_not))
    try_link(pin_named(br, "else", "False"), pin_exec_in(br_is))
    try_link(pin_named(br_not, "then", "True"), pin_exec_in(play_w))
    try_link(pin_exec_out(play_w), pin_exec_in(set_t))
    try_link(pin_named(br_is, "then", "True"), pin_exec_in(play_i))
    try_link(pin_exec_out(play_i), pin_exec_in(set_f))
    save(bp)
    gen_class(bp)
    log("wire done")


def set_pawn(gm_path, pawn_cls):
    if not unreal.EditorAssetLibrary.does_asset_exist(gm_path):
        warn("missing " + gm_path); return
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    except Exception:
        pass
    try:
        g = gm.get_editor_property("generated_class")
        if callable(g): g = g()
        cdo = unreal.get_default_object(g)
        cdo.set_editor_property("default_pawn_class", pawn_cls)
        save(gm)
        unreal.BlueprintEditorLibrary.compile_blueprint(gm)
        log("DefaultPawn %s -> %s" % (gm_path, pawn_cls))
    except Exception as e:
        warn("set_pawn: " + str(e))


def fix_hub():
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    n = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label(); cls = a.get_class().get_name()
        if any(k in lab or k in cls for k in ("ThirdPersonCharacter", "KayKitKnight", "BP_KayKit")):
            try:
                unreal.EditorLevelLibrary.destroy_actor(a); n += 1
            except Exception:
                pass
    log("removed=%d" % n)
    starts = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if "PlayerStart" in a.get_class().get_name()]
    if not starts:
        ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,120), unreal.Rotator(0,0,0))
        if ps: ps.set_actor_label("PlayerStart_Hub")
    tp = unreal.load_class(None, TP_GM + ".ThirdPersonGameMode_C")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name().startswith("WorldSettings") and tp:
            try:
                a.set_editor_property("default_game_mode", tp)
                log("Hub WorldSettings GM set")
            except Exception as e:
                warn(str(e))
    try: unreal.EditorLevelLibrary.save_current_level()
    except Exception: pass


def main():
    log("==== finish2 ====")
    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    apply_material(sk, mat)
    fix_abp_skeleton(sk)

    anims = list_anims()
    idle = pick_idle(anims)
    walk = pick_by_end(anims, ["Walking_A_Rig", "Walking_B_Rig", "Walking_C_Rig"])
    run = pick_by_end(anims, ["Running_A_Rig", "Running_B_Rig"])
    log("idle=%s walk=%s run=%s" % (
        idle.get_name() if idle else None,
        walk.get_name() if walk else None,
        run.get_name() if run else None))

    if not unreal.EditorAssetLibrary.does_asset_exist(BP_PATH):
        # duplicate again
        dst = unreal.EditorAssetLibrary.duplicate_asset(
            "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter", BP_PATH)
        log("dup=" + str(dst))
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    configure(bp, sk, idle)
    wire(bp, idle, walk or run)

    pawn_cls = gen_class(bp)
    if pawn_cls:
        set_pawn(TP_GM, pawn_cls)
        set_pawn(GM_HUB, pawn_cls)
    fix_hub()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("PLAYER READY mesh=%s bp=%s abp=%s mesh_scale=%.2f default_pawn=%s" % (
        SK_PATH, BP_PATH, ABP_PATH, MESH_SCALE, BP_PATH))
    log("==== END ====")


main()
