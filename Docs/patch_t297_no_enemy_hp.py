# -*- coding: utf-8 -*-
"""T297: disable enemy HP bars in shop_interact_runtime.py (keep player HUD + damage)."""
from __future__ import print_function
import os
import shutil
import re

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
SRC = os.path.join(ROOT, "Content", "Python", "shop_interact_runtime.py")
LOG = os.path.join(ROOT, "Docs", "patch_t297_no_enemy_hp.txt")
out = []

def log(m):
    out.append(str(m))
    print(m)
DMG_LINES = [
    'def _list_live_enemy_actors(world):',
    '    """Collect BP_Enemy_Skeleton actors (used when HP bars are off)."""',
    '    enemies = []',
    '    if world is None:',
    '        return enemies',
    '    cls = None',
    '    for p in _ENEMY_CLS_PATHS:',
    '        try:',
    '            cls = unreal.load_class(None, p)',
    '            if cls:',
    '                break',
    '        except Exception:',
    '            cls = None',
    '    if cls:',
    '        try:',
    '            for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):',
    '                if a is not None and _uobj_alive(a):',
    '                    enemies.append(a)',
    '        except Exception:',
    '            pass',
    '    if not enemies:',
    '        try:',
    '            for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):',
    '                if _is_enemy_skeleton(a) and _uobj_alive(a):',
    '                    enemies.append(a)',
    '        except Exception:',
    '            pass',
    '    return enemies',
    '',
    '',
    'def _damage_enemies_near_attack(world, pawn):',
    '    """When player chops, lightly damage nearby skeletons (works with or without HP bars)."""',
    '    if world is None or pawn is None:',
    '        return',
    '    try:',
    '        pl = pawn.get_actor_location()',
    '    except Exception:',
    '        return',
    '    targets = []',
    '    if _ENEMY_BARS:',
    '        for _key, st in list(_ENEMY_BARS.items()):',
    '            targets.append(st)',
    '    else:',
    '        for actor in _list_live_enemy_actors(world):',
    '            st = {',
    '                "actor": actor,',
    '                "health": _ENEMY_HP_DEFAULT,',
    '                "max_health": _ENEMY_HP_DEFAULT,',
    '                "pb": None,',
    '            }',
    '            try:',
    '                _read_enemy_hp(actor, st)',
    '            except Exception:',
    '                pass',
    '            targets.append(st)',
    '    hit_any = False',
    '    for st in targets:',
    '        actor = st.get("actor")',
    '        if actor is None or (not _uobj_alive(actor)):',
    '            continue',
    '        try:',
    '            loc = actor.get_actor_location()',
    '        except Exception:',
    '            continue',
    '        if _dist(pl, loc) > 220.0:',
    '            continue',
    '        health, maxh = _read_enemy_hp(actor, st)',
    '        health = max(0.0, health - 10.0)',
    '        st["health"] = health',
    '        _write_enemy_hp(actor, health, maxh)',
    '        hit_any = True',
    '        pct = 0.0 if maxh <= 0 else health / maxh',
    '        pb = st.get("pb")',
    '        if pb is not None:',
    '            try:',
    '                pb.set_percent(pct)',
    '            except Exception:',
    '                pass',
    '        if health <= 0.0001:',
    '            _print(world, "Skeleton down", (1.0, 0.5, 0.4, 1.0), 1.5)',
    '    if hit_any:',
    '        _print(world, "Hit skeleton", (1.0, 0.6, 0.2, 1.0), 0.6)',
    '',
]
DMG_NEW = "\n" + "\n".join(DMG_LINES) + "\n"

EARLY_LINES = [
    "",
    "    # T297_NO_ENEMY_HP: do not create/project enemy bars; purge leftovers only.",
    "    if not ENEMY_HP_BARS_ENABLED:",
    "        try:",
    "            if _ENEMY_BARS:",
    "                _clear_enemy_bars(True)",
    "            else:",
    "                _ENEMY_PURGE_ACC[0] += 0.016",
    "                if _ENEMY_PURGE_ACC[0] >= 0.75:",
    "                    _ENEMY_PURGE_ACC[0] = 0.0",
    "                    _purge_enemy_viewport_widgets()",
    "        except Exception:",
    "            pass",
    "        return",
    "",
]
EARLY = "\n".join(EARLY_LINES) + "\n"

