import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
SCALE = 750.0  # mesh ~1 unit -> ~7.5m buildings
LAYOUT = [
    ("building_church_blue", unreal.Vector(4500, -3000, 0), unreal.Rotator(0, 0, 0)),
    ("building_tavern_blue", unreal.Vector(-3800, -3400, 0), unreal.Rotator(0, 90, 0)),
    ("building_market_blue", unreal.Vector(0, -5200, 0), unreal.Rotator(0, 0, 0)),
    ("building_blacksmith_blue", unreal.Vector(5200, 800, 0), unreal.Rotator(0, -90, 0)),
    ("building_barracks_blue", unreal.Vector(-5200, 800, 0), unreal.Rotator(0, 90, 0)),
    ("building_home_A_blue", unreal.Vector(3400, 4200, 0), unreal.Rotator(0, 180, 0)),
    ("building_home_B_blue", unreal.Vector(-3000, 4500, 0), unreal.Rotator(0, 180, 0)),
    ("building_well_blue", unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)),
    ("building_tower_A_blue", unreal.Vector(6800, -6800, 0), unreal.Rotator(0, 45, 0)),
    ("building_castle_blue", unreal.Vector(0, 7500, 0), unreal.Rotator(0, 180, 0)),
    ("building_windmill_blue", unreal.Vector(-6800, -1500, 0), unreal.Rotator(0, 30, 0)),
]

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

# remove old dressing
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubMed_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

# shared material (atlas)
mat = unreal.EditorAssetLibrary.load_asset("/Game/Environments/KayKitMedieval/Buildings/hexagons_medieval")
tex = unreal.EditorAssetLibrary.load_asset("/Game/Environments/KayKitMedieval/Buildings/hexagons_medieval_ncl1_1")
unreal.log("MAT=" + str(mat) + " TEX=" + str(tex))

placed = 0
for key, loc, rot in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        unreal.log_warning("missing " + key)
        continue
    # ensure material slot uses kaykit atlas mat if present
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception as e:
            unreal.log_warning("set_material: " + str(e))
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
    actor.set_actor_label("HubMed_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    placed += 1
    unreal.log("placed " + key)

# enlarge floor if present
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    label = a.get_actor_label()
    if label in ("Hub_Floor", "Floor") or "Floor" in label:
        # big plaza under city
        a.set_actor_scale3d(unreal.Vector(40, 40, 1))
        a.set_actor_location(unreal.Vector(0, 0, -10), False, True)
        unreal.log("scaled floor " + label)
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(400, 400, 150), False, True)
        unreal.log("moved PlayerStart")

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory("/Game/Environments/KayKitMedieval")
unreal.log("HUB RESCALE DONE placed=" + str(placed))
