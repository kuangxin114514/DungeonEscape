import unreal
import math
import os

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
RAW = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj"
DEST = "/Game/Environments/KayKitMedieval"
SCALE = 400.0
# 向右顺时针 90°（绕竖直轴看时为 Yaw=-90；立起来用 Roll=-90）
IMPORT_ROT = unreal.Rotator(0.0, 0.0, -90.0)  # baked into import if supported
SPAWN_ROLL = -90.0  # 顺时针立起来

IMPORT_LIST = [
    ("Tiles", "tiles/base", "hex_grass.obj"),
    ("Tiles", "tiles/roads", "hex_road_A.obj"),
    ("Tiles", "tiles/roads", "hex_road_B.obj"),
    ("Tiles", "tiles/roads", "hex_road_C.obj"),
    ("Tiles", "tiles/roads", "hex_road_D.obj"),
    ("Tiles", "tiles/roads", "hex_road_E.obj"),
    ("Tiles", "tiles/roads", "hex_road_J.obj"),
    ("Nature", "decoration/nature", "tree_single_A.obj"),
    ("Nature", "decoration/nature", "tree_single_B.obj"),
    ("Nature", "decoration/nature", "trees_A_small.obj"),
    ("Nature", "decoration/nature", "trees_A_medium.obj"),
    ("Nature", "decoration/nature", "trees_B_small.obj"),
    ("Nature", "decoration/nature", "rock_single_A.obj"),
    ("Nature", "decoration/nature", "rock_single_B.obj"),
    ("Nature", "decoration/nature", "rock_single_C.obj"),
]

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def import_obj(abs_path, dest_path, asset_name):
    full = dest_path + "/" + asset_name
    # delete old crooked import so we refresh
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
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
        # 向右顺时针 90°
        for prop, val in [
            ("import_rotation", IMPORT_ROT),
            ("import_translation", unreal.Vector(0, 0, 0)),
            ("convert_scene", True),
            ("force_front_x_axis", False),
            ("transform_vertex_to_absolute", True),
        ]:
            try:
                sm.set_editor_property(prop, val)
            except Exception:
                pass
        options.set_editor_property("static_mesh_import_data", sm)
        task.options = options
    except Exception as e:
        unreal.log_warning("opt " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.log("imported " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    unreal.log_error("fail " + abs_path)
    return None

def spawn_on_ground(mesh, x, y, yaw, ground_z, label, scale=SCALE):
    # Roll -90 = 向右顺时针立起来
    rot = unreal.Rotator(0.0, float(yaw), SPAWN_ROLL)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(float(x), float(y), ground_z), rot
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

# --- import ---
meshes = {}
for folder, sub, fname in IMPORT_LIST:
    dest = DEST + "/" + folder
    ensure_dir(dest)
    path = os.path.join(RAW, sub.replace("/", os.sep), fname)
    name = fname.replace(".obj", "")
    if not os.path.isfile(path):
        unreal.log_warning("missing " + path)
        continue
    m = import_obj(path, dest, name)
    if m:
        meshes[name] = m

mat = None
for p in [DEST + "/Buildings/hexagons_medieval", DEST + "/Tiles/hexagons_medieval"]:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        mat = unreal.EditorAssetLibrary.load_asset(p)
        break
if mat:
    for m in meshes.values():
        try:
            m.set_material(0, mat)
        except Exception:
            pass

unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

# ground height from HubGround_Plane or character feet
ground_z = 127.0
gx, gy = 0.0, 0.0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "HubGround_Plane":
        loc = a.get_actor_location()
        ground_z = loc.z
        gx, gy = loc.x, loc.y
        unreal.log("ground from plane z=" + str(ground_z))
        break
else:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "ThirdPersonCharacter" in a.get_actor_label():
            o, e = a.get_actor_bounds(True)
            ground_z = o.z - e.z
            loc = a.get_actor_location()
            gx, gy = loc.x, loc.y
            unreal.log("ground from char z=" + str(ground_z))
            break

# clear previous env dress
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubEnv_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

grass = meshes.get("hex_grass")
roads = [meshes[k] for k in ["hex_road_A", "hex_road_B", "hex_road_C", "hex_road_D", "hex_road_E", "hex_road_J"] if meshes.get(k)]
trees = [meshes[k] for k in ["tree_single_A", "tree_single_B", "trees_A_small", "trees_A_medium", "trees_B_small"] if meshes.get(k)]
rocks = [meshes[k] for k in ["rock_single_A", "rock_single_B", "rock_single_C"] if meshes.get(k)]

step = SCALE * 0.85
# grass patch around character / ground center
half = 8
n = 0
if grass:
    for iy in range(-half, half + 1):
        for ix in range(-half, half + 1):
            xoff = (step * 0.5) if (iy % 2) else 0.0
            x = gx + ix * step + xoff
            y = gy + iy * step * 0.75
            spawn_on_ground(grass, x, y, 0, ground_z, "HubEnv_Grass_%d" % n)
            n += 1
    unreal.log("grass=" + str(n))

# cross roads through center
ri = 0
if roads:
    for i in range(-6, 7):
        spawn_on_ground(roads[ri % len(roads)], gx + i * step, gy, 0, ground_z + 1.0, "HubEnv_RoadX_%d" % i, SCALE)
        ri += 1
    for i in range(-6, 7):
        if i == 0:
            continue
        spawn_on_ground(roads[ri % len(roads)], gx, gy + i * step, 90, ground_z + 1.0, "HubEnv_RoadY_%d" % i, SCALE)
        ri += 1
    unreal.log("roads done")

# trees around plaza edge
ti = 0
if trees:
    for i in range(12):
        ang = math.radians(i * 30)
        r = step * 7.5
        x = gx + math.cos(ang) * r
        y = gy + math.sin(ang) * r
        spawn_on_ground(trees[ti % len(trees)], x, y, i * 30, ground_z, "HubEnv_Tree_%d" % ti)
        ti += 1
    for i in range(8):
        ang = math.radians(20 + i * 45)
        r = step * 5.0
        x = gx + math.cos(ang) * r
        y = gy + math.sin(ang) * r
        spawn_on_ground(trees[ti % len(trees)], x, y, i * 45, ground_z, "HubEnv_Tree_%d" % ti, SCALE * 0.8)
        ti += 1
    unreal.log("trees=" + str(ti))

ri = 0
if rocks:
    for i in range(8):
        ang = math.radians(10 + i * 45)
        r = step * 6.2
        spawn_on_ground(rocks[ri % len(rocks)], gx + math.cos(ang) * r, gy + math.sin(ang) * r, i * 40, ground_z, "HubEnv_Rock_%d" % ri, SCALE * 0.65)
        ri += 1

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory(DEST)
unreal.log("HUB GROUND DRESS DONE meshes=%d z=%s" % (len(meshes), ground_z))
