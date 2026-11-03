import unreal
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GROUND_Z = 0.0
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not a.get_actor_label().startswith("HubMed_"):
        continue
    r = a.get_actor_rotation()
    # 向后旋转 90°：绕本地 X 再加 Pitch -90（或 Roll），用户说的“向后”按 Pitch -90
    new_r = unreal.Rotator(r.pitch - 90.0, r.yaw, r.roll)
    a.set_actor_rotation(new_r, False)
    # 重新贴地
    origin, extent = a.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = a.get_actor_location()
    a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + (GROUND_Z - bottom)), False, True)
    n += 1
    unreal.log("rotated " + a.get_actor_label())
unreal.EditorLevelLibrary.save_current_level()
unreal.log("ROTATE HUB DONE n=" + str(n))
