# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

old_lock = '''        # Keep playing full attack clip once triggered (no early cut to run/idle)
        atk_until = float(st.get("attack_until", 0.0) or 0.0)
        if atk_until > 0.0 and now < atk_until:
            if ctrl:
                _stop_move(ctrl)
                _set_focus_player(ctrl, player)
            st["anim"] = "attack"
            continue
        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            if st.get("anim") == "attack":
                st["anim"] = None'''

new_lock = '''        # Attack lock: stay in run lean (Chop clip starts upright and pops)
        atk_until = float(st.get("attack_until", 0.0) or 0.0)
        if atk_until > 0.0 and now < atk_until:
            if ctrl:
                _stop_move(ctrl)
                _set_focus_player(ctrl, player)
            if st.get("anim") != "run":
                _play_anim(enemy, ANIM_RUN, True)
                st["anim"] = "run"
            continue
        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0'''

old_trig = '''            if windup_ok and cd_ok and float(st.get("attack_hit_due", 0.0) or 0.0) <= 0.0:
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + ATTACK_HIT_DELAY
                st["attack_until"] = now + _anim_length(ANIM_ATK)
                _play_anim(enemy, ANIM_ATK, False)
                st["anim"] = "attack"
            elif st.get("anim") != "attack":
                # keep run lean in melee so we don't pop upright before the chop
                if st.get("anim") != "run":
                    _play_anim(enemy, ANIM_RUN, True)
                    st["anim"] = "run"
            continue'''

new_trig = '''            if windup_ok and cd_ok and float(st.get("attack_hit_due", 0.0) or 0.0) <= 0.0:
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + ATTACK_HIT_DELAY
                # lock a bit past hit; keep run lean instead of upright Chop
                st["attack_until"] = now + max(1.0, float(ATTACK_HIT_DELAY) + 0.45)
                if st.get("anim") != "run":
                    _play_anim(enemy, ANIM_RUN, True)
                    st["anim"] = "run"
            else:
                if st.get("anim") != "run":
                    _play_anim(enemy, ANIM_RUN, True)
                    st["anim"] = "run"
            continue'''

ok = True
if old_lock not in raw:
    print("LOCK_MISSING")
    ok = False
else:
    raw = raw.replace(old_lock, new_lock, 1)
    print("lock_ok")
if old_trig not in raw:
    print("TRIG_MISSING")
    ok = False
else:
    raw = raw.replace(old_trig, new_trig, 1)
    print("trig_ok")
if ok:
    io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
    print("written")
else:
    print("ABORT")
for i, line in enumerate(io.open(p, encoding="utf-8"), 1):
    if any(x in line for x in ("attack_until", "ANIM_ATK", "run lean", "Attack lock", "Chop")):
        if 420 <= i <= 500 or "ANIM_ATK" in line and i < 30:
            print("%d:%s" % (i, line.rstrip()))
