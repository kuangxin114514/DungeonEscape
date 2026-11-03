import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
SCALE = 500.0
GROUND_Z = 0.0

# Blender/OBJ often needs Roll=+90 in UE (X-forward Y-up -> Z-up)
LAYOUT = [
    ("building_church_blue", unreal.Vector(1100, -800, 0), 0),
    ("building_tavern_blue", unreal.Vector(-1000, -800, 0), 90),
    ("building_market_blue", unreal.Vector(0, -1400, 0), 0),
    ("building_blacksmith_blue", unreal.Vector(1400, 150, 0), -90),
    ("building_barracks_blue", unreal.Vector(-1400, 150, 0), 90),
    ("building_home_A_blue", unreal.Vector(900, 1100, 0), 180),
    ("building_home_B_blue", unreal.Vector(-800, 1200, 0), 180),
    ("building_well_blue", unreal.Vector(0, 0, 0), 0),
    ("building_tower_A_blue", unreal.Vector(1800, -1500, 0), 45),
    ("building_castle_blue", unreal.Vector(0, 2000, 0), 180),
    ("building_windmill_blue", unreal.Vector(-1800, -350, 0), 30),
]

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubMed_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

mat = unreal.EditorAssetLibrary.load_asset(DEST + "/hexagons_medieval")
placed = 0

for key, xy, yaw in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        unreal.log_warning("missing " + key)
        continue
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass

    # Roll 90 stands Y-up mesh; yaw faces plaza
    rot = unreal.Rotator(0.0, yaw, 90.0)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(xy.x, xy.y, 0.0), rot
    )
    actor.set_actor_label("HubMed_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))

    # Snap bottom of world bounds to GROUND_Z
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    delta = GROUND_Z - bottom
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + delta), False, True)

    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass

    origin2, extent2 = actor.get_actor_bounds(False)
    unreal.log(
        "level " + key
        + " bottom=" + str(origin2.z - extent2.z)
        + " h=" + str(extent2.z * 2)
    )
    placed += 1

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    label = a.get_actor_label()
    if label in ("Floor", "Hub_Floor"):
        a.set_actor_location(unreal.Vector(0, 0, -5), False, True)
        a.set_actor_scale3d(unreal.Vector(40, 40, 1))
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(200, 200, 100), False, True)

unreal.EditorLevelLibrary.save_current_level()
unreal.log("HUB LEVEL DONE placed=" + str(placed))
