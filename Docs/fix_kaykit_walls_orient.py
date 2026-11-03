# -*- coding: utf-8 -*-
"""Rebuild Map_Hub KayKit walls with correct UE4 Rotator(roll,pitch,yaw) orientation."""
from __future__ import print_function
import unreal
import math
import traceback

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
DEST_WALLS = "/Game/Environments/KayKitMedieval/Walls"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_kaykit_walls.log"
COURTYARD_HALF = 3000.0
WALL_HEIGHT_TARGET = 380.0
GROUND_Z = 0.0
SPAWN = unreal.Vector(0.0, 0.0, 100.0)

_log_lines = []

def log(msg):
    line = str(msg)
    _log_lines.append(line)
    unreal.log("KAYWALLS: " + line)

def flush_log():
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(_log_lines) + "\n")

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
        pass

def mesh_size(mesh):
    bbox = mesh.get_bounding_box()
    return (
        abs(bbox.max.x - bbox.min.x),
        abs(bbox.max.y - bbox.min.y),
        abs(bbox.max.z - bbox.min.z),
    )

def snap_bottom(actor, ground_z=GROUND_Z):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    loc = actor.get_actor_location()
    actor.set_actor_location(
        unreal.Vector(loc.x, loc.y, loc.z + (ground_z - bottom)), False, True
    )

def make_rot(yaw_deg):
    # UE4.27 Python: Rotator(roll, pitch, yaw)  -- NOT (pitch,yaw,roll)!
    # roll=+90 stands KayKit Y-up meshes upright (Y -> world Z)
    return unreal.Rotator(90.0, 0.0, float(yaw_deg))

def place_segment(mesh, loc, yaw, scale, label):
    rot = make_rot(yaw)
    actor = spawn(unreal.StaticMeshActor, loc, rot)
    if not actor:
        return None
    actor.set_actor_label(label)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    try:
        comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        comp.set_editor_property("collision_profile_name", "BlockAll")
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:
        pass
    snap_bottom(actor, GROUND_Z)
    return actor

def clear_owned():
    n = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        lab = a.get_actor_label() or ""
        if lab.startswith(("HubWall_", "HubCorner_", "HubGate_", "ProbeWall_")):
            destroy(a)
            n += 1
    log("cleared=%d" % n)

