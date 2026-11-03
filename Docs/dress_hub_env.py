import unreal
import math

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
RAW = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj"
DEST = "/Game/Environments/KayKitMedieval"
SCALE = 500.0
GROUND_Z = 0.0
# KayKit hex tile ~1 unit across in source; after scale ~500uu
HEX = 500.0

IMPORTS = {
    "Walls": [
        ("buildings/neutral", "wall_straight.obj"),
        ("buildings/neutral", "wall_straight_gate.obj"),
        ("buildings/neutral", "wall_corner_A_outside.obj"),
        ("buildings/neutral", "wall_corner_B_outside.obj"),
        ("buildings/neutral", "fence_stone_straight.obj"),
    ],
    "Tiles": [
        ("tiles/base", "hex_grass.obj"),
        ("tiles/base", "hex_grass_bottom.obj"),
    ],
    "Nature": [
        ("decoration/nature", "tree_single_A.obj"),
        ("decoration/nature", "tree_single_B.obj"),
        ("decoration/nature", "trees_A_small.obj"),
        ("decoration/nature", "trees_A_medium.obj"),
        ("decoration/nature", "trees_B_small.obj"),
        ("decoration/nature", "rock_single_A.obj"),
        ("decoration/nature", "rock_single_B.obj"),
        ("decoration/nature", "rock_single_C.obj"),
        ("decoration/nature", "hills_A_trees.obj"),
        ("decoration/nature", "hills_B.obj"),
        ("decoration/nature", "mountain_A_grass_trees.obj"),
        ("decoration/nature", "mountain_B_grass.obj"),
    ],
    "Props": [
        ("decoration/props", "barrel.obj"),
        ("decoration/props", "crate_A_big.obj"),
        ("decoration/props", "crate_B_small.obj"),
        ("decoration/props", "flag_blue.obj"),
        ("decoration/props", "wagon" if False else "wheelbarrow.obj"),
        ("decoration/props", "sack.obj"),
    ],
}

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def import_obj(abs_path, dest_path, asset_name):
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
        options.set_editor_property("static_mesh_import_data", sm)
        task.options = options
    except Exception as e:
        unreal.log_warning("options " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.log("imported " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    unreal.log_error("fail " + abs_path)
    return None

def spawn_kay(mesh, x, y, yaw, label, scale=SCALE):
    rot = unreal.Rotator(0.0, float(yaw), 90.0)  # Roll 90 for Y-up OBJ
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(float(x), float(y), 0.0), rot
    )
    if not actor:
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + (GROUND_Z - bottom)), False, True)
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    return actor

# --- import ---
meshes = {}
for folder, items in IMPORTS.items():
    dest = DEST + "/" + folder
    ensure_dir(dest)
    for sub, fname in items:
        path = RAW + "\\" + sub.replace("/", "\\") + "\\" + fname
        name = fname.replace(".obj", "")
        import os
        if not os.path.isfile(path):
            unreal.log_warning("missing file " + path)
            continue
        m = import_obj(path, dest, name)
        if m:
            meshes[name] = m

# shared material if present
mat = None
for p in [
    DEST + "/Buildings/hexagons_medieval",
    DEST + "/Walls/hexagons_medieval",
    DEST + "/Tiles/hexagons_medieval",
]:
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

