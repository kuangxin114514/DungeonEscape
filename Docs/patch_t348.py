# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p + ".pre_t348_gold100")
t = open(p, encoding="utf-8").read()
if "T348_GOLD100" not in t:
    t = t.replace("T347_DUAL_SWORD_SHIELD", "T347_DUAL_SWORD_SHIELD T348_GOLD100", 1)
old = "DEFAULT_GOLD = 5"
if old not in t:
    raise SystemExit("DEFAULT_GOLD=5 not found")
t = t.replace(old, "DEFAULT_GOLD = 100", 1)
# also clear_progress uses DEFAULT_GOLD already
open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("OK", "DEFAULT_GOLD = 100" in t, "DEFAULT_GOLD = 5" not in t)
