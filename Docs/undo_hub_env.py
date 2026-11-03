import unreal
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
n = 0
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubEnv_"):
        unreal.EditorLevelLibrary.destroy_actor(a)
        n += 1
# unhide floor
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() in ("Floor", "Hub_Floor"):
        a.set_actor_hidden_in_game(False)
        try:
            a.set_is_temporarily_hidden_in_editor(False)
        except Exception:
            pass
unreal.EditorLevelLibrary.save_current_level()
unreal.log("UNDO HUB ENV removed=" + str(n))
