# Game Flow Skeleton

States (C++ enum `EDungeonGameState`):
1. MainMenu
2. Hub
3. InDungeon
4. Boss
5. Extracting
6. Dead
7. Results

Travel:
MainMenu → Hub → InDungeon (room sequence) → Boss → Extract portal → Results → Hub
Any time InDungeon/Boss: death → Dead → (drop run loot) → Hub

`UDungeonGameInstance` owns current state + helpers:
- StartRun()
- EnterDungeon()
- OnPlayerDied()
- OnExtracted()
- ShowResultsAndReturnToHub()

Maps (to create in editor next):
- /Game/Maps/Hub/Map_Hub
- /Game/Maps/Dungeon/Map_Dungeon_Test (single test room first)
