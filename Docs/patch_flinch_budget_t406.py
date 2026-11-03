# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

old_st = '''        st = {
            "aggro": False,
            "anim": None,
            "in_melee_since": 0.0,
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,
            "attack_until": 0.0,
            "hit_until": 0.0,
            "t": 0.0,
        }'''
new_st = '''        st = {
            "aggro": False,
            "anim": None,
            "in_melee_since": 0.0,
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,
            "attack_until": 0.0,
            "hit_until": 0.0,
            "flinch_left": 2,
            "t": 0.0,
        }'''
if old_st not in raw:
    print("STATE_MISSING")
else:
    raw = raw.replace(old_st, new_st, 1)
    print("state_ok")

old_n = '''def notify_hit(pawn):
    """Player landed a hit: play Hit_A and cancel current attack windup."""
    if pawn is None or (not _alive(pawn)):
        return False
    st = _state_for(pawn)
    now = float(st.get("t", 0.0) or 0.0)
    dur = _anim_length(ANIM_HIT)
    st["hit_until"] = now + dur
    st["attack_hit_due"] = 0.0
    st["attack_until"] = 0.0
    st["last_attack_t"] = now  # push cooldown so no instant re-swing
    st["in_melee_since"] = 0.0
    _play_anim(pawn, ANIM_HIT, False)
    st["anim"] = "hit"
    try:
        ctrl = _get_ai_controller(pawn)
        if ctrl:
            _stop_move(ctrl)
    except Exception:
        pass
    return True'''

new_n = '''def notify_hit(pawn):
    """Player hit: at most 2 flinches, then none until next attack ends; never during attack."""
    if pawn is None or (not _alive(pawn)):
        return False
    st = _state_for(pawn)
    now = float(st.get("t", 0.0) or 0.0)
    # no flinch while attack clip is playing
    if float(st.get("attack_until", 0.0) or 0.0) > now or st.get("anim") == "attack":
        return False
    if int(st.get("flinch_left", 2) or 0) <= 0:
        return False
    dur = _anim_length(ANIM_HIT)
    st["hit_until"] = now + dur
    st["attack_hit_due"] = 0.0
    st["attack_until"] = 0.0
    st["last_attack_t"] = now
    st["in_melee_since"] = 0.0
    st["flinch_left"] = int(st.get("flinch_left", 2)) - 1
    _play_anim(pawn, ANIM_HIT, False)
    st["anim"] = "hit"
    try:
        ctrl = _get_ai_controller(pawn)
        if ctrl:
            _stop_move(ctrl)
    except Exception:
        pass
    return True'''

if old_n not in raw:
    print("NOTIFY_MISSING")
else:
    raw = raw.replace(old_n, new_n, 1)
    print("notify_ok")

old_end = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            if st.get("anim") == "attack":
                st["anim"] = None'''
new_end = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None'''
if old_end not in raw:
    print("ATK_END_MISSING")
else:
    raw = raw.replace(old_end, new_end, 1)
    print("atk_end_ok")

io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
compile(raw, p, "exec")
print("syntax_ok")
