# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
old = '''def notify_hit(pawn):
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
new = '''def notify_hit(pawn):
    """Player hit: flinch up to 2 times (can interrupt attack); then armored until attack ends."""
    if pawn is None or (not _alive(pawn)):
        return False
    st = _state_for(pawn)
    now = float(st.get("t", 0.0) or 0.0)
    # out of flinch budget => hyper armor (even mid-attack)
    if int(st.get("flinch_left", 2) or 0) <= 0:
        return False
    dur = _anim_length(ANIM_HIT)
    st["hit_until"] = now + dur
    st["attack_hit_due"] = 0.0
    st["attack_until"] = 0.0  # interrupt attack if any
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
if old not in raw:
    print("MISSING")
else:
    raw = raw.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
    compile(raw, p, "exec")
    print("ok")
