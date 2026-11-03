import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
SCALE = 600.0

# Compact plaza: buildings close enough to see from PlayerStart
# Z will be lifted per-mesh so bottoms sit on ground
LAYOUT = [
    ("building_church_blue", unreal.Vector(1200, -900, 0), unreal.Rotator(0, 0, 0)),
    ("building_tavern_blue", unreal.Vector(-1100, -900, 0), unreal.Rotator(0, 90, 0)),
    ("building_market_blue", unreal.Vector(0, -1500, 0), unreal.Rotator(0, 0, 0)),
    ("building_blacksmith_blue", unreal.Vector(1500, 200, 0), unreal.Rotator(0, -90, 0)),
    ("building_barracks_blue", unreal.Vector(-1500, 200, 0), unreal.Rotator(0, 90, 0)),
    ("building_home_A_blue", unreal.Vector(1000, 1200, 0), unreal.Rotator(0, 180, 0)),
    ("building_home_B_blue", unreal.Vector(-900, 1300, 0), unreal.Rotator(0, 180, 0)),
    ("building_well_blue", unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)),
    ("building_tower_A_blue", unreal.Vector(2000, -1600, 0), unreal.Rotator(0, 45, 0)),
    ("building_castle_blue", unreal.Vector(0, 2200, 0), unreal.Rotator(0, 180, 0)),
    ("building_windmill_blue", unreal.Vector(-2000, -400, 0), unreal.Rotator(0, 30, 0)),
]

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

destroyed = 0
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    label = a.get_actor_label()
    name = a.get_name()
    cls = a.get_class().get_name()
    kill = False
    if label.startswith("HubMed_"):
        kill = True
    # template arena walls / cubes
    if label.startswith("Wall") or "Wall" in label:
        kill = True
    if label in ("Arena",):
        kill = True
    # leftover third person overview props
    if "ThirdPerson" in label and "Character" not in cls:
        pass
    # SM_Cube walls used as arena
    if isinstance(a, unreal.StaticMeshActor):
        smc = a.static_mesh_component
        mesh = smc.static_mesh if smc else None
        if mesh and mesh.get_name() == "SM_Cube":
            # keep Floor if labeled Floor / Hub_Floor
            if label not in ("Floor", "Hub_Floor") and "Floor" not in label:
                kill = True
    if kill:
        unreal.EditorLevelLibrary.destroy_actor(a)
        destroyed += 1

unreal.log("destroyed=" + str(destroyed))

mat = unreal.EditorAssetLibrary.load_asset("/Game/Environments/KayKitMedieval/Buildings/hexagons_medieval")

placed = 0
for key, loc, rot in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        unreal.log_warning("missing " + key)
        continue
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass
    # lift so mesh bottom sits on Z=0
    bbox = mesh.get_bounding_box()
    z_lift = -bbox.min.z * SCALE
    final_loc = unreal.Vector(loc.x, loc.y, z_lift)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, final_loc, rot)
    actor.set_actor_label("HubMed_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    placed += 1
    unreal.log("placed " + key + " z=" + str(z_lift))

# floor: large flat plaza
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    label = a.get_actor_label()
    if label in ("Floor", "Hub_Floor") or label == "Floor":
        a.set_actor_location(unreal.Vector(0, 0, -5), False, True)
        a.set_actor_scale3d(unreal.Vector(50, 50, 1))
        unreal.log("floor scaled")
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(250, 250, 120), False, True)
        unreal.log("PlayerStart ok")

# remove empty Arena folder if any leftover
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory("/Game/Environments/KayKitMedieval")
unreal.log("HUB VISIBLE REBUILD DONE placed=" + str(placed))
