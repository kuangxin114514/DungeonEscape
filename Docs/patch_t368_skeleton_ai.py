# -*- coding: utf-8 -*-
from __future__ import print_function
import io, os, re, shutil

RUNTIME = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
AI_BLOCK = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_t368_ai_block.py"
OUT_LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t368_skeleton_ai.txt"
lines_log = []

def L(m):
    lines_log.append(str(m))
    print(m)

with io.open(RUNTIME, "r", encoding="utf-8") as f:
    src = f.read()

if "T368_SKELETON_AI" in src and "def update_skeleton_ai(" in src:
    L("already patched — skip insert, will re-apply hooks if needed")
else:
    with io.open(AI_BLOCK, "r", encoding="utf-8") as f:
        block = f.read()
    # Ensure block is pure python (strip BOM)
    if block.startswith("\ufeff"):
        block = block[1:]
    marker = "\ndef _on_tick(dt):"
    idx = src.find(marker)
    if idx < 0:
        L("FAIL: cannot find def _on_tick")
        open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log))
        raise SystemExit(1)
    src = src[:idx] + "\n\n" + block + "\n" + src[idx:]
    L("inserted AI block before _on_tick (%d chars)" % len(block))

# Header tag
if "T368_SKELETON_AI" not in src.split("\n")[26]:
    old = "T367_SEPARATE_HANDS:"
    if old in src:
        src = src.replace(old, "T367_SEPARATE_HANDS T368_SKELETON_AI:", 1)
        L("header tag updated")
    else:
        # insert comment near top after T299 line
        needle = "# T299_HP50:"
        if needle in src and "T368_SKELETON_AI:" not in src[:2500]:
            src = src.replace(
                needle,
                "# T368_SKELETON_AI: skeleton aggro+LOS chase/run/attack; player HP damage 5.\n" + needle,
                1,
            )
            L("added T368 header comment")

# Hook into _on_tick after ensure_enemy_health_bars block
HOOK = '''    # T368_SKELETON_AI: aggro (range+LOS), chase run anim, melee attack 5 dmg
    try:
        if pawn is not None:
            update_skeleton_ai(world, pawn, dt)
            _purge_dead_skeleton_ai_keys(world)
    except Exception as e:
        _log("T368_SKELETON_AI " + str(e))
'''

if "update_skeleton_ai(world, pawn, dt)" not in src:
    anchor = '        _log("ensure_enemy_health_bars " + str(e))\n'
    if anchor not in src:
        L("FAIL: ensure_enemy_health_bars anchor missing")
        open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log))
        raise SystemExit(2)
    src = src.replace(anchor, anchor + "\n" + HOOK, 1)
    L("hooked update_skeleton_ai into _on_tick")
else:
    L("tick hook already present")

# Reset player HP + clear AI on PIE start (after clear_progress)
PIE_EXTRA = '''        try:
            _clear_skeleton_ai()
            _reset_player_hp(None)
            _log("T368_SKELETON_AI PIE reset ai+player HP")
        except Exception as e:
            _log("T368 PIE reset " + str(e))
'''
if "T368_SKELETON_AI PIE reset" not in src:
    pie_anchor = '            _log("T327 PIE start reset gold/sword")\n'
    if pie_anchor in src:
        src = src.replace(pie_anchor, pie_anchor + PIE_EXTRA, 1)
        L("PIE start resets skeleton AI + player HP")
    else:
        L("WARN: PIE anchor missing")
else:
    L("PIE reset already present")

# clear AI on bootstrap
BOOT_EXTRA = '''    try:
        _clear_skeleton_ai()
        _reset_player_hp(None)
    except Exception:
        pass
'''
if "_clear_skeleton_ai()" not in src[src.find("def bootstrap"):] if "def bootstrap" in src else True:
    pass
# Always ensure bootstrap clears — check near end of bootstrap before final log
if "bootstrap T368 clear" not in src:
    boot_anchor = "    _PENDING_ATTACK_HIT[0] = None\n"
    if boot_anchor in src:
        src = src.replace(
            boot_anchor,
            boot_anchor + "    try:\n        _clear_skeleton_ai()\n        _reset_player_hp(None)\n        _log(\"bootstrap T368 clear\")\n    except Exception:\n        pass\n",
            1,
        )
        L("bootstrap clears skeleton AI")
    else:
        L("WARN: bootstrap anchor missing")
else:
    L("bootstrap clear already present")

# Also clear AI caches on travel reset if _reset_ui_after_travel exists — optional
if "_clear_skeleton_ai()" not in src[src.find("def _reset_ui_after_travel"):src.find("def _reset_ui_after_travel")+800] if "def _reset_ui_after_travel" in src else True:
    # find function and inject near end — soft
    m = re.search(r"def _reset_ui_after_travel\([^\)]*\):\n(?:.*\n){5,40}?", src)
    # skip complex; travel already clears enemy bars and world change path can clear via bootstrap/hot reload
    L("skip travel inject (optional)")

# ensure_health_hud should pick up damaged HP — already reads Health props; we write them. Good.

# Fix: math import at module level is cleaner — AI block imports math inside _look_at_xy; OK.

with io.open(RUNTIME, "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
L("wrote runtime len=%d" % len(src))
L("has update_skeleton_ai=%s" % ("def update_skeleton_ai(" in src))
L("has _has_line_of_sight=%s" % ("def _has_line_of_sight(" in src))
L("has tick hook=%s" % ("update_skeleton_ai(world, pawn, dt)" in src))
open(OUT_LOG, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
print("WROTE", OUT_LOG)
