# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
bak = p + ".pre_t343_kill_gold"
shutil.copy2(p, bak)
t = open(p, encoding="utf-8").read()

if "KILL_GOLD_REWARD" not in t:
    t = t.replace(
        "SWORD1_ATTACK_DAMAGE = 20.0   # sword1 equipped",
        "SWORD1_ATTACK_DAMAGE = 20.0   # sword1 equipped\n"
        "KILL_GOLD_REWARD = 1          # gold per skeleton kill",
        1,
    )

old = '''        if health <= 0.0001:
            ok = _destroy_enemy_actor(actor)
            _print(world, "Skeleton died", (1.0, 0.4, 0.3, 1.0), 1.5)
            _log("T299 destroy ok=%s" % ok)'''

new = '''        if health <= 0.0001:
            ok = _destroy_enemy_actor(actor)
            g = add_gold(KILL_GOLD_REWARD, world)
            _print(world, u"+%d Gold  (%d)" % (int(KILL_GOLD_REWARD), int(g)), (1.0, 0.85, 0.2, 1.0), 1.5)
            _print(world, "Skeleton died", (1.0, 0.4, 0.3, 1.0), 1.5)
            _log("T343 kill gold+=%s now=%s destroy=%s" % (KILL_GOLD_REWARD, g, ok))'''

if old not in t:
    raise SystemExit("death block not found")
t = t.replace(old, new, 1)

if "T343_KILL_GOLD" not in t:
    t = t.replace("T341_SWORD1_DMG20", "T341_SWORD1_DMG20 T343_KILL_GOLD", 1)

open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("OK", "KILL_GOLD_REWARD" in t, "T343 kill gold" in t, "T343_KILL_GOLD" in t)
