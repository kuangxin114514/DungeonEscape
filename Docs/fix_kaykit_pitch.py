import unreal

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST = "/Game/Environments/KayKitMedieval/Buildings"
# Pitch -90: Y-up OBJ -> Z-up UE (verified: tall axis becomes world Z)
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

mat = unreal.EditorAssetLibrary.load_asset(DEST + "/M_KayKitMedieval")
if not mat:
    mat = unreal.EditorAssetLibrary.load_asset(DEST + "/hexagons_medieval")

placed = 0
for key, x, y, yaw in LAYOUT:
    mesh = unreal.EditorAssetLibrary.load_asset(DEST + "/" + key)
    if not mesh:
        unreal.log_warning("missing " + key)
        continue
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass
    # Pitch=-90 upright
    rot = unreal.Rotator(-90.0, float(yaw), 0.0)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(float(x), float(y), float(ground_z)), rot
    )
    actor.set_actor_label("HubKay_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True
    )
    origin, extent = actor.get_actor_bounds(False)
    tall_z = extent.z * 2.0
    xy = max(extent.x, extent.y) * 2.0
    ok = "UPRIGHT" if tall_z >= xy * 0.85 else "SIDEWAYS?"
    unreal.log(
        "fix %s Z=%.1f maxXY=%.1f %s locZ=%.1f"
        % (key, tall_z, xy, ok, actor.get_actor_location().z)
    )
    placed += 1

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(200.0, 200.0, ground_z + 120.0), False, True)
        break

unreal.EditorLevelLibrary.save_current_level()
unreal.log("KAYKIT PITCH FIX READY placed=%d" % placed)
