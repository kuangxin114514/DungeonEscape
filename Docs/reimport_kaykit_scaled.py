import unreal
import os
import shutil

# ---------------------------------------------------------------------------
# KayKit Medieval Hexagon: reimport at human scale + clean Map_Hub plaza
# Target: house ~7-8m (OBJ Y~0.93 * 800 ~= 744 uu). Actor scale stays 1.
# ---------------------------------------------------------------------------

OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj\buildings\blue"
TEX_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Textures\hexagons_medieval.png"
TEMP_OBJ = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\_kaykit_scaled_obj"
DEST = "/Game/Environments/KayKitMedieval"
DEST_BLD = DEST + "/Buildings"
DEST_TEX = DEST + "/Textures"
HUB_MAP = "/Game/Maps/Hub/Map_Hub"

IMPORT_SCALE = 800.0  # primary bake target (cm)
MIN_OK_HEIGHT = 400.0  # if mesh tall axis < this, scale did not bake
ACTOR_SCALE = 1.0
SPAWN_PITCH = -90.0  # Y-up OBJ -> upright in UE Z-up (Roll=-90 left them sideways)

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

# Sparse square plaza around origin (uu). Yaw only; Roll applied separately.
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


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def mesh_extents(mesh):
    """Return (sx, sy, sz, bbox) of axis-aligned bbox size."""
    try:
        bb = mesh.get_bounding_box()
        return (
            abs(bb.max.x - bb.min.x),
            abs(bb.max.y - bb.min.y),
            abs(bb.max.z - bb.min.z),
            bb,
        )
    except Exception as e:
        unreal.log_warning("bbox fail: " + str(e))
        return (0.0, 0.0, 0.0, None)


def tallest(sx, sy, sz):
    return max(sx, sy, sz)


def write_scaled_obj(src_path, dst_path, scale):
    """Multiply vertex coords by scale; copy faces/UVs. Bakes size into geometry."""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    src_mtl = os.path.splitext(src_path)[0] + ".mtl"
    if os.path.isfile(src_mtl):
        shutil.copy2(src_mtl, os.path.splitext(dst_path)[0] + ".mtl")
    out_lines = []
    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    x = float(parts[1]) * scale
                    y = float(parts[2]) * scale
                    z = float(parts[3]) * scale
                    rest = " ".join(parts[4:]) if len(parts) > 4 else ""
                    if rest:
                        out_lines.append("v %.6f %.6f %.6f %s\n" % (x, y, z, rest))
                    else:
                        out_lines.append("v %.6f %.6f %.6f\n" % (x, y, z))
                else:
                    out_lines.append(line)
            else:
                out_lines.append(line)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)


