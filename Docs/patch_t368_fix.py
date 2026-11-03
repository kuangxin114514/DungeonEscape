# -*- coding: utf-8 -*-
from __future__ import print_function
import io
RUNTIME = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t368_fix.txt"
log=[]
def L(m):
    log.append(str(m)); print(m)
with io.open(RUNTIME,"r",encoding="utf-8") as f:
    src=f.read()

HOOK = '''    # T368_SKELETON_AI: aggro (range+LOS), chase run anim, melee attack 5 dmg
    try:
        if pawn is not None:
            update_skeleton_ai(world, pawn, dt)
            _purge_dead_skeleton_ai_keys(world)
    except Exception as e:
        _log("T368_SKELETON_AI " + str(e))
'''

# Insert hook only inside _on_tick after ensure_enemy_health_bars log
on_tick_start = src.find("\ndef _on_tick(dt):")
bootstrap_start = src.find("\ndef bootstrap():")
if on_tick_start < 0 or bootstrap_start < 0:
    L("FAIL find tick/bootstrap"); open(OUT,"w",encoding="utf-8").write("\n".join(log)); raise SystemExit(1)
tick_body = src[on_tick_start:bootstrap_start]
if "update_skeleton_ai(world, pawn, dt)" not in tick_body:
    anchor = '        _log("ensure_enemy_health_bars " + str(e))\n'
    pos = tick_body.find(anchor)
    if pos < 0:
        L("FAIL tick anchor"); open(OUT,"w",encoding="utf-8").write("\n".join(log)); raise SystemExit(2)
    tick_body = tick_body[:pos+len(anchor)] + "\n" + HOOK + tick_body[pos+len(anchor):]
    src = src[:on_tick_start] + tick_body + src[bootstrap_start:]
    L("inserted tick hook in _on_tick")
else:
    L("tick hook already in _on_tick")

# Ensure bootstrap clears AI — find last _PENDING_ATTACK_HIT in bootstrap section
boot = src[bootstrap_start:]
if "bootstrap T368 clear" not in boot:
    # inject before final _log("runtime ready
    marker = '    _PENDING_ATTACK_HIT[0] = None\n'
    # use last occurrence in bootstrap
    idx = boot.rfind(marker)
    if idx < 0:
        L("FAIL bootstrap pending marker")
    else:
        insert = marker + '''    try:
        _clear_skeleton_ai()
        _reset_player_hp(None)
        _log("bootstrap T368 clear")
    except Exception:
        pass
'''
        boot = boot[:idx] + insert + boot[idx+len(marker):]
        src = src[:bootstrap_start] + boot
        L("inserted bootstrap T368 clear")
else:
    L("bootstrap already has T368 clear")

# Also ensure _reset_ui_after_travel clear is OK — rename log message so it's not confused
src2 = src.replace(
    '_log("bootstrap T368 clear")\n    except Exception:\n        pass\n    _DUNGEON_PAWN_TRIED[0] = False',
    '_log("T278/T368 reset clear skeleton AI")\n    except Exception:\n        pass\n    _DUNGEON_PAWN_TRIED[0] = False',
    1,
)
if src2 != src:
    src = src2
    L("renamed travel-reset log to T278/T368")

with io.open(RUNTIME,"w",encoding="utf-8",newline="\n") as f:
    f.write(src)

# verify
on_tick_start = src.find("\ndef _on_tick(dt):")
bootstrap_start = src.find("\ndef bootstrap():")
tick_body = src[on_tick_start:bootstrap_start]
boot = src[bootstrap_start:]
L("tick_has_hook=%s" % ("update_skeleton_ai(world, pawn, dt)" in tick_body))
L("boot_has_clear=%s" % ("bootstrap T368 clear" in boot or "_clear_skeleton_ai()" in boot))
L("los_fn=%s" % ("def _has_line_of_sight(" in src))
open(OUT,"w",encoding="utf-8").write("\n".join(log)+"\n")
print("WROTE",OUT)
