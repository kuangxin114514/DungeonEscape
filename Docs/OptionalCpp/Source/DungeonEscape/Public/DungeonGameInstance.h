#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "DungeonTypes.h"
#include "DungeonGameInstance.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnDungeonGameStateChanged, EDungeonGameState, OldState, EDungeonGameState, NewState);

/**
 * Persistent run / meta flow: Hub → Dungeon → Extract/Death → Results.
 * Assign this class in Project Settings → Maps & Modes → Game Instance.
 */
UCLASS(Blueprintable, BlueprintType)
class DUNGEONESCAPE_API UDungeonGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	UDungeonGameInstance();

	UPROPERTY(BlueprintReadOnly, Category="Dungeon|Flow")
	EDungeonGameState CurrentState;

	UPROPERTY(BlueprintAssignable, Category="Dungeon|Flow")
	FOnDungeonGameStateChanged OnGameStateChanged;

	/** Soft paths — set in BP defaults or Project Settings after maps exist. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Dungeon|Maps")
	FSoftObjectPath HubMap;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Dungeon|Maps")
	FSoftObjectPath DungeonTestMap;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Dungeon|Maps")
	FSoftObjectPath ResultsMap;

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void SetGameState(EDungeonGameState NewState);

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void StartRunFromHub();

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void EnterDungeon();

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void OnPlayerDied();

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void OnExtracted();

	UFUNCTION(BlueprintCallable, Category="Dungeon|Flow")
	void FinishResultsAndReturnToHub();

protected:
	void TravelTo(const FSoftObjectPath& MapPath);
};
