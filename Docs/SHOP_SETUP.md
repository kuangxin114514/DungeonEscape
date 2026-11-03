# Shop Interact Setup

## Root cause (E 没反应)
Previously interact only ran in **editor slate tick** using `was_input_key_just_pressed`.
In PIE that flag is cleared at the end of the game frame, so the slate callback almost always missed **E**.
`BP_ShopInteract` was an empty stub (no Event Graph).

## Fix (2026-10-31)
- `Content/Python/shop_interact_runtime.py` v3:
  - **DE_ShopPC** Python `PlayerController` with **game-thread** `receive_tick` + E edge-detect (`is_input_key_down`)
  - Assigned to `GM_Hub.player_controller_class` every editor launch via `init_unreal.py` (not baked into the asset)
  - Slate tick kept as backup (same edge-detect + HubShop label fallback)
  - Near hint: on-screen "按 E 打开…"
- Map markers (buildings untouched): `InteractHint_*` TextRender above shops/gate
- Triggers still on Map_Hub: `ShopTrigger_*`, `GateTrigger_DungeonEntrance`
- Removed DebugExecBindings that stole Space/Enter/Esc in `DefaultInput.ini`

## Assets
- `/Game/UI/Shop/WBP_Shop`
- `/Game/Core/Interact/BP_ShopInteract` (stub; runtime does the work)
- `/Game/Core/GameFlow/GM_Hub` (Default Pawn = BP_KayKitKnight)

## How to test
1. Editor already has runtime loaded (or restart editor once so `init_unreal.py` runs)
2. Open `Map_Hub`, PIE (Alt+P)
3. Walk to a yellow "按E …" text / shop cube — screen should hint **按 E 打开…**
4. Press **E** → empty shop widget; E/Esc/关闭 to dismiss
5. At dungeon gate, **E** → "地下城入口（待接入）"

## Buildings
Hub* buildings LOCKED / unchanged.