import unreal
import os
import math

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
Q_FBX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\QuaterniusMedieval\Medieval Village Pack - Dec 2020"
K_FBX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KenneyFantasyTown\Models\FBX format"
DEST_Q = "/Game/Environments/QuaterniusVillage"
DEST_K = "/Game/Environments/KenneyTown"
# Quaternius often meters -> 100; Kenney similar
SCALE_Q = 100.0
SCALE_K = 100.0

Q_BUILDINGS = [
    ("Buildings/FBX", "House_1.fbx"),
    ("Buildings/FBX", "House_2.fbx"),
    ("Buildings/FBX", "House_3.fbx"),
    ("Buildings/FBX", "House_4.fbx"),
    ("Buildings/FBX", "Inn.fbx"),
    ("Buildings/FBX", "Blacksmith.fbx"),
    ("Buildings/FBX", "Mill.fbx"),
    ("Buildings/FBX", "Stable.fbx"),
    ("Buildings/FBX", "Bell_Tower.fbx"),
    ("Buildings/FBX", "Well.fbx"),
    ("Buildings/FBX", "Gazebo.fbx"),
    ("Buildings/FBX", "Sawmill.fbx"),
]
Q_PROPS = [
    ("Props/FBX", "Barrel.fbx"),
    ("Props/FBX", "Crate.fbx"),
    ("Props/FBX", "Cart.fbx"),
    ("Props/FBX", "Bench_1.fbx"),
    ("Props/FBX", "MarketStand_1.fbx"),
    ("Props/FBX", "MarketStand_2.fbx"),
    ("Props/FBX", "Fence.fbx"),
    ("Props/FBX", "Path_Straight.fbx"),
    ("Props/FBX", "Path_Square.fbx"),
    ("Props/FBX", "Rock_1.fbx"),
    ("Props/FBX", "Rock_2.fbx"),
    ("Props/FBX", "Hay.fbx"),
]
# find actual prop folder names
K_ITEMS = [
    "tree.fbx", "tree-high.fbx", "tree-crooked.fbx", "tree-high-round.fbx",
    "road.fbx", "road-bend.fbx", "road-corner.fbx", "road-edge.fbx",
    "hedge.fbx", "hedge-large.fbx", "hedge-gate.fbx",
    "wall.fbx", "wall-corner.fbx", "wall-doorway-square.fbx", "fence.fbx", "fence-gate.fbx",
]

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def import_fbx(abs_path, dest_path, asset_name):
    full = dest_path + "/" + asset_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = dest_path
    task.destination_name = asset_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    try:
        options = unreal.FbxImportUI()
        options.set_editor_property("automated_import_should_detect_type", False)
        options.set_editor_property("import_as_skeletal", False)
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_materials", True)
        options.set_editor_property("import_textures", True)
        sm = unreal.FbxStaticMeshImportData()
        sm.set_editor_property("combine_meshes", True)
        sm.set_editor_property("auto_generate_collision", True)
        sm.set_editor_property("import_uniform_scale", 1.0)
        try:
            sm.set_editor_property("convert_scene", True)
            sm.set_editor_property("force_front_x_axis", False)
        except Exception:
            pass
        options.set_editor_property("static_mesh_import_data", sm)
        task.options = options
    except Exception as e:
        unreal.log_warning(str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.log("ok " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    unreal.log_error("fail " + abs_path)
    return None

def spawn(mesh, x, y, yaw, ground_z, label, scale):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(float(x), float(y), float(ground_z)),
        unreal.Rotator(0.0, float(yaw), 0.0),
    )
    if not actor:
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    o, e = actor.get_actor_bounds(False)
    bottom = o.z - e.z
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True)
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    return actor

# discover Quaternius folders
def find_q(rel_guess, fname):
    # try common layouts
    candidates = [
        os.path.join(Q_FBX, rel_guess.replace("/", os.sep), fname),
        os.path.join(Q_FBX, "FBX", fname),
        os.path.join(Q_FBX, "Buildings", "FBX", fname),
        os.path.join(Q_FBX, "Props", "FBX", fname),
    ]
    for root, dirs, files in os.walk(Q_FBX):
        if fname in files:
            return os.path.join(root, fname)
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

meshes_q = {}
ensure_dir(DEST_Q + "/Buildings")
ensure_dir(DEST_Q + "/Props")
for rel, fname in Q_BUILDINGS + Q_PROPS:
    path = find_q(rel, fname)
    if not path:
        unreal.log_warning("missing " + fname)
        continue
    name = fname.replace(".fbx", "").replace(".FBX", "")
    folder = "Buildings" if (rel, fname) in Q_BUILDINGS else "Props"
    m = import_fbx(path, DEST_Q + "/" + folder, name)
    if m:
        meshes_q[name] = m

