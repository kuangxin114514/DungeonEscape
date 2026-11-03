# DungeonEscape — Naming & Folders (UE 4.27)

## Folders (`Content/`)
| Folder | Use |
|---|---|
| Core/GameFlow | GameInstance, GameMode, state, level travel |
| Characters/Player | Playable characters / occupations |
| Characters/Enemies | Normal / elite AI |
| Characters/Boss | Boss |
| Combat | Damage, weapons, skills |
| Items | Pickups, item definitions |
| Inventory | Inventory component / widgets logic |
| UI/HUD | Health, gold, in-run HUD |
| UI/Menus | Main menu, shop, death, results |
| Maps/Hub | Respawn / town |
| Maps/Dungeon | Prefab rooms, boss, extract |
| Environments | Modular meshes from free Fab packs |
| Audio / VFX | SFX, cues, niagara/cascade |
| Data | DataTables, enums as data |

## Blueprint / Asset prefixes
- BP_ Actor / Pawn / Character blueprints
- WBP_ UMG widgets
- GM_ GameMode
- GI_ GameInstance
- GS_ GameState
- AC_ Actor Component
- DT_ DataTable
- DA_ DataAsset
- ENUM_ / E_ Enums (or C++ EDungeon...)
- IF_ Interface
- T_ Texture, M_ Material, MI_ Material Instance
- SK_ Skeletal mesh, SM_ Static mesh
- A_ Animation sequence, ABP_ Anim blueprint
- LS_ Level sequence (if any)

## Examples
- `GI_DungeonGame` — game flow / persistent run data
- `GM_Hub`, `GM_Dungeon`
- `BP_PlayerMelee`, `BP_PlayerCaster`
- `BP_EnemyGrunt`, `BP_BossGatekeeper`
- `WBP_Inventory`, `WBP_Results`
- `DT_Items`, `DT_Weapons`

## Maps
- `Map_Hub` — respawn / shop entry
- `Map_Dungeon_Room_01` … `06`
- `Map_Dungeon_Boss`
- `Map_Dungeon_Extract`
