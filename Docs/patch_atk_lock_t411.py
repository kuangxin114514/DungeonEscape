# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
raw = io.open(p, "r", encoding="utf-8").read()

if "_ATTACK_UNTIL" not in raw:
    raw = raw.replace(
        "_LAST_ATTACK_T = [0.0]",
        "_LAST_ATTACK_T = [0.0]\n_ATTACK_UNTIL = [0.0]  # next LMB only after current chop ends",
        1,
    )
    print("until_var")
else:
    print("until_exists")

old = '''    now = time.time()
    if (now - _LAST_ATTACK_T[0]) < ATTACK_COOLDOWN:
        return False
    # If previous single-node attack still playing, ignore
    if _ATTACK_RESTORE[1] is not None and now < _ATTACK_RESTORE[0]:
        return False'''
new = '''    now = time.time()
    # Wait until current attack anim finishes (simplest lock)
    if now < float(_ATTACK_UNTIL[0] or 0.0):
        return False
    if (now - _LAST_ATTACK_T[0]) < ATTACK_COOLDOWN:
        return False
    # If previous single-node attack still playing, ignore
    if _ATTACK_RESTORE[1] is not None and now < _ATTACK_RESTORE[0]:
        return False'''
if old not in raw.replace("\r\n","\n") and old.replace("\n","\r\n") not in raw:
    # try with file newlines
    if "\r\n" in raw:
        old2 = old.replace("\n","\r\n"); new2 = new.replace("\n","\r\n")
    else:
        old2, new2 = old, new
    if old2 not in raw:
        print("GATE_MISSING")
    else:
        raw = raw.replace(old2, new2, 1)
        print("gate_ok")
else:
    raw_n = raw.replace("\r\n","\n")
    if old in raw_n:
        raw = raw_n.replace(old, new, 1)
        if "\r\n" in io.open(p,encoding="utf-8").read()[:200] or True:
            pass
        print("gate_ok_lf")
    else:
        print("GATE_MISSING2")

old_p = '''    if played:
        _LAST_ATTACK_T[0] = now
        _print(world, u"挥砍！", (1.0, 0.7, 0.2, 1.0), 0.5)
        _log("attack OK via=%s dur=%.2f" % (via, duration))
        return True'''
new_p = '''    if played:
        _LAST_ATTACK_T[0] = now
        _ATTACK_UNTIL[0] = now + float(duration)
        _print(world, u"挥砍！", (1.0, 0.7, 0.2, 1.0), 0.5)
        _log("attack OK via=%s dur=%.2f" % (via, duration))
        return True'''
# normalize
src = raw.replace("\r\n","\n")
if old_p not in src:
    print("PLAYED_MISSING")
else:
    src = src.replace(old_p, new_p, 1)
    print("played_ok")

# reset _ATTACK_UNTIL on PIE bootstrap near _LAST_ATTACK_T or _PENDING clear
if "_ATTACK_UNTIL[0] = 0.0" not in src:
    if "_PREV_LMB[0] = False" in src:
        src = src.replace("_PREV_LMB[0] = False", "_PREV_LMB[0] = False\n    try:\n        _ATTACK_UNTIL[0] = 0.0\n    except Exception:\n        pass", 1)
        print("bootstrap_reset")
    else:
        print("no_bootstrap")

io.open(p, "w", encoding="utf-8", newline="\n").write(src)
compile(src, p, "exec")
print("syntax_ok")
