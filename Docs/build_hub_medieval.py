import unreal
import os

OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj\buildings\blue"
TEX_ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack"
DEST = "/Game/Environments/KayKitMedieval"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"
SCALE = 120.0  # KayKit units -> UE cm (tune)

BUILDINGS = [
    "building_church_blue.obj",
    "building_tavern_blue.obj",
    "building_market_blue.obj",
    "building_blacksmith_blue.obj",
    "building_barracks_blue.obj",
    "building_home_A_blue.obj",
    "building_home_B_blue.obj",
    "building_well_blue.obj",
    "building_tower_A_blue.obj",
    "building_castle_blue.obj",
    "building_windmill_blue.obj",
]

# Hub layout: square plaza around origin (PlayerStart near 0,0)
LAYOUT = [
    ("building_church_blue", unreal.Vector(1200, -800, 0), unreal.Rotator(0, 0, 0)),
    ("building_tavern_blue", unreal.Vector(-1000, -900, 0), unreal.Rotator(0, 90, 0)),
    ("building_market_blue", unreal.Vector(0, -1400, 0), unreal.Rotator(0, 0, 0)),
    ("building_blacksmith_blue", unreal.Vector(1400, 200, 0), unreal.Rotator(0, -90, 0)),
    ("building_barracks_blue", unreal.Vector(-1400, 200, 0), unreal.Rotator(0, 90, 0)),
    ("building_home_A_blue", unreal.Vector(900, 1100, 0), unreal.Rotator(0, 180, 0)),
    ("building_home_B_blue", unreal.Vector(-800, 1200, 0), unreal.Rotator(0, 180, 0)),
    ("building_well_blue", unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)),
    ("building_tower_A_blue", unreal.Vector(1800, -1800, 0), unreal.Rotator(0, 45, 0)),
    ("building_castle_blue", unreal.Vector(0, 2000, 0), unreal.Rotator(0, 180, 0)),
    ("building_windmill_blue", unreal.Vector(-1800, -400, 0), unreal.Rotator(0, 30, 0)),
]

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def import_obj(abs_path, dest_path, asset_name):
    full = dest_path + "/" + asset_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.log("exists " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = dest_path
    task.destination_name = asset_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    options = unreal.FbxImportUI()
    # OBJ uses Interchange/or AutomatedAssetImport in 4.27 - FbxImportUI may still apply for static mesh
    try:
        options.set_editor_property("automated_import_should_detect_type", False)
        options.set_editor_property("import_as_skeletal", False)
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_materials", True)
        options.set_editor_property("import_textures", True)
        options.set_editor_property("static_mesh_import_data", unreal.FbxStaticMeshImportData())
        sm = options.get_editor_property("static_mesh_import_data")
        sm.set_editor_property("combine_meshes", True)
        sm.set_editor_property("auto_generate_collision", True)
        sm.set_editor_property("import_uniform_scale", 1.0)
        task.options = options
    except Exception as e:
        unreal.log_warning("options: " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.log("imported " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    # sometimes name differs
    assets = unreal.EditorAssetLibrary.list_assets(dest_path, True, False)
    for a in assets:
        if asset_name.lower() in a.lower():
            unreal.log("found as " + a)
            return unreal.EditorAssetLibrary.load_asset(a)
    unreal.log_error("import failed " + abs_path)
    return None

def spawn_mesh(mesh, loc, rot, label):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
    if not actor:
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
    # enable collision
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    return actor

ensure_dir(DEST)
ensure_dir(DEST + "/Buildings")

# Import selected buildings
imported = {}
for fname in BUILDINGS:
    path = os.path.join(OBJ_DIR, fname)
    if not os.path.isfile(path):
        unreal.log_warning("missing " + path)
        continue
    name = os.path.splitext(fname)[0]
    mesh = import_obj(path, DEST + "/Buildings", name)
    if mesh:
        imported[name] = mesh

unreal.log("imported_count=" + str(len(imported)))

# Load hub
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
unreal.log("hub loaded")

# Hide/remove old arena walls? Keep floor for walkability; hide large template props optionally
actors = unreal.EditorLevelLibrary.get_all_level_actors()
for a in actors:
    label = a.get_actor_label()
    name = a.get_name()
    # Remove previous KayKit hub dressing if re-run
    if label.startswith("HubMed_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

# Place buildings
for key, loc, rot in LAYOUT:
    mesh = imported.get(key)
    if not mesh:
        unreal.log_warning("no mesh for " + key)
        continue
    spawn_mesh(mesh, loc, rot, "HubMed_" + key)
    unreal.log("placed " + key)

# Nudge PlayerStart to plaza center near well
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(200.0, 200.0, 120.0), False, True)
        unreal.log("moved PlayerStart")
        break

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory(DEST)
unreal.log("HUB MEDIEVAL DRESSING DONE")
