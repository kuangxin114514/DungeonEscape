# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

if "ANIM_WALK" not in raw:
    raw = raw.replace(
        'ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig"',
        'ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig"\n'
        'ANIM_WALK = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig"\n'
        'STOP_BLEND = 0.45  # run -> walk -> idle',
        1,
    )
    print("walk_const")
else:
    print("walk_exists")

# helper to go idle with blend
helper = '''
def _go_idle(pawn, st, now):
    """Run/stop: brief walk then idle so lean does not pop upright."""
    if st.get("anim") in ("run", "stop"):
        if st.get("anim") != "stop":
            _play_anim(pawn, ANIM_WALK, True)
            st["anim"] = "stop"
        st["stop_until"] = float(now) + float(STOP_BLEND)
        return
    if st.get("anim") != "idle":
        _play_anim(pawn, ANIM_IDLE, True)
        st["anim"] = "idle"
        st["stop_until"] = 0.0


'''

if "def _go_idle(" not in raw:
    raw = raw.replace("\ndef clear_state():", "\n" + helper + "def clear_state():", 1)
    if "def _go_idle(" not in raw:
        raw = raw.replace("def clear_state():", helper + "def clear_state():", 1)
    print("helper_ok" if "def _go_idle(" in raw else "helper_fail")
else:
    print("helper_exists")

# add stop_until to state
old_st = '''            "hit_until": 0.0,
            "flinch_left": 2,
            "t": 0.0,'''
new_st = '''            "hit_until": 0.0,
            "flinch_left": 2,
            "stop_until": 0.0,
            "t": 0.0,'''
if old_st in raw:
    raw = raw.replace(old_st, new_st, 1)
    print("state_ok")
else:
    print("state_miss")

# After hit/attack locks, handle stop blend before other idle switches
# Insert after attack_until clear block ends - find a unique spot after atk_until clear

marker = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None

        if dist > LOSE_RANGE:'''

insert = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None

        # Finish run-stop blend into idle
        stop_until = float(st.get("stop_until", 0.0) or 0.0)
        if st.get("anim") == "stop":
            if now < stop_until:
                if ctrl:
                    _stop_move(ctrl)
                continue
            _play_anim(enemy, ANIM_IDLE, True)
            st["anim"] = "idle"
            st["stop_until"] = 0.0

        if dist > LOSE_RANGE:'''

if marker not in raw:
    print("MARKER_MISS")
else:
    raw = raw.replace(marker, insert, 1)
    print("stop_tick_ok")

# Replace idle snaps with _go_idle
# Pattern 1: lose range
raw2 = raw
count = 0
# replace blocks that set idle from various places - careful with attack/hit

repls = [
(
'''            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue

        los_ok = _has_los''',
'''            _go_idle(enemy, st, now)
            continue

        los_ok = _has_los'''
),
(
'''            else:
                if st.get("anim") != "idle":
                    _play_anim(enemy, ANIM_IDLE, True)
                    st["anim"] = "idle"
                continue
        elif not los_ok:''',
'''            else:
                _go_idle(enemy, st, now)
                continue
        elif not los_ok:'''
),
(
'''            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue

        if dist <= ATTACK_RANGE:''',
'''            _go_idle(enemy, st, now)
            continue

        if dist <= ATTACK_RANGE:'''
),
]
for a,b in repls:
    if a in raw2:
        raw2 = raw2.replace(a, b, 1)
        count += 1
        print("repl", count)
    else:
        print("miss repl", count+1)

io.open(p, "w", encoding="utf-8", newline="\n").write(raw2)
compile(raw2, p, "exec")
print("syntax_ok", "go_idle_calls", raw2.count("_go_idle("))