# wipe previous env dressing only (keep user's HubMed_ buildings)
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    if a.get_actor_label().startswith("HubEnv_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

# bounds of user's buildings
min_x = min_y = 1e9
max_x = max_y = -1e9
hub_count = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not a.get_actor_label().startswith("HubMed_"):
        continue
    o, e = a.get_actor_bounds(False)
    min_x = min(min_x, o.x - e.x)
    max_x = max(max_x, o.x + e.x)
    min_y = min(min_y, o.y - e.y)
    max_y = max(max_y, o.y + e.y)
    hub_count += 1

if hub_count == 0:
    min_x, max_x, min_y, max_y = -2000, 2000, -2000, 2500

pad = 900.0
wall_min_x, wall_max_x = min_x - pad, max_x + pad
wall_min_y, wall_max_y = min_y - pad, max_y + pad
cx = (wall_min_x + wall_max_x) * 0.5
cy = (wall_min_y + wall_max_y) * 0.5
unreal.log("hub_bounds x=%.0f..%.0f y=%.0f..%.0f" % (min_x, max_x, min_y, max_y))

# hide template floor (keep collision via grass)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    label = a.get_actor_label()
    if label in ("Floor", "Hub_Floor"):
        a.set_actor_hidden_in_game(True)
        try:
            a.set_is_temporarily_hidden_in_editor(True)
        except Exception:
            pass
        # still enlarge collision plane under grass
        a.set_actor_location(unreal.Vector(cx, cy, -20), False, True)
        a.set_actor_scale3d(unreal.Vector(60, 60, 1))

# --- grass hex grid covering city + margin ---
grass = meshes.get("hex_grass")
# pointy-top hex spacing approx: width=HEX, height=HEX*sqrt(3)/2 for axial; KayKit hex often flat size ~1
# use square-ish packing with HEX*0.9 step for coverage
if grass:
    step = HEX * 0.85
    gx0 = wall_min_x - HEX
    gx1 = wall_max_x + HEX
    gy0 = wall_min_y - HEX
    gy1 = wall_max_y + HEX
    n = 0
    row = 0
    y = gy0
    while y <= gy1:
        xoff = (step * 0.5) if (row % 2) else 0.0
        x = gx0 + xoff
        while x <= gx1:
            spawn_kay(grass, x, y, 0, "HubEnv_Grass_%d" % n, SCALE)
            n += 1
            x += step
        y += step * 0.75
        row += 1
    unreal.log("grass_tiles=" + str(n))

# --- city walls rectangle ---
wall = meshes.get("wall_straight")
corner = meshes.get("wall_corner_A_outside") or meshes.get("wall_corner_B_outside")
gate = meshes.get("wall_straight_gate") or wall
# estimate wall segment length from mesh bounds at scale
seg = HEX  # ~ one hex edge length after scale; tune
if wall:
    # probe length along local after spawn trick: use asset bounds * scale
    bb = wall.get_bounding_box()
    # after roll 90, length along X roughly max(x extent, z extent)*scale
    raw_len = max(bb.max.x - bb.min.x, bb.max.z - bb.min.z, bb.max.y - bb.min.y)
    seg = max(raw_len * SCALE * 0.95, 400.0)
    unreal.log("wall_seg=" + str(seg))

def place_wall_line(x0, y0, x1, y1, outward_yaw, label_prefix, use_gate=False):
    dx = x1 - x0
    dy = y1 - y0
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1:
        return
    ux, uy = dx / length, dy / length
    count = max(1, int(round(length / seg)))
    actual = length / count
    for i in range(count):
        t = (i + 0.5) * actual
        x = x0 + ux * t
        y = y0 + uy * t
        mesh = gate if (use_gate and i == count // 2) else wall
        if not mesh:
            continue
        spawn_kay(mesh, x, y, outward_yaw, "%s_%d" % (label_prefix, i))

if wall:
    # south (min y): face -Y -> yaw 180; north max y face +Y yaw 0; west min x face -X yaw -90; east +X yaw 90
    # outward normals for wall facing
    place_wall_line(wall_min_x, wall_min_y, wall_max_x, wall_min_y, 180, "HubEnv_WallS", use_gate=True)
    place_wall_line(wall_min_x, wall_max_y, wall_max_x, wall_max_y, 0, "HubEnv_WallN")
    place_wall_line(wall_min_x, wall_min_y, wall_min_x, wall_max_y, -90, "HubEnv_WallW")
    place_wall_line(wall_max_x, wall_min_y, wall_max_x, wall_max_y, 90, "HubEnv_WallE")
    if corner:
        spawn_kay(corner, wall_min_x, wall_min_y, 180, "HubEnv_CornerSW")
        spawn_kay(corner, wall_max_x, wall_min_y, 90, "HubEnv_CornerSE")
        spawn_kay(corner, wall_min_x, wall_max_y, -90, "HubEnv_CornerNW")
        spawn_kay(corner, wall_max_x, wall_max_y, 0, "HubEnv_CornerNE")
    unreal.log("walls placed")

# --- trees & rocks around outside and a few inside ---
tree_list = [meshes.get(k) for k in ["tree_single_A", "tree_single_B", "trees_A_small", "trees_A_medium", "trees_B_small"] if meshes.get(k)]
rock_list = [meshes.get(k) for k in ["rock_single_A", "rock_single_B", "rock_single_C"] if meshes.get(k)]

def ring_points(radius, n, yaw0=0):
    pts = []
    for i in range(n):
        ang = math.radians(yaw0 + i * (360.0 / n))
        pts.append((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius, math.degrees(ang)))
    return pts

ti = 0
outer_r = max(wall_max_x - wall_min_x, wall_max_y - wall_min_y) * 0.55 + 600
for x, y, ang in ring_points(outer_r, 16):
    if tree_list:
        spawn_kay(tree_list[ti % len(tree_list)], x, y, ang, "HubEnv_Tree_%d" % ti)
        ti += 1
# inner courtyard trees (sparse)
inner_r = max(400.0, min(wall_max_x - wall_min_x, wall_max_y - wall_min_y) * 0.22)
for x, y, ang in ring_points(inner_r, 6, 20):
    # skip very center (well)
    if abs(x - cx) < 200 and abs(y - cy) < 200:
        continue
    if tree_list:
        spawn_kay(tree_list[ti % len(tree_list)], x, y, ang, "HubEnv_Tree_%d" % ti, SCALE * 0.85)
        ti += 1

ri = 0
for x, y, ang in ring_points(outer_r * 0.85, 10, 12):
    if rock_list:
        spawn_kay(rock_list[ri % len(rock_list)], x, y, ang, "HubEnv_Rock_%d" % ri, SCALE * 0.7)
        ri += 1

# background hills / mountains farther out
bg = [
    ("hills_A_trees", cx - 4500, cy + 2000, 30, SCALE * 1.2),
    ("hills_B", cx + 4200, cy + 1800, -20, SCALE * 1.2),
    ("mountain_A_grass_trees", cx, cy + 6500, 180, SCALE * 1.5),
    ("mountain_B_grass", cx - 5500, cy - 3000, 45, SCALE * 1.4),
    ("mountain_A_grass_trees", cx + 5500, cy - 2500, -45, SCALE * 1.4),
]
for name, x, y, yaw, sc in bg:
    m = meshes.get(name)
    if m:
        spawn_kay(m, x, y, yaw, "HubEnv_BG_" + name, sc)

# props near plaza
prop_spots = [
    ("barrel", cx + 350, cy - 200, 10),
    ("crate_A_big", cx + 420, cy - 80, 40),
    ("crate_B_small", cx - 380, cy + 150, -15),
    ("sack", cx - 300, cy - 120, 70),
    ("flag_blue", wall_min_x + 200, wall_min_y + 200, 0),
    ("flag_blue", wall_max_x - 200, wall_min_y + 200, 0),
]
for name, x, y, yaw in prop_spots:
    m = meshes.get(name)
    if m:
        spawn_kay(m, x, y, yaw, "HubEnv_Prop_" + name, SCALE)

# sky / atmosphere if missing
has_sky = False
has_fog = False
has_light = False
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    cn = a.get_class().get_name()
    if "SkySphere" in cn or "BP_Sky" in cn or "SkyAtmosphere" in cn:
        has_sky = True
    if "ExponentialHeightFog" in cn:
        has_fog = True
    if "DirectionalLight" in cn:
        has_light = True

if not has_light:
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 500), unreal.Rotator(-40, 30, 0)
    )
    if sun:
        sun.set_actor_label("HubEnv_Sun")

if not has_fog:
    fog = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)
    )
    if fog:
        fog.set_actor_label("HubEnv_Fog")

# try load engine sky sphere blueprint
if not has_sky:
    sky_bp = unreal.EditorAssetLibrary.load_asset("/Engine/EngineSky/BP_Sky_Sphere")
    if not sky_bp:
        sky_bp = unreal.EditorAssetLibrary.load_asset("/Engine/EngineEnvironments/BP_Sky_Sphere")
    if sky_bp:
        sky = unreal.EditorLevelLibrary.spawn_actor_from_object(sky_bp, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        if sky:
            sky.set_actor_label("HubEnv_Sky")
            unreal.log("spawned sky sphere")
    else:
        # fallback skylight + sky atmosphere if available
        try:
            sl = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.SkyLight, unreal.Vector(0, 0, 200), unreal.Rotator(0, 0, 0)
            )
            if sl:
                sl.set_actor_label("HubEnv_SkyLight")
        except Exception:
            pass
        unreal.log_warning("no BP_Sky_Sphere found")

# player start stay near center plaza
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(cx + 150, cy + 150, 100), False, True)
        break

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory(DEST)
unreal.log("HUB ENV DRESS DONE meshes=%d hub_buildings=%d" % (len(meshes), hub_count))
