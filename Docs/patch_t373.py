# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t373")
t=open(p,encoding="utf-8").read()
if "T373_SKEL_FACE_FIX" not in t:
    t=t.replace("T372_SKEL_FACE_RUN:","T372_SKEL_FACE_RUN T373_SKEL_FACE_FIX:",1)

# Mesh relative 270 makes run play perpendicular to actor forward -> sideways shuffle.
# Force mesh yaw 0; actor yaw = atan2; hard-zero pitch/roll.
t=t.replace("SKELETON_MESH_REL_YAW = 270.0","SKELETON_MESH_REL_YAW = 0.0",1)
t=t.replace("SKELETON_FACE_YAW_OFFSET = 0.0","SKELETON_FACE_YAW_OFFSET = 0.0  # mesh rel yaw forced to 0",1)

start=t.find("def _look_at_xy(actor, target_loc):")
end=t.find("def _move_actor_toward(actor, target_loc, speed, dt):")
if start<0 or end<0: raise SystemExit("markers")
new_look='''def _look_at_xy(actor, target_loc):
    """Face move direction: actor yaw=atan2, mesh relative yaw=0, pitch/roll forced 0.
    Also detach AIController rotation so default AI cannot tumble the pawn.
    """
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 16.0:
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        # Disable AI / CMC rotation fights
        try:
            ctrl = None
            try:
                ctrl = actor.get_controller()
            except Exception:
                ctrl = None
            if ctrl is not None:
                try:
                    # Stop default AI from steering rotation/movement while we drive chase in Python
                    ctrl.stop_movement()
                except Exception:
                    pass
                try:
                    actor.set_editor_property("use_controller_rotation_yaw", False)
                    actor.set_editor_property("use_controller_rotation_pitch", False)
                    actor.set_editor_property("use_controller_rotation_roll", False)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if isinstance(actor, unreal.Character):
                mc = actor.get_movement_component()
                if mc is not None:
                    for prop, val in (
                        ("orient_rotation_to_movement", False),
                        ("use_controller_desired_rotation", False),
                        ("b_orient_rotation_to_movement", False),
                    ):
                        try:
                            mc.set_editor_property(prop, val)
                        except Exception:
                            pass
        except Exception:
            pass
        # Mesh: force upright + yaw 0 so run anim faces actor forward
        try:
            mesh = _get_pawn_mesh(actor)
            if mesh is not None:
                try:
                    mesh.set_editor_property(
                        "relative_rotation",
                        unreal.Rotator(0.0, float(SKELETON_MESH_REL_YAW), 0.0),
                    )
                except Exception:
                    pass
        except Exception:
            pass
        # Actor: hard zero pitch/roll every time (fixes tumble seen in PIE)
        try:
            cur = actor.get_actor_rotation()
            cur_yaw = float(cur.yaw)
            diff = abs(((yaw - cur_yaw + 180.0) % 360.0) - 180.0)
            if diff < 2.0 and abs(float(cur.pitch)) < 1.0 and abs(float(cur.roll)) < 1.0:
                return
        except Exception:
            pass
        actor.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    except Exception:
        pass


'''
t=t[:start]+new_look+t[end:]

# At start of update for each enemy, also force upright once when aggroed - already in look_at

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK mesh_yaw", "SKELETON_MESH_REL_YAW = 0.0" in t)
