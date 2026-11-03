# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()

raw2, n = re.subn(r"ATTACK_HIT_DELAY\s*=\s*[0-9.]+", "ATTACK_HIT_DELAY = 0.5", raw, count=1)
print("hit_delay", n)

old = '''            elif st.get("anim") != "attack" and st.get("anim") != "idle":
                _play_anim(enemy, ANIM_IDLE, True)
                st["anim"] = "idle"
            continue'''
new = '''            elif st.get("anim") != "attack":
                # keep run lean in melee so we don't pop upright before the chop
                if st.get("anim") != "run":
                    _play_anim(enemy, ANIM_RUN, True)
                    st["anim"] = "run"
            continue'''
if old in raw2:
    raw2 = raw2.replace(old, new, 1)
    print("melee_keep_run")
else:
    print("melee_block_MISSING")
    idx = raw2.find('st["anim"] = "attack"')
    print(repr(raw2[idx:idx+500]) if idx >= 0 else "no")

io.open(p, "w", encoding="utf-8", newline="\n").write(raw2)
print("written")
for i, line in enumerate(io.open(p, encoding="utf-8"), 1):
    if "ATTACK_HIT_DELAY" in line or "keep run lean" in line:
        print("%d:%s" % (i, line.rstrip()))
    if 'ANIM_IDLE' in line and i > 450:
        print("%d:%s" % (i, line.rstrip()))
