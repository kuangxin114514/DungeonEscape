# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
old = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None'''
new = '''        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            # keep flinch_left: after 2 flinches stay armored until de-aggro
            if st.get("anim") == "attack":
                st["anim"] = None'''
if old not in raw:
    print("ATK_END_MISSING")
else:
    raw = raw.replace(old, new, 1)
    print("removed_atk_reset")

# reset flinch on lose aggro (LOSE_RANGE and wall drop)
old1 = '''        if dist > LOSE_RANGE:
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue'''
new1 = '''        if dist > LOSE_RANGE:
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            st["flinch_left"] = 2
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue'''
if old1 not in raw:
    print("LOSE_MISSING")
else:
    raw = raw.replace(old1, new1, 1)
    print("lose_reset_ok")

old2 = '''        elif not los_ok:
            # simplest: wall / no sight => drop aggro, don't chase through walls
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue'''
new2 = '''        elif not los_ok:
            # simplest: wall / no sight => drop aggro, don't chase through walls
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            st["flinch_left"] = 2
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            if st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue'''
if old2 not in raw:
    print("LOS_DROP_MISSING")
else:
    raw = raw.replace(old2, new2, 1)
    print("los_drop_reset_ok")

io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
compile(raw, p, "exec")
print("syntax_ok")
