# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, encoding="utf-8").read()
# ensure windup 0.5
raw2, n1 = re.subn(r"ATTACK_WINDUP\s*=\s*[0-9.]+", "ATTACK_WINDUP = 0.5", raw, count=1)
print("windup", n1)

old = '''            elif st.get("anim") != "attack":
                # keep run lean in melee so we don't pop upright before the chop
                if st.get("anim") != "run":
                    _play_anim(enemy, ANIM_RUN, True)
                    st["anim"] = "run"
            continue'''
new = '''            elif st.get("anim") != "attack":
                # windup: stand idle (not run) until chop starts
                if st.get("anim") != "idle":
                    _play_anim(enemy, ANIM_IDLE, True)
                    st["anim"] = "idle"
            continue'''
if old not in raw2:
    print("MELEE_MISSING")
    # show nearby
    i = raw2.find("windup_ok")
    print(repr(raw2[i:i+450]) if i>=0 else "no windup_ok")
else:
    raw2 = raw2.replace(old, new, 1)
    print("melee_idle_ok")
io.open(p, "w", encoding="utf-8", newline="\n").write(raw2)
compile(raw2, p, "exec")
print("syntax_ok")
