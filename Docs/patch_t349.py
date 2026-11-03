# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t349_square")
t=open(p,encoding="utf-8").read()
if "T349_SQUARE_SHIELD" not in t:
    t=t.replace("T348_GOLD100","T348_GOLD100 T349_SQUARE_SHIELD",1)
t=t.replace('SHIELD1_ITEM = "SM_KayKitShield_Round"','SHIELD1_ITEM = "SM_KayKitShield_Square"',1)
t=t.replace('SHIELD1_MESH = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield_Round"','SHIELD1_MESH = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield_Square"',1)
# also treat Round as alias already owned? optional - skip
open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", 'SHIELD1_ITEM = "SM_KayKitShield_Square"' in t, "Round" not in t[t.find("SHIELD1_ITEM"):t.find("SHIELD1_ITEM")+200])