def main():
    log("=== fix_kaykit_walls_orient start ===")
    wall = unreal.EditorAssetLibrary.load_asset(DEST_WALLS + "/wall_straight")
    gate = unreal.EditorAssetLibrary.load_asset(DEST_WALLS + "/wall_straight_gate")
    corner_a = unreal.EditorAssetLibrary.load_asset(DEST_WALLS + "/wall_corner_A_outside")
    corner_b = unreal.EditorAssetLibrary.load_asset(DEST_WALLS + "/wall_corner_B_outside")
    if not wall:
        log("FATAL no wall_straight")
        flush_log()
        return

    sx, sy, sz = mesh_size(wall)
    # KayKit wall_straight: X=len~2, Y=height~1.1, Z=thick~0.8
    wall_len = sx
    wall_h = sy
    scale = WALL_HEIGHT_TARGET / wall_h
    log("wall size=%.3f x %.3f x %.3f scale=%.4f" % (sx, sy, sz, scale))

    unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
    clear_owned()

    seg_len = wall_len * scale
    half = COURTYARD_HALF
    thick = sz * scale
    inset = thick * 0.5
    corner_span = 1.2 * scale
    usable = half * 2.0 - 2.0 * corner_span
    n = max(3, int(round(usable / seg_len)))
    start = -half + corner_span + seg_len * 0.5
    end = half - corner_span - seg_len * 0.5
    positions = [start + (end - start) * (i / float(n - 1)) for i in range(n)] if n > 1 else [0.0]
    log("seg_len=%.1f n=%d inset=%.1f" % (seg_len, n, inset))

    placed = []

    def side_name(axis, sign):
        if axis == "x" and sign > 0: return "S"
        if axis == "x" and sign < 0: return "N"
        if axis == "y" and sign > 0: return "E"
        return "W"

    def place_side(axis, sign, yaw, include_gate=False):
        gate_i = n // 2 if include_gate else -1
        for i, t in enumerate(positions):
            if axis == "x":
                loc = unreal.Vector(t, sign * (half - inset), 0.0)
            else:
                loc = unreal.Vector(sign * (half - inset), t, 0.0)
            side = side_name(axis, sign)
            if include_gate and i == gate_i and gate:
                a = place_segment(gate, loc, yaw, scale, "HubGate_DungeonEntrance")
                if a:
                    placed.append(a)
                    log("gate at (%.0f,%.0f) yaw=%.0f" % (loc.x, loc.y, yaw))
            else:
                a = place_segment(wall, loc, yaw, scale, "HubWall_%s_%02d" % (side, i))
                if a:
                    placed.append(a)

    # N/S: length along world X -> yaw 0; E/W: length along world Y -> yaw 90
    place_side("x", -1.0, 0.0, False)   # North
    place_side("x", +1.0, 0.0, True)    # South + gate
    place_side("y", -1.0, 90.0, False)  # West
    place_side("y", +1.0, 90.0, False)  # East

    cmesh_list = [corner_a, corner_b, corner_a, corner_b]
    corners = [
        (unreal.Vector(-half + inset, -half + inset, 0.0), 0.0, "NW"),
        (unreal.Vector(half - inset, -half + inset, 0.0), 90.0, "NE"),
        (unreal.Vector(half - inset, half - inset, 0.0), 180.0, "SE"),
        (unreal.Vector(-half + inset, half - inset, 0.0), -90.0, "SW"),
    ]
    for i, (loc, yaw, name) in enumerate(corners):
        m = cmesh_list[i] or corner_a or corner_b
        if not m:
            continue
        a = place_segment(m, loc, yaw, scale, "HubCorner_" + name)
        if a:
            placed.append(a)

    # Measure sample
    sample_h = 0.0
    for a in placed:
        lab = a.get_actor_label() or ""
        if lab.startswith("HubWall_"):
            o, e = a.get_actor_bounds(False)
            sample_h = e.z * 2.0
            log("sample %s world_h=%.1f loc=%s rot=%s" % (
                lab, sample_h, a.get_actor_location(), a.get_actor_rotation()))
            break

    # Ensure player start still central
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "PlayerStart" in a.get_class().get_name():
            a.set_actor_location(SPAWN, False, True)
            a.set_actor_label("Hub_PlayerStart")
            break

    unreal.EditorLevelLibrary.save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception as e:
        log("save_dirty: " + str(e))

    walls = sum(1 for a in unreal.EditorLevelLibrary.get_all_level_actors() if (a.get_actor_label() or "").startswith("HubWall_"))
    corners_n = sum(1 for a in unreal.EditorLevelLibrary.get_all_level_actors() if (a.get_actor_label() or "").startswith("HubCorner_"))
    gates = sum(1 for a in unreal.EditorLevelLibrary.get_all_level_actors() if (a.get_actor_label() or "").startswith("HubGate_"))
    shops = sum(1 for a in unreal.EditorLevelLibrary.get_all_level_actors() if (a.get_actor_label() or "").startswith("HubShop_"))
    log("SUMMARY walls=%d corners=%d gates=%d shops=%d placed=%d" % (walls, corners_n, gates, shops, len(placed)))
    log("SCALE=%.4f seg_len=%.1fcm world_wall_h=%.1fcm (~%.2fx ThirdPerson 192cm)" % (
        scale, seg_len, sample_h, sample_h / 192.0))
    log("Rotator note: UE4 py Rotator(roll,pitch,yaw); used roll=90 upright")
    log("=== fix_kaykit_walls_orient DONE ===")
    flush_log()

try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc())
    flush_log()
    raise