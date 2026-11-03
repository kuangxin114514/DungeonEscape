import unreal
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GROUND_Z = 0.0
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
# Player / character facing reference
ref = unreal.Vector(0, 0, 0)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        ref = a.get_actor_location()
        break
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not a.get_actor_label().startswith("HubMed_"):
        continue
    loc = a.get_actor_location()
    r = a.get_actor_rotation()
    # 竖着转 90° = Yaw +90（绕竖直轴）
    a.set_actor_rotation(unreal.Rotator(r.pitch, r.yaw + 90.0, r.roll), False)
    origin, extent = a.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc2 = a.get_actor_location()
    a.set_actor_location(unreal.Vector(loc2.x, loc2.y, loc2.z + (GROUND_Z - bottom)), False, True)
    n += 1
    unreal.log("yaw90 " + a.get_actor_label())
unreal.EditorLevelLibrary.save_current_level()
unreal.log("YAW HUB DONE n=" + str(n))
