# -*- coding: utf-8 -*-
"""Finish DefaultPawn + optional Tick wire. Never touch Hub buildings."""
import unreal

DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
BP_PATH = DEST + "/BP_KayKitKnight"
TP_GM = "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
MESH_SCALE = 0.5


def log(m): unreal.log("PLAYER: " + str(m))
def warn(m): unreal.log_warning("PLAYER: " + str(m))
def save(a):
    if a:
        try: unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e: warn("save "+str(e))


def load_cls(path_c):
    try:
        return unreal.load_class(None, path_c)
    except Exception as e:
        warn("load_class "+str(e))
        return None


def list_anims():
    found = {}
    for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, True, False):
        a = unreal.EditorAssetLibrary.load_asset(p)
        if a and a.get_class().get_name() == "AnimSequence":
            found[a.get_name()] = a
    log("anim_count=%d" % len(found))
    return found


def pick_idle(anims):
    for n, a in anims.items():
        if n.endswith("Idle_Rig") and all(x not in n for x in ("Melee","Unarmed","Chair","Floor","Lie","2H","Jump")):
            return a
    return None


def pick_end(anims, ends):
    for end in ends:
        for n, a in anims.items():
            if n.endswith(end):
                return a
    return None


def configure_again(sk, idle):
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    cls = load_cls(BP_PATH + ".BP_KayKitKnight_C")
    if not cls:
        warn("no BP_C")
        return bp, None
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
    mesh.set_editor_property("relative_scale3d", unreal.Vector(MESH_SCALE, MESH_SCALE, MESH_SCALE))
    mesh.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
    half = 96.0
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -half))
    try:
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", half)
        cap.set_editor_property("capsule_radius", 36.0)
    except Exception as e:
        warn("cap "+str(e))
    if idle:
        try:
            mesh.override_animation_data(idle, True, True, 0.0, 1.0)
            log("idle set on CDO")
        except Exception as e:
            warn("idle "+str(e))
    save(bp)
    return bp, cls


def get_ubergraph(bp):
    for getter in (
        lambda: bp.get_editor_property("ubergraph_pages"),
        lambda: getattr(bp, "ubergraph_pages", None),
        lambda: bp.get_editor_property("UbergraphPages"),
    ):
        try:
            pages = getter()
            if pages:
                return list(pages)
        except Exception as e:
            warn("ubergraph probe: "+str(e))
    # enumerate properties
    try:
        for p in bp.get_editor_property("skeleton") and []:
            pass
    except Exception:
        pass
    try:
        names = dir(bp)
        log("bp_attrs_sample=" + ", ".join([n for n in names if "graph" in n.lower() or "uber" in n.lower()][:30]))
    except Exception:
        pass
    return []


def find_pins(node):
    try: return list(node.pins)
    except Exception:
        try: return list(node.get_editor_property("pins"))
        except Exception: return []


def pin_named(node, *names):
    lower=[n.lower() for n in names]
    for p in find_pins(node):
        try: n=str(p.get_editor_property("pin_name")).lower()
        except Exception: n=""
        for t in lower:
            if t==n or t in n: return p
    return None


def pin_exec_out(node):
    for prefer in ("then","execute"):
        for p in find_pins(node):
            try:
                if p.get_editor_property("direction")==unreal.EdGraphPinDirection.EGPD_OUTPUT and str(p.get_editor_property("pin_name"))==prefer:
                    return p
            except Exception: pass
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction")==unreal.EdGraphPinDirection.EGPD_OUTPUT:
                return p
        except Exception: pass
    return None


def pin_exec_in(node):
    for p in find_pins(node):
        try:
            if p.get_editor_property("direction")==unreal.EdGraphPinDirection.EGPD_INPUT:
                return p
        except Exception: pass
    return None


def try_link(a,b):
    if not a or not b: return False
    try:
        a.make_link_to(b); return True
    except Exception:
        try:
            unreal.EdGraphSchema_K2().try_create_connection(a,b); return True
        except Exception: return False


def set_call(node, cls, fname):
    try:
        mr=node.get_editor_property("function_reference")
        mr.set_editor_property("member_name", fname)
        mr.set_editor_property("member_parent", cls)
        node.set_editor_property("function_reference", mr)
        return True
    except Exception as e:
        warn("set_call "+str(e)); return False


