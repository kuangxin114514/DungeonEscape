# -*- coding: utf-8 -*-
"""Build Map_Hub as a four-walled Kenney city courtyard at default ThirdPerson scale."""
from __future__ import print_function
import unreal
import math
import os
import traceback

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
GM_HUB = "/Game/Core/GameFlow/GM_Hub"
TP_CHAR = "/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter"
KENNEY = "/Game/Environments/KenneyTown"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_hub_walls.log"

# Courtyard: ~60m across, walls ~3.5-4m tall (vs ~1.92m ThirdPerson pawn)
COURTYARD_HALF = 3000.0   # cm -> 60m across
WALL_HEIGHT_TARGET = 380.0  # cm ~3.8m city wall
GROUND_Z = 0.0
SPAWN = unreal.Vector(0.0, 0.0, 100.0)

# Labels we own / recreate each run
OWN_PREFIXES = (
    "HubWall_", "HubCorner_", "HubGate_", "HubShop_", "HubPlaceholder_",
    "HubFloor_", "Hub_Floor", "HubMed_", "HubEnv_", "HubKay_", "HubPlayerPreview",
    "HubLabel_", "HubMarker_",
)

KEEP_LABEL_EXACT = set()  # none forced

_log_lines = []


def log(msg):
    line = str(msg)
    _log_lines.append(line)
    try:
        unreal.log("HUBWALLS: " + line)
    except Exception:
        print("HUBWALLS: " + line)


def flush_log():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(_log_lines) + "\n")
    except Exception as e:
        try:
            unreal.log_warning("log write fail: " + str(e))
        except Exception:
            pass


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


def load_mesh(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None


def mesh_size(mesh):
    """Return (sx, sy, sz) full extents in cm of mesh local bounds."""
    if not mesh:
        return (100.0, 25.0, 200.0)
    try:
        bbox = mesh.get_bounding_box()
        sx = abs(bbox.max.x - bbox.min.x)
        sy = abs(bbox.max.y - bbox.min.y)
        sz = abs(bbox.max.z - bbox.min.z)
        if sx < 1.0:
            sx = 1.0
        if sy < 1.0:
            sy = 1.0
        if sz < 1.0:
            sz = 1.0
        return (sx, sy, sz)
    except Exception as e:
        log("mesh_size fail: " + str(e))
        return (100.0, 25.0, 200.0)


def set_mesh_on_actor(actor, mesh, scale_vec):
    if not actor:
        return
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(scale_vec)
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_editor_property("collision_profile_name", "BlockAll")
    except Exception:
        pass
    try:
        # Mobility movable so we can tweak in editor
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:
        pass


def snap_bottom_to_ground(actor, ground_z=GROUND_Z):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True
    )


def should_destroy(actor):
    lab = actor.get_actor_label() or ""
    cls = actor.get_class().get_name()
    name = actor.get_name()

    for p in OWN_PREFIXES:
        if lab.startswith(p) or lab == p.rstrip("_"):
            return True

    # Old KayKit clutter / knight preview
    if "KayKit" in lab or "KayKit" in name:
        return True
    if "HubMed" in lab or "HubEnv" in lab or "HubKay" in lab:
        return True
    if lab == "HubPlayerPreview":
        return True
    if "Knight" in lab and "PlayerStart" not in cls:
        # preview pawns / skeletal actors
        if "Character" in cls or "Skeletal" in cls or "BP_" in lab:
            return True

    # Template SM_Cube arena walls (not floor)
    if isinstance(actor, unreal.StaticMeshActor):
        try:
            smc = actor.static_mesh_component
            mesh = smc.static_mesh if smc else None
            if mesh and mesh.get_name() in ("SM_Cube", "Cube"):
                if lab not in ("Floor", "Hub_Floor", "HubFloor_Ground") and "Floor" not in lab:
                    # Keep only if labeled as floor
                    if "Wall" in lab or "Arena" in lab or lab.startswith("Cube"):
                        return True
                    # Large vertical cubes likely walls
                    sc = actor.get_actor_scale3d()
                    if sc.z >= 3.0 and (sc.x < 3.0 or sc.y < 3.0):
                        return True
        except Exception:
            pass

    if lab.startswith("Wall") or lab == "Arena":
        return True

    return False


