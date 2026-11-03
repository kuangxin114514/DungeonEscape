# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t367")
t=open(p,encoding="utf-8").read()
if "T367_SEPARATE_HANDS" not in t:
    t=t.replace("T350_DUAL_SWORD_SHIELD","T350_DUAL_SWORD_SHIELD T367_SEPARATE_HANDS",1)

old_sword='''    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        # When both sword1+shield1 equipped, read sword from dual BP.
        if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
            tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1Shield1", prefer_mesh_substr="Sword")
            if tmpl is None:
                tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
        else:
            tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    else:'''

new_sword='''    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        # Always from Sword1 BP (right hand); shield never overrides this.
        tmpl = _read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    else:'''

old_shield='''    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        # When both sword1+shield1 equipped, read shield from dual BP.
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            tmpl = _read_bp_shield_template("BP_KayKitKnight_Sword1Shield1")
            if tmpl is None:
                tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
        else:
            tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
    else:'''

new_shield='''    if get_equipped_shield(world_ctx) == SHIELD1_ITEM:
        # Always from Shield1 BP (left hand); sword never overrides this.
        tmpl = _read_bp_shield_template("BP_KayKitKnight_Shield1")
    else:'''

if old_sword not in t:
    raise SystemExit("sword block missing")
if old_shield not in t:
    raise SystemExit("shield block missing")
t=t.replace(old_sword, new_sword, 1)
t=t.replace(old_shield, new_shield, 1)

# tip text: dual switch -> both equipped (keep unicode escapes style via explicit unicode)
# Fix garbled tips by rewriting buy tip branches with clean unicode
import re
# Replace any print lines that mention dual switch messily - rewrite buy_sword1 and buy_shield1 tip sections via markers

# Simpler: replace known dual tip patterns if present as mojibake or correct
for bad in [
    u'剑1+盾1 已切换',
]:
    t=t.replace(bad, u'剑1+盾1 同时装备')

# Also docstring tweak on apply_equipped_gear_look
t=t.replace(
    '"""Apply equipped sword AND shield independently (both can show at once)."""',
    '"""Apply sword (right) and shield (left) from separate BPs; both can show at once."""',
    1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK T367")
print("dual sword branch gone", "Sword1Shield1" not in t[t.find("def apply_equipped_sword_look"):t.find("def ensure_equipped_pawn_class")])
print("dual shield branch gone", "Sword1Shield1" not in t[t.find("def apply_equipped_shield_look"):t.find("def buy_shield1")])