def wire_beginplay_idle(bp, idle, walk):
    pages = get_ubergraph(bp)
    if not pages:
        warn("no ubergraph — leave Animation Asset Idle on mesh CDO only")
        return False
    graph = pages[0]
    idle_to = idle or walk
    walk_to = walk or idle

    def add_event(name,x,y):
        ev=unreal.new_object(unreal.K2Node_Event, graph)
        try:
            ref=ev.get_editor_property("event_reference")
            ref.set_editor_property("member_name", name)
            ev.set_editor_property("event_reference", ref)
        except Exception: pass
        ev.node_pos_x=x; ev.node_pos_y=y
        graph.add_node(ev, False, False)
        return ev

    def add_vget(name,x,y):
        n=unreal.new_object(unreal.K2Node_VariableGet, graph)
        try:
            vr=n.get_editor_property("variable_reference")
            vr.set_editor_property("member_name", name)
            n.set_editor_property("variable_reference", vr)
        except Exception: pass
        n.node_pos_x=x; n.node_pos_y=y
        graph.add_node(n, False, False)
        return n

    def add_call(cls,fname,x,y):
        n=unreal.new_object(unreal.K2Node_CallFunction, graph)
        set_call(n, cls, fname)
        n.node_pos_x=x; n.node_pos_y=y
        graph.add_node(n, False, False)
        return n

    def set_anim(node, anim):
        ap=pin_named(node,"NewAnimToPlay","AnimToPlay","New Anim To Play")
        if ap and anim:
            try: ap.set_editor_property("default_object", anim)
            except Exception: pass
        lp=pin_named(node,"bLooping","Looping")
        if lp:
            try: lp.set_editor_property("default_value","true")
            except Exception: pass

    # BeginPlay -> Play idle once
    begin=add_event("ReceiveBeginPlay", -1400, 4200)
    mesh0=add_vget("Mesh", -1100, 4300)
    play0=add_call(unreal.SkeletalMeshComponent.static_class(),"PlayAnimation", -700, 4200)
    try_link(pin_exec_out(begin), pin_exec_in(play0))
    try_link(pin_named(mesh0,"Mesh"), pin_named(play0,"self","Target"))
    set_anim(play0, idle_to)

    # Tick with state via temporary: compare current — skip; use speed branch BUT
    # only Play when using a custom latent? 
    # Use Set Timer isn't easy.
    # For walk: Event Tick -> GetVelocity -> VSize -> Branch;
    # True: Play walk; False: Play idle — jitter risk.
    # Mitigation: use PlayAnimation only — in practice UE4 SingleNode PlayAnimation
    # every frame resets. So ONLY beginplay.
    log("wired BeginPlay -> Play Idle")
    save(bp)
    return True


def set_pawn(gm_path, gm_name, pawn_cls):
    if not pawn_cls:
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(gm_path):
        warn("no "+gm_path); return
    gm = unreal.EditorAssetLibrary.load_asset(gm_path)
    save(gm)
    gcls = load_cls("%s.%s_C" % (gm_path, gm_name))
    if not gcls:
        warn("no class "+gm_name); return
    try:
        cdo = unreal.get_default_object(gcls)
        cdo.set_editor_property("default_pawn_class", pawn_cls)
        save(gm)
        # verify
        got = cdo.get_editor_property("default_pawn_class")
        log("DefaultPawn %s -> %s (verify=%s)" % (gm_path, pawn_cls, got))
    except Exception as e:
        warn("set_pawn "+str(e))


def strip_pawn_only():
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    n=0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab=a.get_actor_label(); cls=a.get_class().get_name()
        if ("ThirdPersonCharacter" in lab) or ("ThirdPersonCharacter" in cls) or ("BP_KayKitKnight" in lab) or ("BP_KayKitKnight" in cls):
            try:
                unreal.EditorLevelLibrary.destroy_actor(a); n+=1
                log("removed pawn actor "+lab)
            except Exception as e:
                warn(str(e))
    log("pawns_removed=%d buildings_untouched=1" % n)
    # Ensure PlayerStart exists but do NOT move buildings
    starts=[a for a in unreal.EditorLevelLibrary.get_all_level_actors() if "PlayerStart" in a.get_class().get_name()]
    if not starts:
        ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,120), unreal.Rotator(0,0,0))
        if ps:
            ps.set_actor_label("PlayerStart_Hub")
            log("added PlayerStart only")
    # Set world GM to ThirdPersonGameMode so DefaultPawn applies
    tp = load_cls(TP_GM + ".ThirdPersonGameMode_C")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name().startswith("WorldSettings") and tp:
            try:
                a.set_editor_property("default_game_mode", tp)
                log("Hub WorldSettings -> ThirdPersonGameMode")
            except Exception as e:
                warn("ws "+str(e))
    try: unreal.EditorLevelLibrary.save_current_level()
    except Exception: pass


def main():
    log("==== finish pawn/gm ====")
    sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
    anims = list_anims()
    idle = pick_idle(anims)
    walk = pick_end(anims, ["Walking_A_Rig","Walking_B_Rig"])
    run = pick_end(anims, ["Running_A_Rig","Running_B_Rig"])
    log("idle=%s walk=%s" % (idle.get_name() if idle else None, walk.get_name() if walk else None))

    bp, pawn_cls = configure_again(sk, idle)
    if not pawn_cls:
        pawn_cls = load_cls(BP_PATH + ".BP_KayKitKnight_C")
    wire_beginplay_idle(bp, idle, walk or run)

    set_pawn(TP_GM, "ThirdPersonGameMode", pawn_cls)
    set_pawn(GM_HUB, "GM_Hub", pawn_cls)
    strip_pawn_only()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    # Also try set GlobalDefaultGameMode pawn indirectly via TP_GM already done
    log("PLAYER READY mesh=%s bp=%s anims=%d idle=%s walk=%s scale=%.2f default_pawn=%s" % (
        SK_PATH, BP_PATH, len(anims),
        idle.get_name() if idle else "NONE",
        walk.get_name() if walk else "NONE",
        MESH_SCALE, BP_PATH))
    log("PLAYSTEPS: 1) Editor opens Map_Hub  2) Click Play  3) WASD move Knight (Idle loop). Buildings not modified.")
    log("WALK_NOTE: Idle plays via Animation Asset. For Idle<->Walk auto-switch, open BP_KayKitKnight and add Tick speed branch to PlayAnimation Walking_A (AnimBP optional).")
    log("==== END ====")


main()
