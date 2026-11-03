# GI Gold / Inventory + Map_Dungeon2 (T309)

## Game Instance
- Asset: `/Game/Core/GameFlow/GI_DungeonGame` (already project Game Instance)
- Project Settings → Maps & Modes → Game Instance Class = `GI_DungeonGame`
- Confirmed in `Config/DefaultEngine.ini`:
  `GameInstanceClass=/Game/Core/GameFlow/GI_DungeonGame.GI_DungeonGame_C`

UE4.27 Python cannot add Blueprint variables automatically. Persistence for the course is in
`Content/Python/shop_interact_runtime.py`:

- Default Gold = 5
- Inventory = string list (item names)
- Helpers: `get_gold`, `add_gold`, `spend_gold`, `get_inventory`, `add_item`, `clear_progress`
- Saved to `Saved/PlayerMeta.json` (survives Play stop; clear with `clear_progress` for new save)
- Survives OpenLevel / character swap (not stored on the knight)

### Optional Blueprint vars (manual, 1 minute)
Open `GI_DungeonGame` → add:
1. `Gold` (Integer, default 5)
2. `Inventory` (String Array)
Python helpers will sync to these when present.
Knight / shops: `Get Game Instance` → Cast to `GI_DungeonGame` → get/set Gold & Inventory.

## Map_Dungeon2
- Path: `/Game/Maps/Dungeon/Map_Dungeon2`
- Blank floor + light + PlayerStart + marker
- World GameMode: `GM_Dungeon` with Default Pawn `BP_KayKitKnight`
- Map_Hub was NOT opened/edited

## Dungeon1 exit E
- Behind skeleton / DungeonExit: OpenLevel → `Map_Dungeon2` (was Map_Hub)
- Hint: 按 E 进入2层
- `return_to_hub` still exists for true hub returns later

## How to verify
1. Stop PIE if running, Play `Map_Dungeon1`
2. Walk to exit behind skeleton, press E → should load Map_Dungeon2 and spawn as knight
3. In Output Log look for `ShopInteract: OpenLevel /Game/Maps/Dungeon/Map_Dungeon2`
4. Gold: after Play, `Saved/PlayerMeta.json` should show `"gold": 5`