def import_obj(abs_path, dest_path, asset_name, uniform_scale):
    full = dest_path + "/" + asset_name
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
        sm.set_editor_property("import_uniform_scale", float(uniform_scale))
        for prop, val in [
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
        unreal.log_warning("import options: " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    for a in unreal.EditorAssetLibrary.list_assets(dest_path, True, False):
        if asset_name.lower() in a.lower():
            return unreal.EditorAssetLibrary.load_asset(a)
    return None


def apply_build_scale(mesh, scale):
    """Fallback: bake via LOD BuildScale3D (EditorScriptingUtilities)."""
    try:
        bs = unreal.EditorStaticMeshLibrary.get_lod_build_settings(mesh, 0)
        bs.set_editor_property("build_scale_3d", unreal.Vector(scale, scale, scale))
        unreal.EditorStaticMeshLibrary.set_lod_build_settings(mesh, 0, bs)
        try:
            unreal.EditorStaticMeshLibrary.set_generate_lightmap_uv(mesh, True)
        except Exception:
            pass
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        return True
    except Exception as e:
        unreal.log_warning("build_scale: " + str(e))
        return False


def import_texture(abs_path, dest_path, asset_name):
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
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    return None


def ensure_material(tex):
    mat_path = DEST_BLD + "/M_KayKitMedieval"
    if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    else:
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "M_KayKitMedieval", DEST_BLD, unreal.Material, factory
        )
    if not mat:
        return None
    if tex:
        try:
            expr = unreal.MaterialEditingLibrary.create_material_expression(
                mat, unreal.MaterialExpressionTextureSample, -384, 0
            )
            expr.set_editor_property("texture", tex)
            unreal.MaterialEditingLibrary.connect_material_property(
                expr, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
            )
            unreal.MaterialEditingLibrary.recompile_material(mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception as e:
            unreal.log_warning("material wire: " + str(e))
    return mat


def snap_to_ground(actor, ground_z):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True
    )


# ============================= RUN =========================================
unreal.log("=== KAYKIT SCALED REIMPORT START scale=%s ===" % IMPORT_SCALE)

ensure_dir(DEST)
ensure_dir(DEST_BLD)
ensure_dir(DEST_TEX)

tex = None
if os.path.isfile(TEX_PATH):
    tex = import_texture(TEX_PATH, DEST_TEX, "T_hexagons_medieval")
    unreal.log("TEX=" + str(tex))
else:
    unreal.log_warning("missing texture " + TEX_PATH)

mat = ensure_material(tex)
unreal.log("MAT=" + str(mat))

imported = {}
bake_method = "import_uniform_scale"

# Pass 1: import originals with import_uniform_scale
for fname in BUILDINGS:
    src = os.path.join(OBJ_DIR, fname)
    if not os.path.isfile(src):
        unreal.log_warning("missing " + src)
        continue
    name = os.path.splitext(fname)[0]
    mesh = import_obj(src, DEST_BLD, name, IMPORT_SCALE)
    if mesh:
        imported[name] = mesh
        sx, sy, sz, bb = mesh_extents(mesh)
        unreal.log("pass1 %s extents=%.1f,%.1f,%.1f tall=%.1f" % (name, sx, sy, sz, tallest(sx, sy, sz)))

# Check home / church
need_fallback = False
for probe in ("building_home_A_blue", "building_church_blue"):
    m = imported.get(probe)
    if not m:
        need_fallback = True
        continue
    sx, sy, sz, _ = mesh_extents(m)
    if tallest(sx, sy, sz) < MIN_OK_HEIGHT:
        need_fallback = True
        unreal.log_warning("pass1 too small: %s tall=%.1f" % (probe, tallest(sx, sy, sz)))

if need_fallback:
    unreal.log("FALLBACK: BuildScale3D x%s" % IMPORT_SCALE)
    bake_method = "build_scale_3d"
    for name, mesh in list(imported.items()):
        apply_build_scale(mesh, IMPORT_SCALE)
        sx, sy, sz, _ = mesh_extents(mesh)
        unreal.log("pass2build %s tall=%.1f" % (name, tallest(sx, sy, sz)))
    still_small = False
    for probe in ("building_home_A_blue", "building_church_blue"):
        m = imported.get(probe)
        if not m:
            still_small = True
            continue
        sx, sy, sz, _ = mesh_extents(m)
        if tallest(sx, sy, sz) < MIN_OK_HEIGHT:
            still_small = True
    if still_small:
        unreal.log("FALLBACK2: pre-scale OBJ vertices x%s then reimport scale=1" % IMPORT_SCALE)
        bake_method = "prescale_obj_vertices"
        if os.path.isdir(TEMP_OBJ):
            shutil.rmtree(TEMP_OBJ, ignore_errors=True)
        os.makedirs(TEMP_OBJ, exist_ok=True)
        try:
            shutil.copy2(TEX_PATH, os.path.join(TEMP_OBJ, "hexagons_medieval.png"))
        except Exception:
            pass
        imported = {}
        for fname in BUILDINGS:
            src = os.path.join(OBJ_DIR, fname)
            if not os.path.isfile(src):
                continue
            name = os.path.splitext(fname)[0]
            dst = os.path.join(TEMP_OBJ, fname)
            write_scaled_obj(src, dst, IMPORT_SCALE)
            mesh = import_obj(dst, DEST_BLD, name, 1.0)
            if mesh:
                imported[name] = mesh
                sx, sy, sz, _ = mesh_extents(mesh)
                unreal.log("pass3 %s tall=%.1f" % (name, tallest(sx, sy, sz)))

# Assign material
for name, mesh in imported.items():
    if mat:
        try:
            mesh.set_material(0, mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        except Exception as e:
            unreal.log_warning("set_material " + name + ": " + str(e))

# Final bounds log
home = imported.get("building_home_A_blue")
church = imported.get("building_church_blue")
home_ext = mesh_extents(home) if home else (0, 0, 0, None)
church_ext = mesh_extents(church) if church else (0, 0, 0, None)
unreal.log(
    "BOUNDS home_A=%.1f,%.1f,%.1f church=%.1f,%.1f,%.1f method=%s"
    % (home_ext[0], home_ext[1], home_ext[2], church_ext[0], church_ext[1], church_ext[2], bake_method)
)

# --------------------------- Map_Hub dress ---------------------------------
unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)

kill_prefixes = ("HubMed_", "HubKay_", "HubQ_", "HubK_", "HubEnv_", "KayKit")
destroyed = 0
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    lab = a.get_actor_label()
    if any(lab.startswith(p) for p in kill_prefixes):
        unreal.EditorLevelLibrary.destroy_actor(a)
        destroyed += 1
unreal.log("destroyed_dressing=" + str(destroyed))

ground_z = 0.0
floor_actor = None
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in ("Hub_Floor", "Floor", "HubGround_Plane") or "Floor" in lab:
        floor_actor = a
        loc = a.get_actor_location()
        ground_z = loc.z
        break

if floor_actor:
    floor_actor.set_actor_location(unreal.Vector(0.0, 0.0, ground_z), False, True)
    floor_actor.set_actor_scale3d(unreal.Vector(60.0, 60.0, 1.0))
    unreal.log("floor ok z=%.1f" % ground_z)
else:
    plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    if plane:
        floor_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)
        )
        floor_actor.set_actor_label("Hub_Floor")
        floor_actor.static_mesh_component.set_static_mesh(plane)
        floor_actor.set_actor_scale3d(unreal.Vector(60.0, 60.0, 1.0))
        ground_z = 0.0
        unreal.log("spawned Hub_Floor")

