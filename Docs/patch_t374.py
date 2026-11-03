# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t374")
t=open(p,encoding="utf-8").read()
if "T374_SKEL_UPRIGHT" not in t:
    t=t.replace("T373_SKEL_FACE_FIX:","T373_SKEL_FACE_FIX T374_SKEL_UPRIGHT:",1)

# Replace _look_at_xy and _move_actor_toward with CMC-driven upright chase
start=t.find("def _look_at_xy(actor, target_loc):")
end=t.find("def _has_line_of_sight(world, enemy, pawn):")
if start<0 or end<0: raise SystemExit("markers %s %s"%(start,end))

new_funcs='''def _skeleton_force_upright(actor):
    """Keep capsule upright. set_actor_location chase was tumbling pitch/roll; player bump fixed it via collision."""
    if actor is None:
        return
    try:
        cur = actor.get_actor_rotation()
        if abs(float(cur.pitch)) < 0.5 and abs(float(cur.roll)) < 0.5:
            return
        actor.set_actor_rotation(unreal.Rotator(0.0, float(cur.yaw), 0.0), False)
    except Exception:
        pass


def _skeleton_prepare_move(actor):
    """Strip AIController steering + lock CMC to walking upright."""
    if actor is None:
        return None
    try:
        ctrl = actor.get_controller()
    except Exception:
        ctrl = None
    if ctrl is not None:
        try:
            ctrl.stop_movement()
        except Exception:
            pass
        # Unpossess AI so default AI cannot tumble/rotate the pawn while Python chases
        try:
            if "AIController" in ctrl.get_class().get_name():
                ctrl.unpossess()
        except Exception:
            pass
    try:
        actor.set_editor_property("use_controller_rotation_yaw", False)
        actor.set_editor_property("use_controller_rotation_pitch", False)
        actor.set_editor_property("use_controller_rotation_roll", False)
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
            ("orient_rotation_to_movement", True),
            ("use_controller_desired_rotation", False),
            ("rotation_rate", unreal.Rotator(0.0, 480.0, 0.0)),
        ):
            try:
                mc.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            mc.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
        except Exception:
            try:
                mc.set_editor_property("movement_mode", unreal.MovementMode.MOVE_WALKING)
            except Exception:
                pass
    # Mesh upright, face actor forward
    try:
        mesh = _get_pawn_mesh(actor)
        if mesh is not None:
            mesh.set_editor_property(
                "relative_rotation",
                unreal.Rotator(0.0, float(SKELETON_MESH_REL_YAW), 0.0),
            )
            # Avoid anim root motion flipping the body
            try:
                mesh.set_editor_property("root_motion_mode", 0)  # NoRootMotionExtraction if enum fails below
            except Exception:
                pass
            try:
                mesh.set_editor_property(
                    "root_motion_mode",
                    unreal.RootMotionMode.NO_ROOT_MOTION_EXTRACTION,
                )
            except Exception:
                pass
    except Exception:
        pass
    _skeleton_force_upright(actor)
    return mc


def _look_at_xy(actor, target_loc):
    """Yaw-only face; always zero pitch/roll. Used when standing in melee."""
    try:
        _skeleton_prepare_move(actor)
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 16.0:
            _skeleton_force_upright(actor)
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        actor.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    except Exception:
        pass


def _move_actor_toward(actor, target_loc, speed, dt):
    """Chase with CharacterMovement add_movement_input (keeps upright). No set_actor_location.
    Returns remaining XY distance.
    """
    try:
        al = actor.get_actor_location()
    except Exception:
        return 99999.0
    dx = float(target_loc.x) - float(al.x)
    dy = float(target_loc.y) - float(al.y)
    dist_xy = (dx * dx + dy * dy) ** 0.5
    if dist_xy < 1.0:
        _skeleton_force_upright(actor)
        return dist_xy
    mc = _skeleton_prepare_move(actor)
    if mc is not None:
        try:
            mc.set_editor_property("max_walk_speed", float(speed))
        except Exception:
            try:
                mc.max_walk_speed = float(speed)
            except Exception:
                pass
        try:
            actor.add_movement_input(unreal.Vector(dx / dist_xy, dy / dist_xy, 0.0), 1.0, False)
        except Exception as e:
            _log("T374 add_movement_input " + str(e))
    else:
        # Non-character fallback: translate but force upright yaw
        step = float(speed) * float(dt)
        if step > dist_xy:
            step = dist_xy
        nx = float(al.x) + dx / dist_xy * step
        ny = float(al.y) + dy / dist_xy * step
        nz = float(al.z)
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        try:
            actor.set_actor_location(unreal.Vector(nx, ny, nz), True, False)
        except Exception:
            try:
                actor.set_actor_location(unreal.Vector(nx, ny, nz), False, True)
            except Exception:
                pass
        try:
            actor.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
        except Exception:
            pass
    _skeleton_force_upright(actor)
    try:
        al2 = actor.get_actor_location()
        dx2 = float(target_loc.x) - float(al2.x)
        dy2 = float(target_loc.y) - float(al2.y)
        return (dx2 * dx2 + dy2 * dy2) ** 0.5
    except Exception:
        return dist_xy


'''
t=t[:start]+new_funcs+t[end:]

# Also force upright each enemy tick when aggroed - inject after st = _skeleton_ai_state(enemy)
needle='        st = _skeleton_ai_state(enemy)\n        # Pending attack damage apply'
repl='        st = _skeleton_ai_state(enemy)\n        try:\n            _skeleton_force_upright(enemy)\n        except Exception:\n            pass\n        # Pending attack damage apply'
if needle not in t:
    # try alternate
    needle='        st = _skeleton_ai_state(enemy)\n        # Pending attack damage apply'
if needle not in t:
    raise SystemExit("inject point missing")
t=t.replace(needle,repl,1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK upright helpers present", "_skeleton_force_upright" in t, "add_movement_input" in t[t.find("def _move_actor_toward"):t.find("def _has_line_of_sight")])
