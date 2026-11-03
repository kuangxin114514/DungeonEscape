#include "DungeonGameInstance.h"
#include "Kismet/GameplayStatics.h"

UDungeonGameInstance::UDungeonGameInstance()
{
	CurrentState = EDungeonGameState::MainMenu;
}

void UDungeonGameInstance::SetGameState(EDungeonGameState NewState)
{
	if (CurrentState == NewState)
	{
		return;
	}
	const EDungeonGameState Old = CurrentState;
	CurrentState = NewState;
	OnGameStateChanged.Broadcast(Old, NewState);
}

void UDungeonGameInstance::TravelTo(const FSoftObjectPath& MapPath)
{
	if (!MapPath.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("DungeonGameInstance: map path not set for state %d"), (int32)CurrentState);
		return;
	}
	UGameplayStatics::OpenLevel(this, FName(*MapPath.GetLongPackageName()));
}

void UDungeonGameInstance::StartRunFromHub()
{
	SetGameState(EDungeonGameState::Hub);
	TravelTo(HubMap);
}

void UDungeonGameInstance::EnterDungeon()
{
	SetGameState(EDungeonGameState::InDungeon);
	TravelTo(DungeonTestMap);
}

void UDungeonGameInstance::OnPlayerDied()
{
	SetGameState(EDungeonGameState::Dead);
	// TODO: drop run inventory / lose run gold — Inventory owner hooks here
	SetGameState(EDungeonGameState::Hub);
	TravelTo(HubMap);
}

void UDungeonGameInstance::OnExtracted()
{
	SetGameState(EDungeonGameState::Extracting);
	SetGameState(EDungeonGameState::Results);
	if (ResultsMap.IsValid())
	{
		TravelTo(ResultsMap);
	}
	else
	{
		// Fallback: results UI can live on Hub until a dedicated map exists
		TravelTo(HubMap);
	}
}

void UDungeonGameInstance::FinishResultsAndReturnToHub()
{
	SetGameState(EDungeonGameState::Hub);
	TravelTo(HubMap);
}