meshes_k = {}
ensure_dir(DEST_K)
for fname in K_ITEMS:
    path = os.path.join(K_FBX, fname)
    if not os.path.isfile(path):
        unreal.log_warning("missing kenney " + fname)
        continue
    name = fname.replace(".fbx", "").replace("-", "_")
    m = import_fbx(path, DEST_K, name)
    if m:
        meshes_k[name] = m

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

# clear previous hub env/buildings from new packs
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    lab = a.get_actor_label()
    if lab.startswith("HubMed_") or lab.startswith("HubEnv_") or lab.startswith("HubQ_") or lab.startswith("HubK_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

ground_z = 127.0
cx, cy = -750.0, 390.0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "HubGround_Plane":
        loc = a.get_actor_location()
        ground_z = loc.z
        cx, cy = loc.x, loc.y
        break
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "ThirdPersonCharacter" in a.get_actor_label():
        loc = a.get_actor_location()
        cx, cy = loc.x, loc.y
        break

unreal.log("center=%.1f,%.1f z=%.1f" % (cx, cy, ground_z))

# layout buildings around plaza
layout = [
    ("Well", 0, 0, 0),
    ("Inn", -900, -700, 20),
    ("Blacksmith", 900, -650, -20),
    ("House_1", -1100, 200, 90),
    ("House_2", 1100, 250, -90),
    ("House_3", -700, 900, 180),
    ("House_4", 700, 950, 180),
    ("Mill", -1500, -200, 45),
    ("Stable", 1400, -100, -45),
    ("Bell_Tower", 0, 1400, 180),
    ("Gazebo", 400, -200, 30),
    ("Sawmill", -400, -1100, 0),
]
for name, dx, dy, yaw in layout:
    m = meshes_q.get(name)
    if m:
        spawn(m, cx + dx, cy + dy, yaw, ground_z, "HubQ_" + name, SCALE_Q)

# market props near center
props_layout = [
    ("MarketStand_1", 250, 150, 10),
    ("MarketStand_2", -250, 180, -15),
    ("Barrel", 180, -80, 0),
    ("Crate", 220, -40, 40),
    ("Cart", -300, -150, 70),
    ("Bench_1", 80, 280, 0),
    ("Hay", 500, 400, 20),
]
for name, dx, dy, yaw in props_layout:
    m = meshes_q.get(name)
    if m:
        spawn(m, cx + dx, cy + dy, yaw, ground_z, "HubQ_" + name, SCALE_Q)

# Kenney roads cross
road = meshes_k.get("road")
if road:
    for i in range(-8, 9):
        spawn(road, cx + i * 200, cy, 0, ground_z + 0.5, "HubK_RoadX_%d" % i, SCALE_K)
        if i != 0:
            spawn(road, cx, cy + i * 200, 90, ground_z + 0.5, "HubK_RoadY_%d" % i, SCALE_K)

# trees ring
tree_names = ["tree", "tree_high", "tree_crooked", "tree_high_round"]
trees = [meshes_k[n] for n in tree_names if n in meshes_k]
ti = 0
for i in range(14):
    ang = math.radians(i * (360.0 / 14))
    r = 1800
    if trees:
        spawn(trees[ti % len(trees)], cx + math.cos(ang) * r, cy + math.sin(ang) * r, i * 25, ground_z, "HubK_Tree_%d" % ti, SCALE_K)
        ti += 1

# hedges / fence bits
hedge = meshes_k.get("hedge_large") or meshes_k.get("hedge")
if hedge:
    for i in range(10):
        ang = math.radians(i * 36)
        r = 1600
        spawn(hedge, cx + math.cos(ang) * r, cy + math.sin(ang) * r, i * 36 + 90, ground_z, "HubK_Hedge_%d" % i, SCALE_K)

# simple wall segments on far side
wall = meshes_k.get("wall")
wdoor = meshes_k.get("wall_doorway_square") or wall
if wall:
    for i in range(-5, 6):
        mesh = wdoor if i == 0 else wall
        spawn(mesh, cx + i * 220, cy - 2000, 0, ground_z, "HubK_WallS_%d" % i, SCALE_K)
        spawn(wall, cx + i * 220, cy + 2000, 180, ground_z, "HubK_WallN_%d" % i, SCALE_K)

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory("/Game/Environments")
unreal.log("NEW HUB DONE q=%d k=%d" % (len(meshes_q), len(meshes_k)))