def ensure_lighting_and_floor():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    has_dir = False
    has_sky = False
    has_floor = False
    for a in actors:
        lab = a.get_actor_label() or ""
        cls = a.get_class().get_name()
        if "DirectionalLight" in cls:
            has_dir = True
        if "SkyLight" in cls:
            has_sky = True
        if lab in ("Floor", "Hub_Floor", "HubFloor_Ground") or (
            isinstance(a, unreal.StaticMeshActor) and "Floor" in lab
        ):
            has_floor = True
            # Resize plaza floor
            a.set_actor_label("HubFloor_Ground")
            a.set_actor_location(unreal.Vector(0.0, 0.0, -2.0), False, True)
            # Plane is 100x100 cm; scale so covers courtyard + margin
            # half 3000 + walls ~3200 -> need ~6400 cm => scale 64
            a.set_actor_scale3d(unreal.Vector(70.0, 70.0, 1.0))
            try:
                sm = a.static_mesh_component.static_mesh
                if not sm:
                    plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
                    a.static_mesh_component.set_static_mesh(plane)
            except Exception:
                pass

    if not has_floor:
        floor = spawn(unreal.StaticMeshActor, unreal.Vector(0.0, 0.0, -2.0))
        if floor:
            plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
            set_mesh_on_actor(floor, plane, unreal.Vector(70.0, 70.0, 1.0))
            floor.set_actor_label("HubFloor_Ground")
            log("spawned HubFloor_Ground")
            has_floor = True

    if not has_dir:
        light = spawn(
            unreal.DirectionalLight,
            unreal.Vector(0.0, 0.0, 800.0),
            unreal.Rotator(-45.0, -35.0, 0.0),
        )
        if light:
            light.set_actor_label("Hub_Sun")
            log("spawned Hub_Sun")

    if not has_sky:
        sky = spawn(unreal.SkyLight, unreal.Vector(0.0, 0.0, 600.0))
        if sky:
            sky.set_actor_label("Hub_SkyLight")
            try:
                sky.light_component.set_editor_property("real_time_capture", True)
            except Exception:
                pass
            log("spawned Hub_SkyLight")

    # Atmospheric fog optional
    has_fog = any("AtmosphericFog" in a.get_class().get_name() or "ExponentialHeightFog" in a.get_class().get_name()
                  for a in unreal.EditorLevelLibrary.get_all_level_actors())
    if not has_fog:
        try:
            fog = spawn(unreal.ExponentialHeightFog, unreal.Vector(0.0, 0.0, 0.0))
            if fog:
                fog.set_actor_label("Hub_HeightFog")
        except Exception as e:
            log("fog skip: " + str(e))