placed = 0
for key, x, y, yaw in LAYOUT:
    mesh = imported.get(key)
    if not mesh:
        unreal.log_warning("no mesh " + key)
        continue
    # Actor yaw only; mesh component Pitch -90 (Y-up -> Z-up, yaw-safe)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(float(x), float(y), float(ground_z)),
        unreal.Rotator(0.0, float(yaw), 0.0),
    )
    if not actor:
        continue
    actor.set_actor_label("HubKay_" + key)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    comp.set_relative_rotation(unreal.Rotator(float(SPAWN_PITCH), 0.0, 0.0), False, True)
    actor.set_actor_scale3d(unreal.Vector(ACTOR_SCALE, ACTOR_SCALE, ACTOR_SCALE))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception:
        pass
    snap_to_ground(actor, ground_z)
    origin, extent = actor.get_actor_bounds(False)
    unreal.log(
        "placed %s loc=(%.0f,%.0f,%.0f) extentZ=%.1f extentXY=%.1f,%.1f"
        % (key, actor.get_actor_location().x, actor.get_actor_location().y,
           actor.get_actor_location().z, extent.z * 2.0, extent.x * 2.0, extent.y * 2.0)
    )
    placed += 1

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        a.set_actor_location(unreal.Vector(200.0, 200.0, ground_z + 120.0), False, True)
        unreal.log("PlayerStart -> plaza center")
        break

unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory(DEST)

unreal.log(
    "KAYKIT READY method=%s import_scale=%.0f placed=%d home_tall=%.1f church_tall=%.1f"
    % (
        bake_method,
        IMPORT_SCALE,
        placed,
        tallest(home_ext[0], home_ext[1], home_ext[2]),
        tallest(church_ext[0], church_ext[1], church_ext[2]),
    )
)
