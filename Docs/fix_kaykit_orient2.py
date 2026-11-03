import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
LAYOUT = [
    ("building_well_blue",        0.0,     0.0,    0.0),
    ("building_church_blue",   2200.0, -1600.0,    0.0),
    ("building_tavern_blue",  -2000.0, -1600.0,   90.0),
    ("building_market_blue",      0.0, -2600.0,    0.0),
    ("building_blacksmith_blue", 2600.0,  400.0,  -90.0),
    ("building_barracks_blue", -2600.0,  400.0,   90.0),
    ("building_home_A_blue",   1800.0, 2200.0,  180.0),
    ("building_home_B_blue",  -1600.0, 2300.0,  180.0),
    ("building_tower_A_blue",  3400.0, -3000.0,  45.0),
    ("building_castle_blue",      0.0, 3600.0,  180.0),
    ("building_windmill_blue",-3400.0, -800.0,   30.0),
]

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubKay_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

ground_z = -20.0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in ("Hub_Floor", "Floor", "HubGround_Plane") or "Floor" in lab:
        ground_z = a.get_actor_location().z
        break

mat = unreal.EditorAssetLibrary.load_asset(DEST + "/M_KayKitMedieval") or unreal.EditorAssetLibrary.load_asset(DEST + "/hexagons_medieval")

# log mesh local tall axis first
for key in ("building_home_A_blue", "building_church_blue", "building_castle_blue", "building_market_blue", "building_tavern_blue"):
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        continue
    bb = mesh.get_bounding_box()
    sx = abs(bb.max.x - bb.min.x)
    sy = abs(bb.max.y - bb.min.y)
    sz = abs(bb.max.z - bb.min.z)
    unreal.log("mesh %s sx=%.1f sy=%.1f sz=%.1f (expect sy tall for Y-up)" % (key, sx, sy, sz))

placed = 0
for key, x, y, yaw in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        continue
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass
    # 1) pitch only so local Y -> world Z
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(float(x), float(y), float(ground_z)),
        unreal.Rotator(-90.0, 0.0, 0.0),
    )
    actor.set_actor_label("HubKay_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
    # 2) yaw in world space around Z so upright is preserved
    if abs(yaw) > 0.01:
        actor.add_actor_world_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False, True)
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True)
    origin, extent = actor.get_actor_bounds(False)
    tall_z = extent.z * 2.0
    xy = max(extent.x, extent.y) * 2.0
    # wide buildings (market) can have xy > z while still upright; compare to mesh sy
    bb = mesh.get_bounding_box()
    sy = abs(bb.max.y - bb.min.y)
    ok = "UPRIGHT" if abs(tall_z - sy) < max(50.0, sy * 0.15) else "CHECK"
    unreal.log("orient %s Z=%.1f meshY=%.1f maxXY=%.1f %s" % (key, tall_z, sy, xy, ok))
    placed += 1

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(200.0, 200.0, ground_z + 120.0), False, True)
        break

unreal.EditorLevelLibrary.save_current_level()
unreal.log("KAYKIT ORIENT2 READY placed=%d" % placed)
