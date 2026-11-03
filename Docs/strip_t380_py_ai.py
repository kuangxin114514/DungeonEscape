# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py")
text = p.read_text(encoding="utf-8")

begin = text.find("# ===== BEGIN T368_SKELETON_AI =====")
end = text.find("# ===== END T368_SKELETON_AI =====")
if begin < 0 or end < 0:
    raise SystemExit("T368 markers missing")
end = end + len("# ===== END T368_SKELETON_AI =====")

hp_block = r'''
# ===== BEGIN T380_PLAYER_HP (kept; skeleton chase AI removed) =====
# T380_REMOVE_PY_AI: Python skeleton aggro/chase/attack deleted.
# Player HP helpers remain so Blueprint (or other) damage + HUD stay consistent.
PLAYER_MAX_HEALTH_DEFAULT = 100.0
_PLAYER_HP_CACHE = {"health": PLAYER_MAX_HEALTH_DEFAULT, "max_health": PLAYER_MAX_HEALTH_DEFAULT, "dead": False}


def _ensure_player_hp(pawn):
    """Make sure player has Health/MaxHealth (default 100). Returns (health, maxh)."""
    if pawn is None:
        return float(_PLAYER_HP_CACHE["health"]), float(_PLAYER_HP_CACHE["max_health"])
    maxh = _float_prop(pawn, ("MaxHealth", "max_health", "MaxHP", "MaxHp"), None)
    health = _float_prop(pawn, ("Health", "health", "HP", "Hp"), None)
    if maxh is None or maxh <= 0.0001:
        maxh = float(_PLAYER_HP_CACHE.get("max_health", PLAYER_MAX_HEALTH_DEFAULT) or PLAYER_MAX_HEALTH_DEFAULT)
    if health is None:
        health = float(_PLAYER_HP_CACHE.get("health", maxh))
    if health > maxh:
        health = maxh
    _PLAYER_HP_CACHE["health"] = float(health)
    _PLAYER_HP_CACHE["max_health"] = float(maxh)
    for name, val in (("Health", health), ("MaxHealth", maxh), ("health", health), ("max_health", maxh)):
        try:
            pawn.set_editor_property(name, float(val))
        except Exception:
            try:
                setattr(pawn, name, float(val))
            except Exception:
                pass
    return float(health), float(maxh)


def _set_player_hp(pawn, health, maxh=None):
    if maxh is None:
        maxh = float(_PLAYER_HP_CACHE.get("max_health", PLAYER_MAX_HEALTH_DEFAULT))
    health = max(0.0, float(health))
    maxh = float(maxh) if float(maxh) > 0.0001 else PLAYER_MAX_HEALTH_DEFAULT
    if health > maxh:
        health = maxh
    _PLAYER_HP_CACHE["health"] = health
    _PLAYER_HP_CACHE["max_health"] = maxh
    if pawn is not None:
        for name, val in (("Health", health), ("MaxHealth", maxh), ("health", health), ("max_health", maxh)):
            try:
                pawn.set_editor_property(name, float(val))
            except Exception:
                try:
                    setattr(pawn, name, float(val))
                except Exception:
                    pass
    return health, maxh


def _reset_player_hp(pawn=None):
    _PLAYER_HP_CACHE["health"] = PLAYER_MAX_HEALTH_DEFAULT
    _PLAYER_HP_CACHE["max_health"] = PLAYER_MAX_HEALTH_DEFAULT
    _PLAYER_HP_CACHE["dead"] = False
    if pawn is not None:
        _set_player_hp(pawn, PLAYER_MAX_HEALTH_DEFAULT, PLAYER_MAX_HEALTH_DEFAULT)


def _damage_player(world, pawn, amount):
    """Apply damage to player HP + print; mark dead at 0. Callable from future BP bridge if needed."""
    if pawn is None or _PLAYER_HP_CACHE.get("dead"):
        return
    health, maxh = _ensure_player_hp(pawn)
    health = max(0.0, health - float(amount))
    _set_player_hp(pawn, health, maxh)
    _print(world, u"\u88ab\u51fb\u4e2d -%d  HP %.0f/%.0f" % (int(amount), health, maxh), (1.0, 0.35, 0.3, 1.0), 1.2)
    _log("T380_PLAYER_HP hit -%s HP=%.0f/%.0f" % (amount, health, maxh))
    if health <= 0.0001:
        _PLAYER_HP_CACHE["dead"] = True
        _print(world, u"\u4f60\u5012\u4e0b\u4e86\uff08HP 0\uff09\u3002\u505c\u6389 PIE \u518d\u8fdb\u53ef\u91cd\u751f", (1.0, 0.2, 0.2, 1.0), 4.0)
        _log("T380_PLAYER_HP player dead")


def _sync_player_hp_cache_from_pawn(pawn):
    """Keep Python cache aligned if Blueprint AI writes Health on the pawn."""
    if pawn is None:
        return
    try:
        health, maxh = _ensure_player_hp(pawn)
        if health <= 0.0001:
            _PLAYER_HP_CACHE["dead"] = True
        else:
            if _PLAYER_HP_CACHE.get("dead") and health > 0.0001:
                _PLAYER_HP_CACHE["dead"] = False
    except Exception:
        pass

# ===== END T380_PLAYER_HP =====
'''

