# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

# Add anim length helper if missing
if "def _anim_length" not in raw:
    helper = '''
def _anim_length(path):
    seq = _load_anim(path)
    if seq is None:
        return 1.0
    try:
        return max(0.35, float(seq.get_editor_property("sequence_length")))
    except Exception:
        pass
    try:
        return max(0.35, float(seq.sequence_length))
    except Exception:
        return 1.0


'''
    raw = raw.replace("def _play_anim(pawn, path, looping):", helper + "def _play_anim(pawn, path, looping):", 1)
    print("added _anim_length")
else:
    print("_anim_length exists")

# Ensure state has attack_until in _state_for
if '"attack_until"' not in raw:
    raw = raw.replace(
        '"attack_hit_due": 0.0,\n            "t": 0.0,',
        '"attack_hit_due": 0.0,\n            "attack_until": 0.0,\n            "t": 0.0,',
        1)
    print("state field added")
else:
    print("state field exists")

# After damage-due block and dist calc, before LOSE_RANGE: lock during attack anim
marker = '        try:\n            dist = _dist(enemy.get_actor_location(), player.get_actor_location())\n        except Exception:\n            continue\n\n        if dist > LOSE_RANGE:'
lock = '''        try:
            dist = _dist(enemy.get_actor_location(), player.get_actor_location())
        except Exception:
            continue

        # Keep playing full attack clip once triggered (no early cut to run/idle)
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
                st["anim"] = None

        if dist > LOSE_RANGE:'''

if "Keep playing full attack clip" not in raw:
    if marker not in raw:
        print("MARKER_MISSING")
    else:
        raw = raw.replace(marker, lock, 1)
        print("lock inserted")
else:
    print("lock exists")

# When starting attack, set attack_until from anim length
old_start = '''                st["last_attack_t"] = now
                st["attack_hit_due"] = now + ATTACK_HIT_DELAY
                _play_anim(enemy, ANIM_ATK, False)
                st["anim"] = "attack"'''
new_start = '''                st["last_attack_t"] = now
                st["attack_hit_due"] = now + ATTACK_HIT_DELAY
                st["attack_until"] = now + _anim_length(ANIM_ATK)
                _play_anim(enemy, ANIM_ATK, False)
                st["anim"] = "attack"'''
if "attack_until\"] = now + _anim_length" not in raw:
    if old_start not in raw:
        print("START_MISSING")
    else:
        raw = raw.replace(old_start, new_start, 1)
        print("start patched")
else:
    print("start exists")

# While chasing, never interrupt an in-progress attack anim
old_chase = '''        if st.get("anim") != "run":
            if st.get("anim") == "attack" and float(st.get("attack_hit_due", 0.0) or 0.0) > 0.0:
                pass
            else:
                _play_anim(enemy, ANIM_RUN, True)
                st["anim"] = "run"'''
new_chase = '''        if st.get("anim") != "run":
            if st.get("anim") == "attack" and float(st.get("attack_until", 0.0) or 0.0) > now:
                pass
            else:
                _play_anim(enemy, ANIM_RUN, True)
                st["anim"] = "run"'''
if old_chase in raw:
    raw = raw.replace(old_chase, new_chase, 1)
    print("chase patched")
else:
    print("chase_block_skip", "attack_until" in raw and "anim")

io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
print("written", len(raw))
# verify snippets
for i, line in enumerate(io.open(p, encoding="utf-8"), 1):
    if "attack_until" in line or "_anim_length" in line or "full attack" in line:
        print("%d:%s" % (i, line.rstrip()))
