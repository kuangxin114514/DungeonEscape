# -*- coding: utf-8 -*-
from __future__ import print_function
import shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p + ".pre_t350")
t = open(p, encoding="utf-8").read()
if "T350_DUAL_SWORD_SHIELD" not in t:
    t = t.replace("T349_SQUARE_SHIELD", "T349_SQUARE_SHIELD T350_DUAL_SWORD_SHIELD", 1)
    print("tag added")
else:
    print("tag already present")

old_path = '''def _bp_asset_path_for_leaf(bp_path_leaf):
    """Map a BP leaf / class path fragment to a Content asset path."""
    leaf = str(bp_path_leaf or "")
    if "Shield1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1"
    if "Sword1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    if "BP_KayKitKnight" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight"
    return None'''

new_path = '''def _bp_asset_path_for_leaf(bp_path_leaf):
    """Map a BP leaf / class path fragment to a Content asset path."""
    leaf = str(bp_path_leaf or "")
    # Dual leaf contains both Sword1 and Shield1 — match it FIRST.
    if "Sword1Shield1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1Shield1"
    if "Shield1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1"
    if "Sword1" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1"
    if "BP_KayKitKnight" in leaf:
        return "/Game/Characters/Player/KayKit/BP_KayKitKnight"
    return None'''

if old_path not in t:
    raise SystemExit("path helper missing")
t = t.replace(old_path, new_path, 1)
print("path helper patched")

old_pn = '''def _pn_matches_bp_leaf(pn, bp_path_leaf):
    """Exact-ish path match so BP_KayKitKnight does not hit Sword1/Shield1 variants."""
    if not pn or not bp_path_leaf:
        return False
    leaf = str(bp_path_leaf)
    if "Shield1" in leaf:
        return "BP_KayKitKnight_Shield1" in pn
    if "Sword1" in leaf:
        return "BP_KayKitKnight_Sword1" in pn
    # default knight: accept BP_KayKitKnight but reject variants
    if "BP_KayKitKnight" in leaf:
        return (
            ("BP_KayKitKnight" in pn)
            and ("BP_KayKitKnight_Sword1" not in pn)
            and ("BP_KayKitKnight_Shield1" not in pn)
        )
    return leaf in pn'''

new_pn = '''def _pn_matches_bp_leaf(pn, bp_path_leaf):
    """Exact-ish path match so BP_KayKitKnight does not hit Sword1/Shield1 variants."""
    if not pn or not bp_path_leaf:
        return False
    leaf = str(bp_path_leaf)
    # Dual first: leaf and path both contain Sword1Shield1.
    if "Sword1Shield1" in leaf:
        return "BP_KayKitKnight_Sword1Shield1" in pn
    if "Shield1" in leaf:
        return "BP_KayKitKnight_Shield1" in pn
    if "Sword1" in leaf:
        # Sword1-only: accept Sword1 but reject dual Sword1Shield1.
        return ("BP_KayKitKnight_Sword1" in pn) and ("Sword1Shield1" not in pn)
    # default knight: accept BP_KayKitKnight but reject variants
    if "BP_KayKitKnight" in leaf:
        return (
            ("BP_KayKitKnight" in pn)
            and ("BP_KayKitKnight_Sword1" not in pn)
            and ("BP_KayKitKnight_Shield1" not in pn)
            and ("Sword1Shield1" not in pn)
        )
    return leaf in pn'''

if old_pn not in t:
    raise SystemExit("pn match missing")
t = t.replace(old_pn, new_pn, 1)
print("pn match patched")

old_sword_look = '''    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    else:'''

new_sword_look = '''    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        # When both sword1+shield1 equipped, read sword from dual BP.
        if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
            tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1Shield1", prefer_mesh_substr="Sword")
            if tmpl is None:
                tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
        else:
            tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    else:'''

if old_sword_look not in t:
    raise SystemExit("sword look block missing")
t = t.replace(old_sword_look, new_sword_look, 1)
print("sword look patched")

old_shield_look = '''    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
    else:'''

new_shield_look = '''    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        # When both sword1+shield1 equipped, read shield from dual BP.
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            tmpl = _read_bp_shield_template("BP_KayKitKnight_Sword1Shield1")
            if tmpl is None:
                tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
        else:
            tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
    else:'''

if old_shield_look not in t:
    raise SystemExit("shield look block missing")
t = t.replace(old_shield_look, new_shield_look, 1)
print("shield look patched")

old_buy_s_owned = '''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        _print(world_ctx, u"\u5df2\u88c5\u5907\u52511", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
new_buy_s_owned = '''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
            _print(world_ctx, u"\u52511+\u76fe1 \u5df2\u5207\u6362", (0.5, 0.9, 1.0, 1.0), 2.0)
        else:
            _print(world_ctx, u"\u5df2\u88c5\u5907\u52511", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
if old_buy_s_owned not in t:
    raise SystemExit("buy sword owned missing")
t = t.replace(old_buy_s_owned, new_buy_s_owned, 1)
print("buy sword owned patched")

old_buy_s_ok = '''    _print(world_ctx, u"\u8d2d\u4e70\u52511\u6210\u529f\uff08-5\u91d1\u5e01\uff09", (0.4, 1.0, 0.5, 1.0), 2.5)
    _log("buy_sword1 OK")
    return True'''
new_buy_s_ok = '''    _print(world_ctx, u"\u8d2d\u4e70\u52511\u6210\u529f\uff08-5\u91d1\u5e01\uff09", (0.4, 1.0, 0.5, 1.0), 2.5)
    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        _print(world_ctx, u"\u52511+\u76fe1 \u5df2\u5207\u6362", (0.5, 0.9, 1.0, 1.0), 2.0)
    _log("buy_sword1 OK")
    return True'''
if old_buy_s_ok not in t:
    raise SystemExit("buy sword ok missing")
t = t.replace(old_buy_s_ok, new_buy_s_ok, 1)
print("buy sword ok patched")

old_buy_h_owned = '''    if SHIELD1_ITEM in inv:
        set_equipped_shield(SHIELD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        _print(world_ctx, u"\u5df2\u88c5\u5907\u76fe1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
new_buy_h_owned = '''    if SHIELD1_ITEM in inv:
        set_equipped_shield(SHIELD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            _print(world_ctx, u"\u52511+\u76fe1 \u5df2\u5207\u6362", (0.5, 0.9, 1.0, 1.0), 2.0)
        else:
            _print(world_ctx, u"\u5df2\u88c5\u5907\u76fe1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
if old_buy_h_owned not in t:
    raise SystemExit("buy shield owned missing")
t = t.replace(old_buy_h_owned, new_buy_h_owned, 1)
print("buy shield owned patched")

old_buy_h_tip = '''    _log("buy_shield1 OK")
    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        _print(world_ctx, u"\u52511+\u76fe1 \u540c\u65f6\u88c5\u5907", (0.5, 0.9, 1.0, 1.0), 2.0)
    return True'''
new_buy_h_tip = '''    _log("buy_shield1 OK")
    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        _print(world_ctx, u"\u52511+\u76fe1 \u5df2\u5207\u6362", (0.5, 0.9, 1.0, 1.0), 2.0)
    return True'''
if old_buy_h_tip not in t:
    raise SystemExit("buy shield tip missing")
t = t.replace(old_buy_h_tip, new_buy_h_tip, 1)
print("buy shield tip patched")

open(p, "w", encoding="utf-8").write(t)
compile(t, p, "exec")
print("OK wrote", p)
