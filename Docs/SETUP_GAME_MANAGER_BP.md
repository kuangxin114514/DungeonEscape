# Create Game Manager in Editor (Blueprint)

This PC has no Visual Studio, so the flow skeleton is Blueprint-first.
C++ sources are saved under `Docs/OptionalCpp/Source` if you install VS later.

## One-time setup (5 minutes)

1. Open `DungeonEscape.uproject` with UE 4.27.
2. In Content Browser go to `Content/Core/GameFlow`.
3. Right-click → Blueprint Class → search **Game Instance** → name it `GI_DungeonGame`.
4. Open `GI_DungeonGame` and add:
   - Variable `CurrentState` (Byte or a Blueprint Enum `E_DungeonGameState`)
   - Functions: `StartRunFromHub`, `EnterDungeon`, `OnPlayerDied`, `OnExtracted`, `FinishResultsAndReturnToHub`
   - Each function: set state, then **Open Level** to the matching map.
5. Create Blueprint Enum `E_DungeonGameState`: MainMenu, Hub, InDungeon, Boss, Extracting, Dead, Results.
6. Create Blueprint Class from **Game Mode Base**:
   - `GM_Hub`
   - `GM_Dungeon`
7. Project Settings → Maps & Modes:
   - Game Instance: `GI_DungeonGame`
   - Default Modes / Default Map: point Hub map when ready (for now keep ThirdPersonExampleMap).

## State flow to wire

Hub --EnterDungeon--> InDungeon --(boss room)--> Boss --extract--> Results --> Hub
InDungeon/Boss --death--> Dead --> Hub (drop run loot later)

## Maps to add next

- `Maps/Hub/Map_Hub`
- `Maps/Dungeon/Map_Dungeon_Test`
