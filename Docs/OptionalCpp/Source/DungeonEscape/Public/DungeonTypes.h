#pragma once

#include "CoreMinimal.h"
#include "DungeonTypes.generated.h"

UENUM(BlueprintType)
enum class EDungeonGameState : uint8
{
	MainMenu UMETA(DisplayName="Main Menu"),
	Hub UMETA(DisplayName="Hub"),
	InDungeon UMETA(DisplayName="In Dungeon"),
	Boss UMETA(DisplayName="Boss"),
	Extracting UMETA(DisplayName="Extracting"),
	Dead UMETA(DisplayName="Dead"),
	Results UMETA(DisplayName="Results")
};
