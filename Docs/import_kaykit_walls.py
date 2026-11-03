# -*- coding: utf-8 -*-
"""Import KayKit Medieval Hexagon walls and rebuild Map_Hub enclosure at default ThirdPerson scale.

Target: wall height ~380cm (~2x ThirdPerson ~192cm pawn). Courtyard half-extent 3000cm.
NOT the old SCALE=500 hex-tile dressing scale.
"""
from __future__ import print_function
import unreal
import math
import os
import traceback

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj\buildings\neutral"
TEX_PNG = os.path.join(OBJ_DIR, "hexagons_medieval.png")
DEST = "/Game/Environments/KayKitMedieval"
DEST_WALLS = DEST + "/Walls"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Buildings"  # existing atlas mat lives here
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_kaykit_walls.log"

COURTYARD_HALF = 3000.0  # cm -> 60m across
WALL_HEIGHT_TARGET = 380.0  # cm ~3.8m
GROUND_Z = 0.0
SPAWN = unreal.Vector(0.0, 0.0, 100.0)

# KayKit OBJ is Blender Y-up. UE4 Wavefront often keeps axes as-is.
# Roll +90 maps local Y -> world Z (upright).
ROLL_UPRIGHT = 90.0  # applied as Rotator(roll=90) — UE4 py arg order is (roll,pitch,yaw)

WALL_FILES = [
    "wall_straight.obj",
    "wall_straight_gate.obj",
    "wall_corner_A_outside.obj",
    "wall_corner_B_outside.obj",
    "wall_corner_A_gate.obj",
    "fence_stone_straight.obj",
]

OWN_WALL_PREFIXES = (
    "HubWall_", "HubCorner_", "HubGate_",
)

KEEP_PREFIXES = (
    "HubShop_", "HubMarker_", "HubLabel_", "HubFloor_", "HubPlaceholder_",
    "Hub_Sun", "Hub_Sky", "Hub_HeightFog", "Hub_PlayerStart",
)

_log_lines = []


def log(msg):
    line = str(msg)
    _log_lines.append(line)
    try:
        unreal.log("KAYWALLS: " + line)
    except Exception:
        print("KAYWALLS: " + line)


def flush_log():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(_log_lines) + "\n")
    except Exception as e:
        try:
            unreal.log_warning("log write fail: " + str(e))
        except Exception:
            pass


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def spawn(cls, loc, rot=None):
    if rot is None:
        rot = unreal.Rotator(0.0, 0.0, 0.0)
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        return sub.spawn_actor_from_class(cls, loc, rot)
    except Exception:
        return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)


def destroy(actor):
    try:
        unreal.EditorLevelLibrary.destroy_actor(actor)
    except Exception:
        try:
            sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            sub.destroy_actor(actor)
        except Exception:
            pass


def mesh_size(mesh):
    if not mesh:
        return (1.0, 1.0, 1.0)
    try:
        bbox = mesh.get_bounding_box()
        sx = abs(bbox.max.x - bbox.min.x)
        sy = abs(bbox.max.y - bbox.min.y)
        sz = abs(bbox.max.z - bbox.min.z)
        return (max(sx, 0.001), max(sy, 0.001), max(sz, 0.001))
    except Exception as e:
        log("mesh_size fail: " + str(e))
        return (1.0, 1.0, 1.0)


def mesh_mins(mesh):
    bbox = mesh.get_bounding_box()
    return (bbox.min.x, bbox.min.y, bbox.min.z)


