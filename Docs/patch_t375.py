# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t375")
t=open(p,encoding="utf-8").read()
if "T375_FACE_NO_FLIP" not in t:
    t=t.replace("T374_SKEL_UPRIGHT:","T374_SKEL_UPRIGHT T375_FACE_NO_FLIP:",1)

start=t.find("def _skeleton_force_upright(actor):")
end=t.find("def _has_line_of_sight(world, enemy, pawn):")
if start<0 or end<0: raise SystemExit("markers %s %s"%(start,end))

new=r'''def _skeleton_force_upright(actor):
    """Zero pitch/roll only (keep current yaw)."""
    if actor is None:
        return
    try:
        cur = actor.get_actor_rotation()
        if abs(float(cur.pitch)) < 0.25 and abs(float(cur.roll)) < 0.25:
            return
        actor.set_actor_rotation(unreal.Rotator(0.0, float(cur.yaw), 0.0), False)
    except Exception:
        pass


def _skeleton_face_target(actor, target_loc):
    """Always face target in XY with pitch=roll=0 (chase must look at player)."""
    if actor is None or target_loc is None:
        return
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 1.0:
            _skeleton_force_upright(actor)
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        actor.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    except Exception:
        _skeleton_force_upright(actor)


def _skeleton_disable_physics_flip(actor):
    """Contact with player was flipping the body (mesh physics / impulses). Hard-disable."""
    if actor is None:
        return
    try:
        ctrl = actor.get_controller()
        if ctrl is not None:
            try:
                ctrl.stop_movement()
            except Exception:
                pass
            try:
                if "AIController" in ctrl.get_class().get_name():
                    ctrl.unpossess()
            except Exception:
                pass
    except Exception:
        pass
    for prop, val in (
        ("use_controller_rotation_yaw", False),
        ("use_controller_rotation_pitch", False),
        ("use_controller_rotation_roll", False),
    ):
        try:
            actor.set_editor_property(prop, val)
        except Exception:
            pass
    mc = None
    try:
        if isinstance(actor, unreal.Character):
            mc = actor.get_movement_component()
    except Exception:
        mc = None
    if mc is not None:
        for prop, val in (
            ("orient_rotation_to_movement", False),  # we set yaw ourselves toward player
            ("use_controller_desired_rotation", False),
            ("enable_physics_interaction", False),
            ("b_enable_physics_interaction", False),
            ("push_force_factor", 0.0),
            ("initial_push_force_factor", 0.0),
        ):
            try:
                mc.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            mc.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
        except Exception:
            pass
    mesh = None
    try:
        mesh = _get_pawn_mesh(actor)
    except Exception:
        mesh = None
    if mesh is not None:
        try:
            mesh.set_simulate_physics(False)
        except Exception:
            pass
        try:
            mesh.set_all_bodies_simulate_physics(False)
        except Exception:
            pass
        try:
            mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
        except Exception:
            try:
                mesh.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_ONLY)
            except Exception:
                pass
        try:
            mesh.set_editor_property(
                "relative_rotation",
                unreal.Rotator(0.0, float(SKELETON_MESH_REL_YAW), 0.0),
            )
        except Exception:
            pass
        for prop, val in (
            ("enable_gravity", False),
            ("update_overlaps_on_animation_finalize", False),
        ):
            try:
                mesh.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            mesh.set_editor_property(
                "root_motion_mode",
                unreal.RootMotionMode.NO_ROOT_MOTION_EXTRACTION,
            )
        except Exception:
            pass
    return mc


def _skeleton_prepare_move(actor):
    return _skeleton_disable_physics_flip(actor)


def _look_at_xy(actor, target_loc):
    _skeleton_disable_physics_flip(actor)
    _skeleton_face_target(actor, target_loc)


def _move_actor_toward(actor, target_loc, speed, dt):
    """Translate with sweep + ALWAYS face player upright. No CMC physics push (contact was flipping)."""
    try:
        al = actor.get_actor_location()
    except Exception:
        return 99999.0
    dx = float(target_loc.x) - float(al.x)
    dy = float(target_loc.y) - float(al.y)
    dist_xy = (dx * dx + dy * dy) ** 0.5
    _skeleton_disable_physics_flip(actor)
    if dist_xy < 1.0:
        _skeleton_face_target(actor, target_loc)
        return dist_xy
    step = float(speed) * float(dt)
    if step > dist_xy:
        step = dist_xy
    nx = float(al.x) + dx / dist_xy * step
    ny = float(al.y) + dy / dist_xy * step
    nz = float(al.z)
    try:
        actor.set_actor_location(unreal.Vector(nx, ny, nz), True, False)
    except Exception:
        try:
            actor.set_actor_location(unreal.Vector(nx, ny, nz), False, True)
        except Exception as e:
            _log("T375 move fail " + str(e))
    # Face player every move step (user request); hard upright
    _skeleton_face_target(actor, target_loc)
    try:
        al2 = actor.get_actor_location()
        dx2 = float(target_loc.x) - float(al2.x)
        dy2 = float(target_loc.y) - float(al2.y)
        return (dx2 * dx2 + dy2 * dy2) ** 0.5
    except Exception:
        return dist_xy


'''
t=t[:start]+new+t[end:]

# In update_skeleton_ai, after force upright, also face player when aggroed — strengthen chase/melee face
# Replace inject: already has _skeleton_force_upright — add face when want_aggro later
# In chase branch already calls _move which faces. In melee calls _look_at_xy. Good.
# Also after pending damage / every aggro frame force face — find "# Aggroed" block

# Ensure melee branch always faces (already does). After contact, force upright+face each tick when aggro:
old_aggro_mark='        # Aggroed\n        if dist <= float(SKELETON_ATTACK_RANGE):'
if old_aggro_mark not in t:
    raise SystemExit("aggro mark missing")
t=t.replace(
    old_aggro_mark,
    '        # Aggroed — always face player + kill any tumble from collision\n'
    '        _skeleton_disable_physics_flip(enemy)\n'
    '        _skeleton_face_target(enemy, pl)\n'
    '        if dist <= float(SKELETON_ATTACK_RANGE):',
    1,
)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", "_skeleton_face_target" in t, "QUERY_ONLY" in t, "T375_FACE_NO_FLIP" in t)
