import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
SCALE = 600.0

# OBJ/Blender Y-up -> UE Z-up: pitch -90
LAYOUT = [
    ("building_church_blue", unreal.Vector(1200, -900, 0), 0),
    ("building_tavern_blue", unreal.Vector(-1100, -900, 0), 90),
    ("building_market_blue", unreal.Vector(0, -1500, 0), 0),
    ("building_blacksmith_blue", unreal.Vector(1500, 200, 0), -90),
    ("building_barracks_blue", unreal.Vector(-1500, 200, 0), 90),
    ("building_home_A_blue", unreal.Vector(1000, 1200, 0), 180),
    ("building_home_B_blue", unreal.Vector(-900, 1300, 0), 180),
    ("building_well_blue", unreal.Vector(0, 0, 0), 0),
    ("building_tower_A_blue", unreal.Vector(2000, -1600, 0), 45),
    ("building_castle_blue", unreal.Vector(0, 2200, 0), 180),
    ("building_windmill_blue", unreal.Vector(-2000, -400, 0), 30),
]

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubMed_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

mat = unreal.EditorAssetLibrary.load_asset(DEST + "/hexagons_medieval")
placed = 0
for key, loc, yaw in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        unreal.log_warning("missing " + key)
        continue
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass
    # After pitch -90, original Y becomes up; use local Y extent for ground lift
    bbox = mesh.get_bounding_box()
    # with Pitch=-90: world Z comes from local Y; bottom often bbox.min.y
    z_lift = -bbox.min.y * SCALE
    # also clamp if min.y is near 0 and min.z was the old bottom
    if abs(bbox.min.y) < 1e-4:
        z_lift = -bbox.min.z * SCALE
    final = unreal.Vector(loc.x, loc.y, z_lift)
    # Pitch -90 stands Y-up meshes upright in UE
    rot = unreal.Rotator(-90.0, yaw, 0.0)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, final, rot)
    actor.set_actor_label("HubMed_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    placed += 1
    unreal.log("upright " + key + " z=" + str(z_lift))

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(250, 250, 120), False, True)

unreal.EditorLevelLibrary.save_current_level()
unreal.log("HUB UPRIGHT DONE placed=" + str(placed))
