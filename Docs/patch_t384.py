# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
shutil.copy2(p, p+".pre_t384")
t=open(p,encoding="utf-8").read()
if "T384_ALWAYS_FACE" not in t:
    t=t.replace(
        '"""T380 engine-style skeleton AI (MoveTo + OrientRotationToMovement).',
        '"""T380/T384 engine-style skeleton AI (MoveTo + always face player).\n# T384_ALWAYS_FACE',
        1,
    )

# Add FACE_YAW_OFFSET constant after CHEST_Z
if "FACE_YAW_OFFSET" not in t:
    t=t.replace("CHEST_Z = 60.0\n", "CHEST_Z = 60.0\nFACE_YAW_OFFSET = 90.0  # mesh relative yaw ~270 on BP\n", 1)

face_fn='''
def _face_player(pawn, player):
    """Always yaw toward player; pitch/roll forced 0. Mesh authored yaw ~270 => +90 offset."""
    if pawn is None or player is None:
        return
    try:
        al = pawn.get_actor_location()
        pl = player.get_actor_location()
        dx = float(pl.x) - float(al.x)
        dy = float(pl.y) - float(al.y)
        if dx * dx + dy * dy < 4.0:
            cur = pawn.get_actor_rotation()
            if abs(float(cur.pitch)) > 0.5 or abs(float(cur.roll)) > 0.5:
                pawn.set_actor_rotation(unreal.Rotator(0.0, float(cur.yaw), 0.0), False)
            return
        yaw = math.degrees(math.atan2(dy, dx)) + float(FACE_YAW_OFFSET)
        pawn.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    except Exception:
        pass


'''

if "def _face_player(" not in t:
    t=t.replace("def _add_input_toward(pawn, target_loc):", face_fn+"def _add_input_toward(pawn, target_loc):", 1)

# In tick, after aggro confirmed / before attack and chase, face player
# When in melee before continue:
old_melee='''        if dist <= ATTACK_RANGE:
            if ctrl:
                _stop_move(ctrl)
            if float(st.get("in_melee_since", 0.0) or 0.0) <= 0.0:'''
new_melee='''        if dist <= ATTACK_RANGE:
            _face_player(enemy, player)
            if ctrl:
                _stop_move(ctrl)
            if float(st.get("in_melee_since", 0.0) or 0.0) <= 0.0:'''
if old_melee not in t: raise SystemExit("melee block missing")
t=t.replace(old_melee, new_melee, 1)

old_chase='''        st["in_melee_since"] = 0.0
        _move_to(ctrl, player, enemy)
        if st.get("anim") != "run":'''
new_chase='''        st["in_melee_since"] = 0.0
        _face_player(enemy, player)
        _move_to(ctrl, player, enemy)
        _face_player(enemy, player)  # again after move so ORTM cannot leave sideways
        if st.get("anim") != "run":'''
if old_chase not in t: raise SystemExit("chase block missing")
t=t.replace(old_chase, new_chase, 1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK face", "def _face_player" in t, "FACE_YAW_OFFSET" in t)
