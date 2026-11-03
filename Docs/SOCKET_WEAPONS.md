# KayKit socket weapons (Round_Shield + 1H_Sword)

## Match Persona preview
- Right hand: **1H_Sword** on `handslot_r`
- Left hand: **Round_Shield** on `handslot_l` (NOT Badge_Shield)

## Pipeline
1. `Docs/export_knight_socket_weapons.py` (Blender) skins sword/shield to handslot bones on body FBX, and exports bone-local SM FBXs.
2. `Docs/socket_kaykit_weapons.py` (UE Python) reimports SK + SM_KayKitSword/SM_KayKitShield, applies M_KayKitKnight, sets BP mesh Idle / Loc Z=-90 Rot Z=-90 Scale 0.75.

## Note on BP components
BP_KayKitKnight has no SimpleConstructionScript (inherited Character Mesh only). UE4.27 Python cannot create SCS nodes here (`SimpleConstructionScript` protected; `BlueprintEditorLibrary` unavailable in-editor). Visual match is via **skinned weapons on SK_KayKitKnight**.

## Verify
Close/reopen `BP_KayKitKnight` Viewport — sword in right hand, round heater shield in left.
