# -*- coding: utf-8 -*-
import ast
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
if "SWORD1_ATTACK_DAMAGE" not in t:
    t=t.replace(
        "ATTACK_DAMAGE = 10.0          # HP removed per successful LMB hit",
        "ATTACK_DAMAGE = 10.0          # HP removed per successful LMB hit (default sword)\n"
        "SWORD1_ATTACK_DAMAGE = 20.0   # equipped SM_KayKitSword_2H / sword1",
        1,
    )
# helper for current damage
if "def current_attack_damage" not in t:
    t=t.replace(
        "def _damage_enemies_near_attack(world, pawn):",
        "def current_attack_damage(world_ctx=None):\n"
        "    ensure_player_meta(world_ctx)\n"
        "    if get_equipped_sword(world_ctx) == SWORD1_ITEM:\n"
        "        return float(SWORD1_ATTACK_DAMAGE)\n"
        "    return float(ATTACK_DAMAGE)\n\n\n"
        "def _damage_enemies_near_attack(world, pawn):",
        1,
    )
old='''        health = max(0.0, health - float(ATTACK_DAMAGE))'''
# may appear once
if "current_attack_damage(" not in t[t.find("def _damage_enemies_near_attack"):t.find("def _damage_enemies_near_attack")+2500]:
    # replace damage application block more carefully
    chunk_a=t.find("def _damage_enemies_near_attack")
    chunk_b=t.find("\ndef ", chunk_a+1)
    chunk=t[chunk_a:chunk_b]
    if "dmg = current_attack_damage" not in chunk:
        chunk2=chunk.replace(
            "health = max(0.0, health - float(ATTACK_DAMAGE))",
            "dmg = current_attack_damage(world)\n"
            "        health = max(0.0, health - float(dmg))",
            1,
        )
        # fix print line
        chunk2=chunk2.replace(
            'world, "Hit -%d  HP %.0f" % (int(ATTACK_DAMAGE), health)',
            'world, "Hit -%d  HP %.0f" % (int(dmg), health)',
        )
        # docstring
        chunk2=chunk2.replace(
            "nearby skeletons lose ATTACK_DAMAGE HP",
            "nearby skeletons lose current_attack_damage() HP",
        )
        t=t[:chunk_a]+chunk2+t[chunk_b:]
if "T341_SWORD1_DMG20" not in t:
    t=t.replace("T340_APPLY_BP_LOOK","T340_APPLY_BP_LOOK T341_SWORD1_DMG20",1)
open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", "SWORD1_ATTACK_DAMAGE = 20" in t, "current_attack_damage" in t)