def main():
    pre = os.path.join(ROOT, "Docs", "shop_interact_runtime_pre_t297.py")
    if os.path.exists(pre):
        text = open(pre, "r", encoding="utf-8").read()
        log("restored clean base from pre_t297.py (%d chars)" % len(text))
    else:
        text = open(SRC, "r", encoding="utf-8").read()
        log("using live SRC (%d chars)" % len(text))

    bak = os.path.join(ROOT, "Docs", "shop_interact_runtime_pre_t297_patch.py")
    if not os.path.exists(bak):
        shutil.copy2(SRC if os.path.exists(SRC) else pre, bak)
        log("backup " + bak)

    old = "# T295: ENEMY_HP_BAR_X_OFFSET at file top = simple left/right knob (screen px; +right / -left).\n"
    new = old + (
        "# T297_NO_ENEMY_HP: enemy screen HP bars DISABLED (no create/project/AddToViewport).\n"
        "#       Player WBP_PlayerHealthBar + shop/gate/travel kept. Damage still works via actor scan.\n"
    )
    if old in text and "T297_NO_ENEMY_HP: enemy screen" not in text:
        text = text.replace(old, new, 1)
        log("header")
    else:
        log("header skip/missing old=%s" % (old in text))

    needle = "ENEMY_HP_BAR_MAX_SCALE = 2.50\n"
    insert = needle + (
        "# T297: set True to bring skeleton HP bars back; False = never spawn overlays.\n"
        "ENEMY_HP_BARS_ENABLED = False\n"
    )
    if "ENEMY_HP_BARS_ENABLED" not in text:
        if needle not in text:
            log("FAIL no MAX_SCALE line")
            raise SystemExit(2)
        text = text.replace(needle, insert, 1)
        log("flag")
    else:
        log("flag already")

    guard = "def ensure_enemy_health_bars(world, pc, pawn=None):\n"
    if guard not in text:
        log("FAIL no ensure fn")
        raise SystemExit(3)
    g = "    if world is None or pc is None:\n        return\n"
    idx = text.find(guard)
    gidx = text.find(g, idx)
    if gidx < 0:
        log("FAIL no guard")
        raise SystemExit(4)
    at = gidx + len(g)
    if "T297_NO_ENEMY_HP: do not create/project" not in text:
        text = text[:at] + EARLY + text[at:]
        log("early-return")
    else:
        log("early-return already")

    m = re.search(r"\ndef _damage_enemies_near_attack\(world, pawn\):", text)
    m2 = re.search(r"\ndef ensure_dungeon_pawn\(world\):", text)
    if not m or not m2 or m2.start() <= m.start():
        log("FAIL damage bounds")
        raise SystemExit(5)
    text = text[: m.start()] + DMG_NEW + text[m2.start():]
    log("damage rewritten")

    text = text.replace(
        '_log("tick registered SPLIT_WBP_V15e_T290_DIST_SCALE gen=%s" % _MY_GEN[0])',
        '_log("tick registered SPLIT_WBP_V15e_T297_NO_ENEMY_HP gen=%s" % _MY_GEN[0])',
    )
    text = text.replace(
        '_log("runtime ready SPLIT_WBP_V15e_T295_X_OFFSET")',
        '_log("runtime ready SPLIT_WBP_V15e_T297_NO_ENEMY_HP")',
    )
    log("tags")

    open(SRC, "w", encoding="utf-8", newline="\n").write(text)
    v = open(SRC, "r", encoding="utf-8").read()
    checks = [
        ("T297 tag", "T297_NO_ENEMY_HP" in v),
        ("flag False", "ENEMY_HP_BARS_ENABLED = False" in v),
        ("early", "if not ENEMY_HP_BARS_ENABLED:" in v),
        ("list_live", "def _list_live_enemy_actors" in v),
        ("player hud", "ensure_health_hud" in v and "WBP_PlayerHealthBar" in v),
        ("bootstrap", "runtime ready SPLIT_WBP_V15e_T297_NO_ENEMY_HP" in v),
        ("fns", "def ensure_dungeon_pawn" in v and "def bootstrap" in v),
    ]
    for name, ok in checks:
        log("CHECK %s=%s" % (name, ok))
        if not ok:
            raise SystemExit(6)
    log("OK " + SRC + " bytes=" + str(len(v)))
    open(LOG, "w", encoding="utf-8").write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
