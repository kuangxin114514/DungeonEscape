#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "DungeonGameMode.generated.h"

/** Base GameMode for Hub / Dungeon — specialize in Blueprints (GM_Hub, GM_Dungeon). */
UCLASS(Blueprintable)
class DUNGEONESCAPE_API ADungeonGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ADungeonGameMode();
};