text2 = text[:begin] + hp_block + text[end:]

old_tick = """    # T368_SKELETON_AI: aggro (range+LOS), chase run anim, melee attack 5 dmg
    try:
        if pawn is not None:
            update_skeleton_ai(world, pawn, dt)
            _purge_dead_skeleton_ai_keys(world)
    except Exception as e:
        _log(\"T368_SKELETON_AI \" + str(e))
"""
new_tick = """    # T380_REMOVE_PY_AI: no Python skeleton chase. Sync HP if BP AI wrote Health.
    try:
        if pawn is not None:
            _sync_player_hp_cache_from_pawn(pawn)
    except Exception as e:
        _log(\"T380_PLAYER_HP sync \" + str(e))
"""
if old_tick not in text2:
    m = re.search(
        r"\n    # T368_SKELETON_AI:.*?\n    except Exception as e:\n        _log\(\"T368_SKELETON_AI \" \+ str\(e\)\)\n",
        text2,
        re.S,
    )
    if not m:
        raise SystemExit("tick block not found")
    text2 = text2[: m.start()] + "\n" + new_tick + text2[m.end() :]
else:
    text2 = text2.replace(old_tick, new_tick)

repls = [
(
"""    try:
        _clear_skeleton_ai()
        _reset_player_hp(None)
        _log(\"T278/T368 reset clear skeleton AI\")
    except Exception:
        pass
""",
"""    try:
        _reset_player_hp(None)
        _log(\"T380 reset player HP (py skeleton AI removed)\")
    except Exception:
        pass
""",
),
(
"""        try:
            _clear_skeleton_ai()
            _reset_player_hp(None)
            _log(\"T368_SKELETON_AI PIE reset ai+player HP\")
        except Exception as e:
            _log(\"T368 PIE reset \" + str(e))
""",
"""        try:
            _reset_player_hp(None)
            _log(\"T380 PIE reset player HP\")
        except Exception as e:
            _log(\"T380 PIE reset \" + str(e))
""",
),
(
"""    try:
        _clear_skeleton_ai()
        _reset_player_hp(None)
        _log(\"bootstrap T368 clear\")
    except Exception:
        pass
""",
"""    try:
        _reset_player_hp(None)
        _log(\"bootstrap T380 player HP clear\")
    except Exception:
        pass
""",
),
]
for a, b in repls:
    if a not in text2:
        print("WARN missing repl block:\n", a[:80])
    else:
        text2 = text2.replace(a, b)

if "T347_DUAL" in text2 and "T380_REMOVE_PY_AI" not in text2.split("T347_DUAL", 1)[0] + "T347_DUAL":
    text2 = text2.replace("T347_DUAL", "T347_DUAL T380_REMOVE_PY_AI", 1)

compile(text2, str(p), "exec")
p.write_text(text2, encoding="utf-8")
print("WROTE", p, "len", len(text2))
for name in ("_damage_player", "update_skeleton_ai", "_clear_skeleton_ai", "T380_REMOVE_PY_AI", "_sync_player_hp_cache_from_pawn", "SKELETON_FACE_YAW"):
    print(name, text2.count(name))