def import_obj(abs_path, dest_path, asset_name):
    full = dest_path + "/" + asset_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("exists " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    if not os.path.isfile(abs_path):
        log("MISSING file " + abs_path)
        return None
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
        try:
            sm.set_editor_property("import_uniform_scale", 1.0)
        except Exception:
            pass
        # Do NOT convert scene — keep KayKit Y-up; we Roll+90 at spawn
        try:
            sm.set_editor_property("convert_scene", False)
        except Exception:
            pass
        try:
            sm.set_editor_property("force_front_x_axis", False)
        except Exception:
            pass
        options.set_editor_property("static_mesh_import_data", sm)
        task.options = options
    except Exception as e:
        log("options warn: " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("imported " + full)
        return unreal.EditorAssetLibrary.load_asset(full)
    # fallback: search dest
    try:
        for a in unreal.EditorAssetLibrary.list_assets(dest_path, False, False):
            if asset_name.lower() in a.lower():
                log("found as " + a)
                return unreal.EditorAssetLibrary.load_asset(a)
    except Exception:
        pass
    log("IMPORT FAIL " + abs_path)
    return None


def import_texture_if_needed():
    tex_path = DEST_TEX + "/T_hexagons_medieval"
    if unreal.EditorAssetLibrary.does_asset_exist(tex_path):
        log("tex exists " + tex_path)
        return unreal.EditorAssetLibrary.load_asset(tex_path)
    if not os.path.isfile(TEX_PNG):
        log("tex png missing " + TEX_PNG)
        return None
    ensure_dir(DEST_TEX)
    task = unreal.AssetImportTask()
    task.filename = TEX_PNG
    task.destination_path = DEST_TEX
    task.destination_name = "T_hexagons_medieval"
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(tex_path):
        log("imported tex " + tex_path)
        return unreal.EditorAssetLibrary.load_asset(tex_path)
    return None


def resolve_material():
    candidates = [
        DEST_MAT + "/M_KayKitMedieval",
        DEST_MAT + "/hexagons_medieval",
        DEST_WALLS + "/hexagons_medieval",
        DEST_WALLS + "/M_KayKitWall",
    ]
    for p in candidates:
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mat = unreal.EditorAssetLibrary.load_asset(p)
            log("using material " + p)
            return mat
    # create simple material with texture
    tex = import_texture_if_needed()
    try:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.MaterialFactoryNew()
        mat = asset_tools.create_asset("M_KayKitWall", DEST_WALLS, unreal.Material, factory)
        if mat and tex:
            # Best-effort: leave default; assign texture via expression is complex in py
            log("created blank M_KayKitWall (assign tex manually if pink)")
        if mat:
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
            return mat
    except Exception as e:
        log("create mat fail: " + str(e))
    return None


def assign_mat(mesh, mat):
    if not mesh or not mat:
        return
    try:
        mesh.set_material(0, mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    except Exception as e:
        log("set_material fail: " + str(e))


def detect_axes(mesh, label="wall"):
    """Return (len_axis, height_axis, thick_axis, len, height, thick) using KayKit conventions.

    Native KayKit wall_straight (Y-up): X=length~2, Y=height~1.1, Z=thickness~0.8
    If importer converted to Z-up: X=length, Y=thickness, Z=height
    """
    sx, sy, sz = mesh_size(mesh)
    mn = mesh_mins(mesh)
    log("%s bbox size=%.4f x %.4f x %.4f  min=(%.4f,%.4f,%.4f)" % (
        label, sx, sy, sz, mn[0], mn[1], mn[2]))

    dims = [("x", sx, mn[0]), ("y", sy, mn[1]), ("z", sz, mn[2])]
    # Height: prefer axis whose min is near 0 and extent ~0.8..1.5 (KayKit wall height units)
    height_cand = None
    for name, ext, vmin in dims:
        if abs(vmin) < 0.15 and 0.6 <= ext <= 1.6:
            height_cand = (name, ext)
            break
    if height_cand is None:
        # fallback: middle extent often height; or Y if Y-up still
        sorted_dims = sorted(dims, key=lambda d: d[1])
        # thickness smallest, length largest, height middle — for wall_straight
        height_cand = (sorted_dims[1][0], sorted_dims[1][1])

    height_axis, height = height_cand
    remaining = [(n, e) for n, e, _ in dims if n != height_axis]
    remaining.sort(key=lambda d: d[1], reverse=True)
    len_axis, length = remaining[0]
    thick_axis, thick = remaining[1]
    log("%s axes: len=%s(%.3f) height=%s(%.3f) thick=%s(%.3f)" % (
        label, len_axis, length, height_axis, height, thick_axis, thick))
    return len_axis, height_axis, thick_axis, length, height, thick


def compute_scale(height_native):
    if height_native < 0.01:
        height_native = 1.1
    s = WALL_HEIGHT_TARGET / height_native
    log("scale=%.4f  (target_h=%.1f / native_h=%.4f)" % (s, WALL_HEIGHT_TARGET, height_native))
    # Sanity: refuse absurd scales
    if s < 50.0 or s > 800.0:
        log("WARN scale out of expected 50..800 range for KayKit units; clamping logic may apply")
    return s


def snap_bottom(actor, ground_z=GROUND_Z):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True
    )


def place_segment(mesh, loc, yaw, scale, label):
    # Pitch 0, Yaw, Roll 90 for Y-up KayKit OBJ
    rot = unreal.Rotator(ROLL_UPRIGHT, 0.0, float(yaw))  # roll,pitch,yaw
    actor = spawn(unreal.StaticMeshActor, loc, rot)
    if not actor:
        log("spawn fail " + label)
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_editor_property("collision_profile_name", "BlockAll")
    except Exception:
        pass
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:
        pass
    snap_bottom(actor, GROUND_Z)
    return actor


def clear_old_walls():
    destroyed = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label() or ""
        for p in OWN_WALL_PREFIXES:
            if lab.startswith(p):
                destroy(a)
                destroyed += 1
                break
        else:
            # Also remove leftover Kenney-only wall cubes if any labeled Wall/Arena
            if lab.startswith("Wall") or lab == "Arena":
                destroy(a)
                destroyed += 1
    log("destroyed old wall actors=%d" % destroyed)
    return destroyed


def ensure_floor_and_lights():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    has_floor = False
    has_dir = False
    has_sky = False
    for a in actors:
        lab = a.get_actor_label() or ""
        cls = a.get_class().get_name()
        if lab.startswith("HubFloor_") or lab in ("Floor", "Hub_Floor"):
            has_floor = True
            a.set_actor_label("HubFloor_Ground")
            a.set_actor_location(unreal.Vector(0.0, 0.0, -2.0), False, True)
            a.set_actor_scale3d(unreal.Vector(70.0, 70.0, 1.0))
        if "DirectionalLight" in cls:
            has_dir = True
        if "SkyLight" in cls:
            has_sky = True
    if not has_floor:
        floor = spawn(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -2.0))
        if floor:
            plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
            floor.static_mesh_component.set_static_mesh(plane)
            floor.set_actor_scale3d(unreal.Vector(70.0, 70.0, 1.0))
            floor.set_actor_label("HubFloor_Ground")
            log("spawned HubFloor_Ground")
    if not has_dir:
        light = spawn(unreal.DirectionalLight, unreal.Vector(0, 0, 800), unreal.Rotator(-45, -35, 0))
        if light:
            light.set_actor_label("Hub_Sun")
    if not has_sky:
        sky = spawn(unreal.SkyLight, unreal.Vector(0, 0, 600))
        if sky:
            sky.set_actor_label("Hub_SkyLight")


def ensure_player_start():
    starts = [a for a in unreal.EditorLevelLibrary.get_all_level_actors()
              if "PlayerStart" in a.get_class().get_name()]
    if not starts:
        ps = spawn(unreal.PlayerStart, SPAWN, unreal.Rotator(0, 90, 0))
        if ps:
            ps.set_actor_label("Hub_PlayerStart")
            log("spawned Hub_PlayerStart")
    else:
        for i, ps in enumerate(starts):
            if i == 0:
                ps.set_actor_location(SPAWN, False, True)
                try:
                    ps.set_actor_rotation(unreal.Rotator(0, 90, 0), False)
                except Exception:
                    pass
                ps.set_actor_label("Hub_PlayerStart")
            else:
                destroy(ps)


def ensure_shops_present():
    """Keep existing HubShop_* if present; otherwise recreate simple cubes."""
    existing = [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors()]
    shops = [
        ("Weapon", unreal.Vector(-1200, -800, 0), (0.95, 0.25, 0.15)),
        ("Armor", unreal.Vector(1200, -800, 0), (0.2, 0.45, 0.95)),
        ("Health", unreal.Vector(0, 1200, 0), (0.2, 0.85, 0.35)),
    ]
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for key, loc, color in shops:
        label = "HubShop_%s" % key
        if any(e == label for e in existing):
            continue
        a = spawn(unreal.StaticMeshActor, loc)
        if not a:
            continue
        a.set_actor_label(label)
        a.static_mesh_component.set_static_mesh(cube)
        a.set_actor_scale3d(unreal.Vector(1.5, 1.5, 2.0))
        snap_bottom(a)
        log("recreated shop " + label)


def set_gm_hub_pawn():
    if not unreal.EditorAssetLibrary.does_asset_exist(GM_HUB):
        log("GM_Hub missing")
        return
    gm = unreal.EditorAssetLibrary.load_asset(GM_HUB)
    tp = unreal.EditorAssetLibrary.load_asset(TP_CHAR)
    if not gm or not tp:
        log("GM/TP load fail")
        return
    try:
        gc = None
        try:
            gc = gm.generated_class()
        except Exception:
            try:
                gc = gm.get_editor_property("generated_class")
            except Exception:
                pass
        if gc:
            cdo = unreal.get_default_object(gc)
            cdo.set_editor_property("default_pawn_class", tp)
            unreal.EditorAssetLibrary.save_loaded_asset(gm)
            log("GM_Hub DefaultPawnClass = ThirdPersonCharacter")
    except Exception as e:
        log("set pawn: " + str(e))


def set_world_gamemode():
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        ws = world.get_world_settings()
        gm = unreal.EditorAssetLibrary.load_asset(GM_HUB)
        if gm:
            try:
                gc = gm.generated_class()
            except Exception:
                gc = gm.get_editor_property("generated_class")
            if gc:
                ws.set_editor_property("default_game_mode", gc)
                log("WorldSettings DefaultGameMode = GM_Hub")
    except Exception as e:
        log("set gm: " + str(e))


def build_enclosure(meshes, scale, wall_len_native, wall_height_native):
    wall = meshes.get("wall_straight")
    gate = meshes.get("wall_straight_gate")
    corner_a = meshes.get("wall_corner_A_outside")
    corner_b = meshes.get("wall_corner_B_outside")
    if not wall:
        log("ERROR no wall_straight")
        return 0, 0, 0

    seg_len = wall_len_native * scale
    seg_h = wall_height_native * scale
    half = COURTYARD_HALF
    # thickness estimate ~0.8 native
    thick = 0.8 * scale
    inset = thick * 0.5

    # Corner footprint: use corner length along one arm (~1.0-1.8 native)
    corner_span = 1.2 * scale  # leave room at each end
    usable = half * 2.0 - 2.0 * corner_span
    n = max(3, int(round(usable / seg_len)))
    # Recenter so segments span the usable range
    start = -half + corner_span + seg_len * 0.5
    end = half - corner_span - seg_len * 0.5
    if n <= 1:
        positions = [0.0]
    else:
        positions = [start + (end - start) * (i / float(n - 1)) for i in range(n)]

    log("enclosure: seg_len=%.1fcm seg_h=%.1fcm n_per_side=%d scale=%.3f" % (
        seg_len, seg_h, n, scale))

    placed = []

    def side_label(axis, sign):
        if axis == "x" and sign > 0:
            return "S"
        if axis == "x" and sign < 0:
            return "N"
        if axis == "y" and sign > 0:
            return "E"
        return "W"

    def place_side(axis, sign, yaw, include_gate=False):
        gate_i = n // 2 if include_gate else -1
        for i, t in enumerate(positions):
            if axis == "x":
                loc = unreal.Vector(t, sign * (half - inset), 0.0)
            else:
                loc = unreal.Vector(sign * (half - inset), t, 0.0)

            side = side_label(axis, sign)
            if include_gate and i == gate_i and gate:
                label = "HubGate_DungeonEntrance"
                a = place_segment(gate, loc, yaw, scale, label)
                if a:
                    placed.append(a)
                    log("gate %s at (%.0f,%.0f)" % (label, loc.x, loc.y))
                # Keep / ensure entrance marker just inside
                if axis == "x":
                    mloc = unreal.Vector(t, sign * (half - inset - 200.0), 50.0)
                else:
                    mloc = unreal.Vector(sign * (half - inset - 200.0), t, 50.0)
                # Only add marker if missing
                have = any((x.get_actor_label() or "") == "HubMarker_DungeonEntrance"
                           for x in unreal.EditorLevelLibrary.get_all_level_actors())
                if not have:
                    try:
                        tgt = spawn(unreal.TargetPoint, mloc)
                        if tgt:
                            tgt.set_actor_label("HubMarker_DungeonEntrance")
                    except Exception:
                        pass
            else:
                label = "HubWall_%s_%02d" % (side, i)
                a = place_segment(wall, loc, yaw, scale, label)
                if a:
                    placed.append(a)

    # After Roll+90, local X (length) aligns with world X at yaw=0
    # North/South walls (run along X): yaw 0
    # East/West walls (run along Y): yaw 90
    place_side("x", -1.0, 0.0, include_gate=False)   # North
    place_side("x", +1.0, 0.0, include_gate=True)    # South + gate
    place_side("y", -1.0, 90.0, include_gate=False)  # West
    place_side("y", +1.0, 90.0, include_gate=False)  # East

    # Corners — try A_outside at four corners with 90deg steps
    cmesh = corner_a or corner_b
    if cmesh:
        corners = [
            (unreal.Vector(-half + inset, -half + inset, 0.0), 0.0, "NW"),
            (unreal.Vector(half - inset, -half + inset, 0.0), 90.0, "NE"),
            (unreal.Vector(half - inset, half - inset, 0.0), 180.0, "SE"),
            (unreal.Vector(-half + inset, half - inset, 0.0), -90.0, "SW"),
        ]
        # Alternate A/B if both present for variety
        for i, (loc, yaw, name) in enumerate(corners):
            m = corner_a if (i % 2 == 0 or not corner_b) else corner_b
            if not m:
                m = cmesh
            a = place_segment(m, loc, yaw, scale, "HubCorner_" + name)
            if a:
                placed.append(a)
    else:
        log("no corner mesh")

    # Verify one wall actor height vs target
    sample_h = 0.0
    for a in placed:
        lab = a.get_actor_label() or ""
        if lab.startswith("HubWall_"):
            o, e = a.get_actor_bounds(False)
            sample_h = e.z * 2.0
            log("sample actor %s world_height~%.1fcm (extent.z*2) loc.z=%.1f" % (
                lab, sample_h, a.get_actor_location().z))
            break

    log("placed wall actors=%d" % len(placed))
    return len(placed), seg_len, sample_h if sample_h > 0 else seg_h


def count_summary():
    walls = corners = gates = shops = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab.startswith("HubWall_"):
            walls += 1
        elif lab.startswith("HubCorner_"):
            corners += 1
        elif lab.startswith("HubGate_"):
            gates += 1
        elif lab.startswith("HubShop_"):
            shops += 1
    return {"walls": walls, "corners": corners, "gates": gates, "shops": shops}


def main():
    log("=== import_kaykit_walls start ===")
    log("target wall_h=%.0fcm courtyard_half=%.0fcm pawn~192cm" % (
        WALL_HEIGHT_TARGET, COURTYARD_HALF))

    ensure_dir(DEST)
    ensure_dir(DEST_WALLS)
    ensure_dir(DEST_TEX)

    import_texture_if_needed()
    mat = resolve_material()

    meshes = {}
    for fname in WALL_FILES:
        path = os.path.join(OBJ_DIR, fname)
        name = os.path.splitext(fname)[0]
        m = import_obj(path, DEST_WALLS, name)
        if m:
            assign_mat(m, mat)
            meshes[name] = m
            unreal.EditorAssetLibrary.save_loaded_asset(m)

    log("imported meshes: " + ", ".join(sorted(meshes.keys())))
    if "wall_straight" not in meshes:
        log("FATAL: wall_straight missing")
        flush_log()
        return

    len_ax, h_ax, t_ax, wall_len, wall_h, wall_th = detect_axes(
        meshes["wall_straight"], "wall_straight")
    scale = compute_scale(wall_h)

    # Also log gate/corner sizes
    for key in ("wall_straight_gate", "wall_corner_A_outside", "wall_corner_B_outside"):
        if key in meshes:
            detect_axes(meshes[key], key)

    # Load map
    if not unreal.EditorAssetLibrary.does_asset_exist(HUB_MAP):
        log("Map_Hub missing; creating")
        try:
            unreal.EditorLevelLibrary.new_level(HUB_MAP)
        except Exception as e:
            log("new_level: " + str(e))
            factory = unreal.WorldFactory()
            unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                "Map_Hub", "/Game/Maps/Hub", unreal.World, factory)
            unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    else:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    log("Map_Hub loaded")

    clear_old_walls()
    ensure_floor_and_lights()
    n_placed, seg_len, world_h = build_enclosure(meshes, scale, wall_len, wall_h)
    ensure_player_start()
    ensure_shops_present()
    set_gm_hub_pawn()
    set_world_gamemode()

    unreal.EditorLevelLibrary.save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception as e:
        log("save_dirty: " + str(e))
    try:
        unreal.EditorAssetLibrary.save_directory(DEST_WALLS)
    except Exception as e:
        log("save_dir: " + str(e))

    summary = count_summary()
    log("SUMMARY " + str(summary))
    log("SCALE=%.4f native_h=%.4f native_len=%.4f -> seg_len=%.1fcm world_wall_h~%.1fcm" % (
        scale, wall_h, wall_len, seg_len, world_h))
    log("vs ThirdPerson ~192cm tall -> wall ~%.1fx character height" % (world_h / 192.0))
    log("import paths under " + DEST_WALLS)
    log("VERIFY: Open Map_Hub, Outliner HubWall_/HubCorner_/HubGate_, PIE walk next to wall")
    log("=== import_kaykit_walls DONE ===")
    flush_log()


try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc())
    flush_log()
    raise
