# -*- coding: utf-8 -*-
"""T380: Configure skeleton CharacterMovement, AnimBP (best-effort), NavMesh on dungeon maps.
Does NOT touch Map_Hub buildings. Writes Docs/setup_t380_engine_ai.txt
"""
from __future__ import print_function
import unreal
import traceback

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t380_engine_ai.txt"
BP = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
SKEL = "/Game/Characters/Enemies/Skeleton/Mesh/SK_SkeletonMinion_Skeleton"
MESH = "/Game/Characters/Enemies/Skeleton/Mesh/SK_SkeletonMinion"
ANIM_IDLE = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig"
ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig"
ANIM_ATK = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_1H_Melee_Attack_Chop_Rig"
ABP_DIR = "/Game/Characters/Enemies/Skeleton/Animations"
ABP_NAME = "ABP_SkeletonMinion"
ABP_PATH = ABP_DIR + "/" + ABP_NAME
TP_ABP = "/Game/Mannequin/Animations/ThirdPerson_AnimBP"
MAPS = [
    "/Game/Maps/Dungeon/Map_Dungeon1",
    "/Game/Maps/Dungeon/Map_Dungeon2",
]
lines = []


def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T380SETUP: " + s)
    except Exception:
        print(s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def load(path):
    a = None
    try:
        a = unreal.load_asset(path)
    except Exception:
        a = None
    if a is None:
        try:
            a = unreal.EditorAssetLibrary.load_asset(path)
        except Exception:
            a = None
    return a


def get_bp_class(path):
    cls = None
    try:
        cls = unreal.EditorAssetLibrary.load_blueprint_class(path)
    except Exception:
        cls = None
    if cls is None:
        try:
            cls = unreal.load_object(None, path + "." + path.rsplit("/", 1)[-1] + "_C")
        except Exception:
            cls = None
    return cls


def compile_bp(path):
    bp = load(path)
    if not bp:
        L("compile: missing " + path)
        return None
    try:
        unreal.KismetSystemLibrary.compile_blueprint(bp)  # may not exist
        L("compile via KismetSystemLibrary")
    except Exception as e:
        L("no KismetSystemLibrary.compile_blueprint: " + str(e))
    try:
        aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        aes.open_editor_for_assets([bp])
        unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        aes.close_all_editors_for_asset(bp)
        L("compile via open/save/close")
    except Exception as e:
        L("open/save compile ERR " + str(e))
    return bp


def configure_skeleton_character():
    L("=== configure BP_Enemy_Skeleton ===")
    compile_bp(BP)
    bcls = get_bp_class(BP)
    L("bcls=" + str(bcls))
    if not bcls:
        # force generate
        bp = load(BP)
        try:
            unreal.EditorAssetLibrary.save_asset(BP, only_if_is_dirty=False)
        except Exception:
            pass
        bcls = get_bp_class(BP)
        L("bcls retry=" + str(bcls))
    if not bcls:
        L("FAIL no generated class")
        return False
    cdo = unreal.get_default_object(bcls)
    L("cdo=" + str(cdo))

    # Movement
    mov = None
    try:
        mov = cdo.get_editor_property("character_movement")
    except Exception as e:
        L("character_movement ERR " + str(e))
    if mov:
        for name, val in (
            ("orient_rotation_to_movement", True),
            ("use_controller_desired_rotation", False),
            ("max_walk_speed", 190.0),
            ("max_acceleration", 800.0),
            ("braking_deceleration_walking", 600.0),
        ):
            try:
                mov.set_editor_property(name, val)
                L("mov.%s=%s" % (name, mov.get_editor_property(name)))
            except Exception as e:
                L("mov.%s ERR %s" % (name, e))
        try:
            # high yaw turn rate
            mov.set_editor_property("rotation_rate", unreal.Rotator(0.0, 720.0, 0.0))
            L("mov.rotation_rate set")
        except Exception as e:
            L("rotation_rate ERR " + str(e))

    for name, val in (
        ("use_controller_rotation_yaw", False),
        ("use_controller_rotation_pitch", False),
        ("use_controller_rotation_roll", False),
    ):
        try:
            cdo.set_editor_property(name, val)
            L("%s=%s" % (name, cdo.get_editor_property(name)))
        except Exception as e:
            L("%s ERR %s" % (name, e))

    try:
        cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        L("auto_possess_ai=PLACED_IN_WORLD_OR_SPAWNED")
    except Exception as e:
        L("auto_possess ERR " + str(e))

    try:
        cdo.set_editor_property("ai_controller_class", unreal.AIController.static_class())
        L("ai_controller_class=AIController")
    except Exception as e:
        try:
            cdo.set_editor_property("ai_controller_class", unreal.AIController)
            L("ai_controller_class=AIController (class obj)")
        except Exception as e2:
            L("ai_controller_class ERR " + str(e) + " / " + str(e2))

    # Mesh: keep authored relative yaw (~270); disable physics flip; prefer AnimBP if created
    mesh = None
    try:
        mesh = cdo.get_editor_property("mesh")
    except Exception as e:
        L("mesh ERR " + str(e))
    if mesh:
        try:
            r = mesh.get_editor_property("relative_rotation")
            L("mesh_rel_rot before pitch=%.1f yaw=%.1f roll=%.1f" % (r.pitch, r.yaw, r.roll))
        except Exception:
            pass
        for name, val in (
            ("enable_gravity", False),
            ("collision_enabled", unreal.CollisionEnabled.QUERY_ONLY),
        ):
            try:
                mesh.set_editor_property(name, val)
            except Exception:
                pass
        try:
            mesh.set_simulate_physics(False)
            L("mesh simulate_physics False")
        except Exception as e:
            L("simulate_physics ERR " + str(e))
        # Disable physics bodies if possible
        try:
            mesh.set_editor_property("physics_asset_override", None)
        except Exception:
            pass

    try:
        unreal.EditorAssetLibrary.save_asset(BP, only_if_is_dirty=False)
        L("saved BP")
    except Exception as e:
        L("save BP ERR " + str(e))
    return True


def create_anim_bp():
    L("=== AnimBP ===")
    skel = load(SKEL)
    idle = load(ANIM_IDLE)
    run = load(ANIM_RUN)
    L("skel=%s idle=%s run=%s" % (skel, idle, run))
    if not skel or not idle or not run:
        L("missing anim deps")
        return None

    # Duplicate ThirdPerson AnimBP and retarget sequences + skeleton
    if load(ABP_PATH) is not None:
        L("ABP already exists, will update sequences")
        abp = load(ABP_PATH)
    else:
        abp = None
        if load(TP_ABP):
            try:
                if not unreal.EditorAssetLibrary.does_directory_exist(ABP_DIR):
                    unreal.EditorAssetLibrary.make_directory(ABP_DIR)
            except Exception:
                pass
            try:
                abp = unreal.EditorAssetLibrary.duplicate_asset(TP_ABP, ABP_PATH)
                L("duplicate TP_ABP -> " + str(abp))
            except Exception as e:
                L("duplicate ERR " + str(e))
                try:
                    tools = unreal.AssetToolsHelpers.get_asset_tools()
                    src = load(TP_ABP)
                    abp = tools.duplicate_asset(ABP_NAME, ABP_DIR, src)
                    L("tools.duplicate -> " + str(abp))
                except Exception as e2:
                    L("tools.duplicate ERR " + str(e2))
        if abp is None:
            # Factory create empty AnimBP
            try:
                factory = unreal.AnimBlueprintFactory()
                try:
                    factory.set_editor_property("target_skeleton", skel)
                except Exception:
                    try:
                        factory.set_editor_property("TargetSkeleton", skel)
                    except Exception as e:
                        L("factory skeleton ERR " + str(e))
                tools = unreal.AssetToolsHelpers.get_asset_tools()
                abp = tools.create_asset(ABP_NAME, ABP_DIR, unreal.AnimBlueprint, factory)
                L("create_asset AnimBP -> " + str(abp))
            except Exception as e:
                L("AnimBP factory ERR " + traceback.format_exc())
                return None

    abp = load(ABP_PATH) or abp
    if not abp:
        L("FAIL no ABP")
        return None

    try:
        abp.set_editor_property("target_skeleton", skel)
        L("target_skeleton set")
    except Exception as e:
        L("target_skeleton ERR " + str(e))

    # Replace sequence players with idle/run (best-effort; jump->idle)
    EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
    n_sp = 0
    for obj in unreal.ObjectIterator(EdGraphNode):
        try:
            pn = obj.get_path_name()
        except Exception:
            continue
        if ABP_NAME not in pn:
            continue
        if "Default__" in pn or "AnimPreview" in pn:
            continue
        cn = obj.get_class().get_name()
        try:
            if cn == "AnimGraphNode_SequencePlayer":
                node = obj.get_editor_property("node")
                seq = None
                try:
                    seq = node.get_editor_property("sequence")
                except Exception:
                    seq = None
                name = seq.get_name() if seq else ""
                nl = name.lower()
                new_seq = idle
                if "run" in nl or "walk" in nl or "jog" in nl:
                    new_seq = run
                node.set_editor_property("sequence", new_seq)
                n_sp += 1
                L("SP %s %s -> %s" % (obj.get_name(), name, new_seq.get_name() if new_seq else None))
            elif cn == "AnimGraphNode_BlendSpacePlayer":
                # no skeleton blendspace — leave; speed may be wrong but idle/run seqs matter more
                L("BSP left as-is " + obj.get_name())
        except Exception as e:
            L("node patch ERR " + str(e))
    L("sequence players patched=%d" % n_sp)

    try:
        unreal.EditorAssetLibrary.save_asset(ABP_PATH, only_if_is_dirty=False)
    except Exception as e:
        L("save ABP ERR " + str(e))

    # Assign to character mesh
    abp_cls = get_bp_class(ABP_PATH)
    L("abp_cls=" + str(abp_cls))
    if abp_cls is None:
        try:
            compile_bp(ABP_PATH)
            abp_cls = get_bp_class(ABP_PATH)
            L("abp_cls after compile=" + str(abp_cls))
        except Exception as e:
            L("abp compile ERR " + str(e))

    bcls = get_bp_class(BP)
    if bcls and abp_cls:
        cdo = unreal.get_default_object(bcls)
        mesh = cdo.get_editor_property("mesh")
        try:
            mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.set_editor_property("anim_class", abp_cls)
            L("assigned anim_class to mesh")
        except Exception as e:
            L("assign anim ERR " + str(e))
        try:
            unreal.EditorAssetLibrary.save_asset(BP, only_if_is_dirty=False)
        except Exception as e:
            L("save BP after anim ERR " + str(e))
    else:
        L("skip anim assign bcls=%s abp_cls=%s" % (bcls, abp_cls))
        # Fallback note: runtime AI will play single-node anims
    return abp


def ensure_navmesh_on_map(map_path):
    L("=== NavMesh " + map_path + " ===")
    if not load(map_path) and not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        # registry may still find it
        L("map load soft fail, try open anyway")
    try:
        unreal.EditorLevelLibrary.load_level(map_path)
    except Exception as e:
        L("load_level ERR " + str(e))
        return False

    # Find existing NavMeshBoundsVolume
    existing = []
    try:
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try:
                if isinstance(a, unreal.NavMeshBoundsVolume) or a.get_class().get_name() == "NavMeshBoundsVolume":
                    existing.append(a)
            except Exception:
                pass
    except Exception as e:
        L("list actors ERR " + str(e))
    L("existing NavMeshBoundsVolume=%d" % len(existing))

    vol = existing[0] if existing else None
    if vol is None:
        try:
            vol = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.NavMeshBoundsVolume, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0)
            )
            L("spawned NavMeshBoundsVolume " + str(vol))
        except Exception as e:
            L("spawn nav volume ERR " + traceback.format_exc())
            return False
    if vol:
        try:
            vol.set_actor_label("NavMeshBounds_Dungeon")
        except Exception:
            pass
        # Scale large to cover dungeon
        try:
            # BrushBuilder scale via root component
            root = vol.get_editor_property("root_component")
            if root:
                root.set_editor_property("relative_scale3d", unreal.Vector(50.0, 50.0, 20.0))
                L("nav scale set 50x50x20")
        except Exception as e:
            L("nav scale ERR " + str(e))
        try:
            vol.set_actor_location(unreal.Vector(0.0, 0.0, 100.0), False, False)
        except Exception:
            try:
                vol.set_actor_location(unreal.Vector(0.0, 0.0, 100.0), False)
            except Exception as e:
                L("nav loc ERR " + str(e))

    # Rebuild navigation
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        nav = unreal.NavigationSystemV1.get_navigation_system(world)
        L("navsys=" + str(nav))
        if nav:
            for meth in ("build", "rebuild_all", "simple_build"):
                if hasattr(nav, meth):
                    try:
                        getattr(nav, meth)()
                        L("nav.%s() ok" % meth)
                    except Exception as e:
                        L("nav.%s ERR %s" % (meth, e))
            try:
                unreal.NavigationSystemV1.build(world)
                L("NavigationSystemV1.build(world) ok")
            except Exception as e:
                L("NavigationSystemV1.build ERR " + str(e))
    except Exception as e:
        L("rebuild nav ERR " + traceback.format_exc())

    try:
        unreal.EditorLevelLibrary.save_current_level()
        L("saved level " + map_path)
    except Exception as e:
        L("save level ERR " + str(e))
    return True


def main():
    L("T380 engine AI setup start")
    ok = configure_skeleton_character()
    L("configure_character ok=" + str(ok))
    abp = create_anim_bp()
    L("abp=" + str(abp))
    # NavMesh on dungeon maps only (never Hub buildings)
    current = None
    try:
        current = unreal.EditorLevelLibrary.get_editor_world()
        L("editor world before=" + str(current))
    except Exception:
        pass
    for mp in MAPS:
        try:
            ensure_navmesh_on_map(mp)
        except Exception as e:
            L("map setup ERR " + mp + " " + traceback.format_exc())
    # Reconfigure after map switches (CDO still valid)
    try:
        configure_skeleton_character()
    except Exception as e:
        L("reconfigure ERR " + str(e))
    L("DONE")
    flush()
    print("WROTE", OUT)


main()
