import unreal

HUB_DIR = "/Game/Maps/Hub"
HUB_MAP = HUB_DIR + "/Map_Hub"

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

ensure_dir(HUB_DIR)

# Create a new blank level asset
if unreal.EditorAssetLibrary.does_asset_exist(HUB_MAP):
    unreal.log("Map exists, loading")
    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
else:
    # new_level creates and opens
    try:
        unreal.EditorLevelLibrary.new_level(HUB_MAP)
        unreal.log("Created new level via EditorLevelLibrary.new_level")
    except Exception as e:
        unreal.log_warning("new_level failed: " + str(e))
        # Fallback factory
        factory = unreal.WorldFactory()
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        world_asset = asset_tools.create_asset("Map_Hub", HUB_DIR, unreal.World, factory)
        if world_asset:
            unreal.EditorAssetLibrary.save_loaded_asset(world_asset)
            unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
            unreal.log("Created via WorldFactory")
        else:
            unreal.log_error("Could not create Map_Hub")

# Helpers for spawn
def spawn(cls, loc, rot=None):
    if rot is None:
        rot = unreal.Rotator(0.0, 0.0, 0.0)
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        return sub.spawn_actor_from_class(cls, loc, rot)
    except Exception:
        return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)

# Clear nothing — empty level; add essentials
# Floor
floor = spawn(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, 0.0))
if floor:
    sm = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    mesh_comp = floor.static_mesh_component
    mesh_comp.set_static_mesh(sm)
    floor.set_actor_scale3d(unreal.Vector(20.0, 20.0, 1.0))
    floor.set_actor_label("Hub_Floor")
    unreal.log("Added floor")

# Light
light = spawn(unreal.DirectionalLight, unreal.Vector(0.0, 0.0, 400.0), unreal.Rotator(-40.0, -30.0, 0.0))
if light:
    light.set_actor_label("Hub_Sun")
    unreal.log("Added directional light")

# Sky atmosphere / skylight for visibility
sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, 500.0))
if sky:
    sky.set_actor_label("Hub_SkyLight")

# Player start
ps = spawn(unreal.PlayerStart, unreal.Vector(0.0, 0.0, 100.0))
if ps:
    ps.set_actor_label("Hub_PlayerStart")
    unreal.log("Added PlayerStart")

# GameMode override
try:
    world_obj = unreal.EditorLevelLibrary.get_editor_world()
    ws = world_obj.get_world_settings()
    gm_cls = unreal.load_class(None, "/Game/Core/GameFlow/GM_Hub.GM_Hub_C")
    if ws and gm_cls:
        ws.set_editor_property("DefaultGameMode", gm_cls)
        unreal.log("WorldSettings DefaultGameMode = GM_Hub")
    else:
        unreal.log_warning("GM_Hub_C not loaded")
except Exception as e:
    unreal.log_warning(str(e))

# Use ThirdPerson character as default pawn via GameMode if possible — GM_Hub is empty GameModeBase
# Set DefaultPawnClass on world GM? Better leave until we configure GM_Hub BP.
# For Play to work, set GameMode to ThirdPersonGameMode temporarily OR set pawn on GM_Hub later.
# Use ThirdPerson GameMode for now so Play works, store GM_Hub for later wiring.
try:
    world_obj = unreal.EditorLevelLibrary.get_editor_world()
    ws = world_obj.get_world_settings()
    tp_gm = unreal.load_class(None, "/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode.ThirdPersonGameMode_C")
    if ws and tp_gm:
        ws.set_editor_property("DefaultGameMode", tp_gm)
        unreal.log("Temp DefaultGameMode = ThirdPersonGameMode (playable)")
except Exception as e:
    unreal.log_warning(str(e))

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_asset(HUB_MAP)
unreal.log("Map_Hub saved")
