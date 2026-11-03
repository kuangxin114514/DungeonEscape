# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p + ".pre_t347_dual")
t = open(p, encoding="utf-8").read()
if "T347_DUAL_SWORD_SHIELD" not in t:
    t = t.replace("T346_SHIELD1", "T346_SHIELD1 T347_DUAL_SWORD_SHIELD", 1)

old_sword_filter = '''        sname = sm.get_name() if sm else ""
        if sname == "SM_KayKitShield" or "StaticMesh1" in nm:
            continue
        if ("Sword" in sname) or nm.startswith("StaticMesh") or ("KayKitSword" in sname):
            out.append(c)
    return out


def apply_equipped_sword_look(pawn, world_ctx=None):'''

new_sword_filter = '''        sname = sm.get_name() if sm else ""
        # Never touch shield slot (StaticMesh1 / any Shield mesh), so sword1+shield1 can coexist.
        if ("StaticMesh1" in nm) or ("Shield" in sname) or ("shield" in nm.lower()):
            continue
        if ("Sword" in sname) or (nm == "StaticMesh") or nm.startswith("StaticMesh_GEN") or ("KayKitSword" in sname):
            out.append(c)
    return out


def apply_equipped_gear_look(pawn, world_ctx=None):
    """Apply equipped sword AND shield independently (both can show at once)."""
    if pawn is None:
        return False
    ok_s = False
    ok_h = False
    try:
        ok_s = apply_equipped_sword_look(pawn, world_ctx)
    except Exception as e:
        _log("apply gear sword " + str(e))
    try:
        ok_h = apply_equipped_shield_look(pawn, world_ctx)
    except Exception as e:
        _log("apply gear shield " + str(e))
    return bool(ok_s or ok_h)


def apply_equipped_sword_look(pawn, world_ctx=None):'''

if old_sword_filter not in t:
    raise SystemExit("sword filter block missing")
t = t.replace(old_sword_filter, new_sword_filter, 1)

# ensure_equipped uses apply_equipped_gear_look
old_ens = '''    ok_s = apply_equipped_sword_look(pawn, world_ctx)
    ok_h = False
    try:
        ok_h = apply_equipped_shield_look(pawn, world_ctx)
    except Exception as e:
        _log("ensure shield look " + str(e))
    return bool(ok_s or ok_h)'''
new_ens = '''    return apply_equipped_gear_look(pawn, world_ctx)'''
if old_ens not in t:
    raise SystemExit("ensure block missing")
t = t.replace(old_ens, new_ens, 1)

# buy_sword1: after apply sword, also refresh shield; and on already-owned path too
old_buy_s_owned = '''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        apply_equipped_sword_look(pawn, world_ctx)
        _print(world_ctx, u"已装备剑1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
new_buy_s_owned = '''    if SWORD1_ITEM in inv:
        set_equipped_sword(SWORD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        _print(world_ctx, u"已装备剑1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
if old_buy_s_owned not in t:
    raise SystemExit("buy sword owned missing")
t = t.replace(old_buy_s_owned, new_buy_s_owned, 1)

old_buy_s_new = '''    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    apply_equipped_sword_look(pawn, world_ctx)'''
new_buy_s_new = '''    add_item(SWORD1_ITEM, world_ctx)
    set_equipped_sword(SWORD1_ITEM, world_ctx)
    apply_equipped_gear_look(pawn, world_ctx)'''
if old_buy_s_new not in t:
    raise SystemExit("buy sword new missing")
t = t.replace(old_buy_s_new, new_buy_s_new, 1)

old_buy_h_owned = '''    if SHIELD1_ITEM in inv:
        set_equipped_shield(SHIELD1_ITEM, world_ctx)
        apply_equipped_shield_look(pawn, world_ctx)
        _print(world_ctx, u"已装备盾1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
new_buy_h_owned = '''    if SHIELD1_ITEM in inv:
        set_equipped_shield(SHIELD1_ITEM, world_ctx)
        apply_equipped_gear_look(pawn, world_ctx)
        _print(world_ctx, u"已装备盾1", (0.4, 1.0, 0.5, 1.0), 2.0)
        return True'''
if old_buy_h_owned not in t:
    raise SystemExit("buy shield owned missing")
t = t.replace(old_buy_h_owned, new_buy_h_owned, 1)

old_buy_h_new = '''    add_item(SHIELD1_ITEM, world_ctx)
    set_equipped_shield(SHIELD1_ITEM, world_ctx)
    apply_equipped_shield_look(pawn, world_ctx)'''
new_buy_h_new = '''    add_item(SHIELD1_ITEM, world_ctx)
    set_equipped_shield(SHIELD1_ITEM, world_ctx)
    apply_equipped_gear_look(pawn, world_ctx)'''
if old_buy_h_new not in t:
    raise SystemExit("buy shield new missing")
t = t.replace(old_buy_h_new, new_buy_h_new, 1)

# after successful shield buy message, if sword1 also equipped hint
old_h_ok = '''    _print(world_ctx, u"购买盾1成功（-5金币）", (0.4, 1.0, 0.5, 1.0), 2.5)
    _log("buy_shield1 OK")
    return True'''
# encoding may be broken in file - find by log line
idx = t.find('_log("buy_shield1 OK")')
if idx < 0:
    raise SystemExit("buy_shield1 OK log missing")
# find the print line before it
snip = t[idx-200:idx+80]
# replace just the log area to add dual message
t = t.replace(
    '_log("buy_shield1 OK")\n    return True',
    '_log("buy_shield1 OK")\n'
    '    if get_equipped_sword(world_ctx) == SWORD1_ITEM:\n'
    '        _print(world_ctx, u"剑1+盾1 同时装备", (0.5, 0.9, 1.0, 1.0), 2.0)\n'
    '    return True',
    1,
)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", "apply_equipped_gear_look" in t, "T347_DUAL_SWORD_SHIELD" in t)
