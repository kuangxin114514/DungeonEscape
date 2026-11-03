import unreal
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GROUND_Z = 0.0
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not a.get_actor_label().startswith("HubMed_"):
        continue
    r = a.get_actor_rotation()
    a.set_actor_rotation(unreal.Rotator(r.pitch + 90.0, r.yaw, r.roll), False)
    origin, extent = a.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = a.get_actor_location()
    a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + (GROUND_Z - bottom)), False, True)
    n += 1
unreal.EditorLevelLibrary.save_current_level()
unreal.log("UNDO ROTATE HUB n=" + str(n))
