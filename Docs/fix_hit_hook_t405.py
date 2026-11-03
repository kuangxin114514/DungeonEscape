# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
raw = io.open(p, "r", encoding="utf-8").read()
pat = re.compile(
    r"[ \t]*if health > 0\.0001:\r?\n"
    r"[ \t]*try:\r?\n"
    r"[ \t]*import skeleton_engine_ai as _skai\r?\n"
    r"[ \t]*_skai\.notify_hit\(actor\)\r?\n"
    r"[ \t]*except Exception as e:\r?\n"
    r"[ \t]*_log\(\"skel hit anim \" \+ str\(e\)\)\r?\n"
    r"[ \t]*if health <= 0\.0001:",
    re.M,
)
repl = (
    "        if health > 0.0001:\n"
    "            try:\n"
    "                import skeleton_engine_ai as _skai\n"
    "                _skai.notify_hit(actor)\n"
    "            except Exception as e:\n"
    "                _log(\"skel hit anim \" + str(e))\n"
    "        if health <= 0.0001:"
)
raw2, n = pat.subn(repl, raw, count=1)
print("fix_n", n)
if n == 0 and "notify_hit" not in raw:
    needle = '        _print(world, "Hit -%d  HP %.0f" % (int(dmg), health), (1.0, 0.6, 0.2, 1.0), 0.8)\n        if health <= 0.0001:'
    insert = (
        '        _print(world, "Hit -%d  HP %.0f" % (int(dmg), health), (1.0, 0.6, 0.2, 1.0), 0.8)\n'
        "        if health > 0.0001:\n"
        "            try:\n"
        "                import skeleton_engine_ai as _skai\n"
        "                _skai.notify_hit(actor)\n"
        "            except Exception as e:\n"
        '                _log("skel hit anim " + str(e))\n'
        "        if health <= 0.0001:"
    )
    if needle in raw2.replace("\r\n", "\n"):
        raw2 = raw2.replace("\r\n", "\n").replace(needle, insert, 1)
        print("inserted")
    else:
        print("NEEDLE_MISSING")
if "\r\n" in raw:
    raw2 = raw2.replace("\r\n", "\n").replace("\n", "\r\n")
io.open(p, "w", encoding="utf-8", newline="").write(raw2)
src = io.open(p, encoding="utf-8").read()
compile(src, p, "exec")
print("syntax_ok")
for i, line in enumerate(src.splitlines(), 1):
    if 3938 <= i <= 3955:
        print("%d:%r" % (i, line))
