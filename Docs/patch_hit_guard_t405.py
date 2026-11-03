# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
old = '''        due = float(st.get("attack_hit_due", 0.0) or 0.0)
        if due > 0.0 and now >= due:
            st["attack_hit_due"] = 0.0
            try:
                d = _dist(enemy.get_actor_location(), player.get_actor_location())
            except Exception:
                d = 9999.0
            if d <= ATTACK_RANGE * 1.35:
                _damage_player(world, player, ATTACK_DAMAGE)'''
new = '''        # No damage resolve while flinching
        hit_until_early = float(st.get("hit_until", 0.0) or 0.0)
        due = float(st.get("attack_hit_due", 0.0) or 0.0)
        if due > 0.0 and now >= due:
            st["attack_hit_due"] = 0.0
            if hit_until_early <= 0.0 or now >= hit_until_early:
                try:
                    d = _dist(enemy.get_actor_location(), player.get_actor_location())
                except Exception:
                    d = 9999.0
                if d <= ATTACK_RANGE * 1.35:
                    _damage_player(world, player, ATTACK_DAMAGE)'''
if old not in raw:
    print("DUE_MISSING")
else:
    raw = raw.replace(old, new, 1)
    print("due_guard_ok")
old2 = '''            if windup_ok and cd_ok and float(st.get("attack_hit_due", 0.0) or 0.0) <= 0.0:'''
new2 = '''            if windup_ok and cd_ok and float(st.get("attack_hit_due", 0.0) or 0.0) <= 0.0 and float(st.get("hit_until", 0.0) or 0.0) <= now:'''
if old2 not in raw:
    print("TRIG_MISSING")
else:
    raw = raw.replace(old2, new2, 1)
    print("trig_guard_ok")
io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
compile(raw, p, "exec")
print("syntax_ok")
