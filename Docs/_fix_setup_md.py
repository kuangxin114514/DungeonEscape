# -*- coding: utf-8 -*-
path = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\SHOP_SETUP.md"
text = """# Shop Interact Setup

## Assets
- `/Game/UI/Shop/WBP_Shop` (empty shell)
- `/Game/Core/Interact/BP_ShopInteract` (stub)
- `Content/Python/shop_interact_runtime.py` (PIE: near TriggerBox + press E)
- `Content/Python/init_unreal.py`

## Actors on Map_Hub (Interact folder)
- `ShopTrigger_Weapon`  (near HubShop_Weapon)
- `ShopTrigger_Armor`   (near HubShop_Armor)
- `ShopTrigger_Health`  (near HubShop_Health)
- `GateTrigger_DungeonEntrance` (near HubGate_DungeonEntrance)

## Anchor actors (untouched)
- `HubShop_Weapon` / `HubShop_Armor` / `HubShop_Health`
- `HubGate_DungeonEntrance`

## Buildings untouched: **True** (39 Hub* actors verified)

## How to test
1. Open `Map_Hub`, PIE (Alt+P)
2. Walk near a shop cube, press **E** -> empty shop WBP (title = Weapon/Armor/Health shop)
3. Press **E** or **Esc** (or Close button) to close
4. Walk to dungeon gate, press **E** -> on-screen text: dungeon entrance (pending)

## Note
Only interaction + empty shell. Full shop UI is for the user to build next.
"""
with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("ok")