def make_colored_cube(loc, scale, label, color_rgb):
    """Spawn a visible cube placeholder with a simple colored material instance if possible."""
    actor = spawn(unreal.StaticMeshActor, loc, unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        return None
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    set_mesh_on_actor(actor, cube, scale)
    actor.set_actor_label(label)
    snap_bottom_to_ground(actor, GROUND_Z)

    # Try create/assign a simple colored MIC
    try:
        mat_path = "/Game/Environments/KenneyTown/M_HubPlaceholder_" + label.replace("HubShop_", "").replace("HubGate_", "").replace("HubMarker_", "")
        # Use engine basic shape material and set vector if MI exists; else leave default
        base = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
        if base:
            # Constant color via create MID on component (runtime) — editor: set override
            mid = actor.static_mesh_component.create_dynamic_material_instance(0, base)
            if mid:
                # BasicShapeMaterial uses Color param often named "Color"
                for pname in ("Color", "BaseColor", "Tint"):
                    try:
                        mid.set_vector_parameter_value(
                            pname,
                            unreal.LinearColor(color_rgb[0], color_rgb[1], color_rgb[2], 1.0),
                        )
                        break
                    except Exception:
                        continue
    except Exception as e:
        log("cube color skip " + label + ": " + str(e))
    return actor


def make_text_label(loc, text, label):
    try:
        tr = spawn(unreal.TextRenderActor, loc, unreal.Rotator(0.0, 0.0, 0.0))
        if not tr:
            return None
        tr.set_actor_label(label)
        comp = None
        try:
            comp = tr.get_component_by_class(unreal.TextRenderComponent.static_class())
        except Exception:
            pass
        if comp is None:
            try:
                comp = tr.root_component
            except Exception:
                pass
        if comp:
            try:
                comp.set_text(text)
            except Exception:
                try:
                    comp.set_editor_property("text", text)
                except Exception:
                    pass
            try:
                comp.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            except Exception:
                pass
            try:
                comp.set_world_size(48.0)
            except Exception:
                try:
                    comp.set_editor_property("world_size", 48.0)
                except Exception:
                    pass
            try:
                comp.set_text_render_color(unreal.Color(255, 255, 40, 255))
            except Exception:
                pass
        return tr
    except Exception as e:
        log("text label fail: " + str(e))
        return None


def make_target(loc, label):
    try:
        tp = spawn(unreal.TargetPoint, loc, unreal.Rotator(0.0, 0.0, 0.0))
        if tp:
            tp.set_actor_label(label)
        return tp
    except Exception as e:
        log("TargetPoint fail: " + str(e))
        return None


def set_gm_hub_pawn():
    pawn_cls = unreal.load_class(None, TP_CHAR + ".ThirdPersonCharacter_C")
    if not pawn_cls:
        try:
            pawn_cls = unreal.EditorAssetLibrary.load_blueprint_class(TP_CHAR)
        except Exception as e:
            log("load ThirdPersonCharacter: " + str(e))
    if not pawn_cls:
        log("ERROR: ThirdPersonCharacter class not found")
        return False

    gm = unreal.EditorAssetLibrary.load_asset(GM_HUB)
    if not gm:
        log("ERROR: GM_Hub missing")
        return False

    cdo = None
    try:
        if hasattr(gm, "generated_class"):
            cdo = unreal.get_default_object(gm.generated_class())
    except Exception as e:
        log("generated_class: " + str(e))
    if cdo is None:
        try:
            gc = gm.get_editor_property("generated_class")
            cdo = unreal.get_default_object(gc)
        except Exception as e:
            log("get generated_class prop: " + str(e))
    if cdo is None:
        try:
            gc = unreal.load_class(None, GM_HUB + ".GM_Hub_C")
            cdo = unreal.get_default_object(gc)
        except Exception as e:
            log("load GM_Hub_C: " + str(e))

    ok = False
    if cdo:
        try:
            cdo.set_editor_property("default_pawn_class", pawn_cls)
            ok = True
            log("GM_Hub CDO DefaultPawnClass = ThirdPersonCharacter")
        except Exception as e:
            log("set CDO pawn: " + str(e))
            try:
                cdo.set_editor_property("DefaultPawnClass", pawn_cls)
                ok = True
                log("GM_Hub CDO DefaultPawnClass (Pascal) set")
            except Exception as e2:
                log("set CDO Pascal: " + str(e2))
    if not ok:
        try:
            gm.set_editor_property("default_pawn_class", pawn_cls)
            ok = True
            log("set default_pawn_class on BP asset")
        except Exception as e:
            log("set on BP: " + str(e))

    unreal.EditorAssetLibrary.save_loaded_asset(gm)
    return ok


def set_world_gamemode():
    try:
        world_obj = unreal.EditorLevelLibrary.get_editor_world()
        ws = world_obj.get_world_settings()
        gm_cls = unreal.load_class(None, GM_HUB + ".GM_Hub_C")
        if ws and gm_cls:
            ws.set_editor_property("DefaultGameMode", gm_cls)
            log("WorldSettings DefaultGameMode = GM_Hub")
            return True
        log("WARN: could not set world GM")
    except Exception as e:
        log("world GM: " + str(e))
    return False


def place_wall_segment(mesh, loc, yaw, scale_vec, label):
    rot = unreal.Rotator(0.0, float(yaw), 0.0)
    actor = spawn(unreal.StaticMeshActor, loc, rot)
    if not actor:
        return None
    actor.set_actor_label(label)
    set_mesh_on_actor(actor, mesh, scale_vec)
    snap_bottom_to_ground(actor, GROUND_Z)
    return actor


def build_walls(wall_mesh, corner_mesh, door_mesh):
    wx, wy, wz = mesh_size(wall_mesh)
    cx, cy, cz = mesh_size(corner_mesh) if corner_mesh else (wx, wy, wz)
    dx, dy, dz = mesh_size(door_mesh) if door_mesh else (wx, wy, wz)

    log("wall mesh size cm: %.1f x %.1f x %.1f" % (wx, wy, wz))
    log("corner mesh size cm: %.1f x %.1f x %.1f" % (cx, cy, cz))
    log("door mesh size cm: %.1f x %.1f x %.1f" % (dx, dy, dz))

    # Determine dominant horizontal length (Kenney walls often long on X)
    wall_len = max(wx, wy)
    wall_thick = min(wx, wy)
    wall_h = wz

    # Uniform XY scale so segment length ~100cm if tiny, or keep if already human
    # Kenney often imports as ~100cm length / ~200cm height already.
    # Scale height to WALL_HEIGHT_TARGET
    h_scale = WALL_HEIGHT_TARGET / wall_h
    # Keep XY near 1.0 if wall_len is between 50-200; else normalize length to 100
    if wall_len < 50.0:
        xy_scale = 100.0 / wall_len
    elif wall_len > 250.0:
        xy_scale = 100.0 / wall_len
    else:
        xy_scale = 1.0

    # Prefer matching height scale on XY a bit so proportions look city-like
    # but don't squash length too much — use h_scale for Z only if h_scale reasonable
    if h_scale < 0.5 or h_scale > 4.0:
        # weird import units — normalize height with XY together
        xy_scale = WALL_HEIGHT_TARGET / wall_h
        z_scale = xy_scale
    else:
        z_scale = h_scale

    scale_vec = unreal.Vector(xy_scale, xy_scale, z_scale)
    seg_len = wall_len * xy_scale
    seg_h = wall_h * z_scale
    log("scale xy=%.3f z=%.3f -> seg_len=%.1f seg_h=%.1f" % (xy_scale, z_scale, seg_len, seg_h))

    half = COURTYARD_HALF
    # Place walls centered on each side; corners at ±half
    # Side walls sit with outer face near |coord|=half
    # Use inward offset by half thickness
    thick = wall_thick * xy_scale
    inset = thick * 0.5

    placed = []
    idx = 0

    def place_side(axis, sign, yaw, include_gate=False):
        """Place wall segments along one side. axis='x' means wall runs along X (north/south)."""
        nonlocal idx
        # Usable length between corners
        usable = half * 2.0 - seg_len  # leave room approx for corners
        # Better: place corners separately; fill between -half+seg/2 ... 
        # Number of segments
        n = max(4, int(math.floor((half * 2.0) / seg_len)))
        # Recalc so segments span exactly
        # Keep seg_len; distribute from -half + seg_len/2 to +half - seg_len/2
        start = -half + seg_len * 0.5
        end = half - seg_len * 0.5
        if n <= 1:
            positions = [0.0]
        else:
            positions = [start + (end - start) * (i / float(n - 1)) for i in range(n)]

        gate_i = n // 2 if include_gate else -1
        for i, t in enumerate(positions):
            if axis == "x":
                # north/south: vary X, fixed Y
                loc = unreal.Vector(t, sign * (half - inset), 0.0)
            else:
                # east/west: vary Y, fixed X
                loc = unreal.Vector(sign * (half - inset), t, 0.0)

            if include_gate and i == gate_i and door_mesh:
                # Door segment length may differ — place door mesh
                dlen = max(dx, dy) * xy_scale
                dscale = unreal.Vector(xy_scale, xy_scale, z_scale)
                # If door height differs, still use z_scale from wall
                label = "HubGate_DungeonEntrance"
                a = place_wall_segment(door_mesh, loc, yaw, dscale, label)
                if a:
                    placed.append(a)
                    log("gate at %s" % loc)
                # Marker just inside gate
                if axis == "x":
                    mloc = unreal.Vector(t, sign * (half - inset - 150.0), 50.0)
                else:
                    mloc = unreal.Vector(sign * (half - inset - 150.0), t, 50.0)
                make_target(mloc, "HubMarker_DungeonEntrance")
                make_text_label(
                    unreal.Vector(mloc.x, mloc.y, 220.0),
                    "DUNGEON ENTRANCE",
                    "HubLabel_DungeonEntrance",
                )
                make_colored_cube(
                    unreal.Vector(mloc.x, mloc.y, 0.0),
                    unreal.Vector(1.2, 0.4, 2.5),
                    "HubPlaceholder_DungeonEntrance",
                    (0.9, 0.2, 0.2),
                )
            else:
                idx += 1
                label = "HubWall_%s_%02d" % (("N" if (axis == "x" and sign < 0) else
                                              "S" if (axis == "x" and sign > 0) else
                                              "W" if (axis == "y" and sign < 0) else "E"), idx)
                # Fix side names: UE Y-forward often; we use:
                # +Y = South side, -Y = North, +X = East, -X = West
                if axis == "x" and sign > 0:
                    side = "S"
                elif axis == "x" and sign < 0:
                    side = "N"
                elif axis == "y" and sign > 0:
                    side = "E"
                else:
                    side = "W"
                label = "HubWall_%s_%02d" % (side, i)
                a = place_wall_segment(wall_mesh, loc, yaw, scale_vec, label)
                if a:
                    placed.append(a)

    # Kenney wall bounds are typically thickX(~10) x longY(~100) x tallZ(~100).
    # North/South walls run along world X -> yaw 90 (local Y -> world X)
    # East/West walls run along world Y -> yaw 0  (local Y -> world Y)
    place_side("x", -1.0, 90.0, include_gate=False)  # North
    place_side("x", +1.0, 90.0, include_gate=True)   # South with gate
    place_side("y", -1.0, 0.0, include_gate=False)   # West
    place_side("y", +1.0, 0.0, include_gate=False)   # East

    # Corners
    if corner_mesh:
        corner_scale = unreal.Vector(xy_scale, xy_scale, z_scale)
        corners = [
            (unreal.Vector(-half + inset, -half + inset, 0.0), 0.0, "NW"),
            (unreal.Vector(half - inset, -half + inset, 0.0), 90.0, "NE"),
            (unreal.Vector(half - inset, half - inset, 0.0), 180.0, "SE"),
            (unreal.Vector(-half + inset, half - inset, 0.0), -90.0, "SW"),
        ]
        for loc, yaw, name in corners:
            a = place_wall_segment(corner_mesh, loc, yaw, corner_scale, "HubCorner_" + name)
            if a:
                placed.append(a)
    else:
        log("no corner mesh; sides only")

    log("wall actors placed=%d seg_len=%.1f courtyard_half=%.1f height~%.1f" % (
        len(placed), seg_len, half, seg_h))
    return placed, seg_len, seg_h


def ensure_player_start():
    starts = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "PlayerStart" in a.get_class().get_name() or "PlayerStart" in (a.get_actor_label() or ""):
            starts.append(a)
    if not starts:
        ps = spawn(unreal.PlayerStart, SPAWN, unreal.Rotator(0.0, 0.0, 0.0))
        if ps:
            ps.set_actor_label("Hub_PlayerStart")
            starts.append(ps)
            log("spawned Hub_PlayerStart")
    else:
        for i, ps in enumerate(starts):
            if i == 0:
                ps.set_actor_location(SPAWN, False, True)
                ps.set_actor_label("Hub_PlayerStart")
                try:
                    ps.set_actor_rotation(unreal.Rotator(0.0, 90.0, 0.0), False)  # face south/gate
                except Exception:
                    pass
                log("moved PlayerStart to courtyard center")
            else:
                destroy(ps)
                log("removed extra PlayerStart")
    return starts[:1]


def place_shops():
    # Three shops inside courtyard, clearly separated
    shops = [
        ("Weapon", unreal.Vector(-1200.0, -800.0, 0.0), (0.95, 0.25, 0.15), "Attack Buff (later)"),
        ("Armor", unreal.Vector(1200.0, -800.0, 0.0), (0.2, 0.45, 0.95), "Defense Buff (later)"),
        ("Health", unreal.Vector(0.0, 1200.0, 0.0), (0.2, 0.85, 0.35), "Heal (later)"),
    ]
    for key, loc, color, subtitle in shops:
        make_colored_cube(
            loc,
            unreal.Vector(1.5, 1.5, 2.0),
            "HubShop_%s" % key,
            color,
        )
        make_target(
            unreal.Vector(loc.x, loc.y, 50.0),
            "HubMarker_Shop_%s" % key,
        )
        make_text_label(
            unreal.Vector(loc.x, loc.y, 250.0),
            "%s SHOP\n%s" % (key.upper(), subtitle),
            "HubLabel_Shop_%s" % key,
        )
        log("shop placeholder " + key + " at " + str(loc))


def count_summary():
    walls = corners = gates = shops = markers = labels = floors = starts = 0
    others = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lab = a.get_actor_label() or ""
        if lab.startswith("HubWall_"):
            walls += 1
        elif lab.startswith("HubCorner_"):
            corners += 1
        elif lab.startswith("HubGate_") or "DungeonEntrance" in lab and lab.startswith("HubPlaceholder"):
            gates += 1
        elif lab.startswith("HubShop_"):
            shops += 1
        elif lab.startswith("HubMarker_"):
            markers += 1
        elif lab.startswith("HubLabel_"):
            labels += 1
        elif lab.startswith("HubFloor_") or lab in ("Floor", "Hub_Floor"):
            floors += 1
        elif "PlayerStart" in a.get_class().get_name():
            starts += 1
        else:
            others += 1
    # gate labeled HubGate_
    gates = sum(1 for a in unreal.EditorLevelLibrary.get_all_level_actors()
                if (a.get_actor_label() or "").startswith("HubGate_"))
    return {
        "walls": walls,
        "corners": corners,
        "gates": gates,
        "shops": shops,
        "markers": markers,
        "labels": labels,
        "floors": floors,
        "player_starts": starts,
        "other_actors": others,
        "total": walls + corners + gates + shops + markers + labels + floors + starts + others,
    }


def main():
    log("=== build_hub_walls start ===")
    wall = load_mesh(KENNEY + "/wall")
    corner = load_mesh(KENNEY + "/wall_corner")
    door = load_mesh(KENNEY + "/wall_doorway_square")
    if not wall:
        log("ERROR: missing Kenney wall at " + KENNEY + "/wall")
        flush_log()
        return
    if not door:
        log("WARN: no doorway mesh; will leave a gap visually with missing door")
    if not corner:
        log("WARN: no corner mesh")

    # Load map
    if not unreal.EditorAssetLibrary.does_asset_exist(HUB_MAP):
        log("Map_Hub missing; creating")
        try:
            unreal.EditorLevelLibrary.new_level(HUB_MAP)
        except Exception as e:
            log("new_level: " + str(e))
            factory = unreal.WorldFactory()
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            asset_tools.create_asset("Map_Hub", "/Game/Maps/Hub", unreal.World, factory)
            unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    else:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    log("Map_Hub loaded")

    # Clear clutter
    destroyed = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        if should_destroy(a):
            destroy(a)
            destroyed += 1
    log("destroyed clutter=%d" % destroyed)

    ensure_lighting_and_floor()
    placed, seg_len, seg_h = build_walls(wall, corner, door)
    ensure_player_start()
    place_shops()
    set_gm_hub_pawn()
    set_world_gamemode()

    unreal.EditorLevelLibrary.save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception as e:
        log("save_dirty: " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(GM_HUB)
    except Exception as e:
        log("save GM_Hub: " + str(e))

    summary = count_summary()
    log("SUMMARY " + str(summary))
    log("COURTYARD half=%.0fcm (%.0fm across) wall_h~%.0fcm seg_len=%.0fcm" % (
        COURTYARD_HALF, COURTYARD_HALF * 2 / 100.0, seg_h, seg_len))
    log("PAWN GM_Hub -> ThirdPersonCharacter")
    log("VERIFY: Open /Game/Maps/Hub/Map_Hub, check Outliner HubWall_/HubShop_/HubGate_, PIE walk")
    log("=== build_hub_walls DONE ===")
    flush_log()


try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc())
    flush_log()
    raise
