# -*- coding: utf-8 -*-
"""Clamp KayKit floor box collision to shared walk deck; complex for grates/foundations/stairs."""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_kaykit_floor_collision.txt"
FLOORS = "/Game/Environments/KayKitDungeon/Meshes/Floors"
STAIRS = "/Game/Environments/KayKitDungeon/Meshes/Stairs"
WALK_TOP_Y = -5.0
WALK_BOT_Y = 10.0

COMPLEX_NAMES = set([
    "SM_floor_tile_big_grate",
    "SM_floor_tile_big_grate_open",
    "SM_floor_tile_extralarge_grates",
    "SM_floor_tile_extralarge_grates_open",
    "SM_floor_tile_grate",
    "SM_floor_tile_grate_open",
    "SM_floor_foundation_allsides",
    "SM_floor_foundation_corner",
    "SM_floor_foundation_diagonal_corner",
    "SM_floor_foundation_front",
    "SM_floor_foundation_front_and_back",
    "SM_floor_foundation_front_and_sides",
])

lines = []

def log(msg):
    lines.append(msg)


def short_box(bs):
    ag = bs.get_editor_property("agg_geom")
    boxes = ag.get_editor_property("box_elems") or []
    convex = len(ag.get_editor_property("convex_elems") or [])
    flag = str(bs.get_editor_property("collision_trace_flag"))
    if boxes:
        b = boxes[0]
        c = b.get_editor_property("center")
        return "flag=%s convex=%d boxes=%d cY=%.2f Ylen=%.2f" % (
            flag, convex, len(boxes), c.y, b.get_editor_property("y"))
    return "flag=%s convex=%d boxes=0" % (flag, convex)


def fix_complex(mesh, asset_path):
    unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
    bs = mesh.get_editor_property("body_setup")
    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)
    return "complex " + short_box(bs)


def fix_thin_box(mesh, asset_path):
    bb = mesh.get_bounding_box()
    unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
    unreal.EditorStaticMeshLibrary.add_simple_collisions(mesh, unreal.ScriptingCollisionShapeType.BOX)
    bs = mesh.get_editor_property("body_setup")
    ag = bs.get_editor_property("agg_geom")
    existing = list(ag.get_editor_property("box_elems") or [])
    if not existing:
        return "FAIL no box after add"

    cx = (bb.min.x + bb.max.x) * 0.5
    cz = (bb.min.z + bb.max.z) * 0.5
    cy = (WALK_TOP_Y + WALK_BOT_Y) * 0.5
    x_len = abs(bb.max.x - bb.min.x)
    z_len = abs(bb.max.z - bb.min.z)
    y_len = WALK_BOT_Y - WALK_TOP_Y

    nb = unreal.KBoxElem()
    nb.set_editor_property("center", unreal.Vector(float(cx), float(cy), float(cz)))
    nb.set_editor_property("x", float(x_len))
    nb.set_editor_property("y", float(y_len))
    nb.set_editor_property("z", float(z_len))
    try:
        nb.set_editor_property("rotation", unreal.Rotator(0.0, 0.0, 0.0))
    except Exception:
        pass

    ag.set_editor_property("box_elems", [nb])
    # clear any leftover convex
    try:
        ag.set_editor_property("convex_elems", [])
    except Exception:
        pass
    bs.set_editor_property("agg_geom", ag)
    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    mesh.set_editor_property("body_setup", bs)
    unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)

    # verify from reload
    mesh2 = unreal.EditorAssetLibrary.load_asset(asset_path)
    return "box " + short_box(mesh2.get_editor_property("body_setup"))


def process(folder, force_complex=False):
    ok = fail = 0
    for path in sorted(unreal.EditorAssetLibrary.list_assets(folder, True, False)):
        asset_path = path.split(".")[0]
        name = asset_path.rsplit("/", 1)[-1]
        mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not mesh or not isinstance(mesh, unreal.StaticMesh):
            log("%s SKIP" % name); fail += 1; continue
        try:
            if force_complex or name in COMPLEX_NAMES:
                result = fix_complex(mesh, asset_path)
            else:
                result = fix_thin_box(mesh, asset_path)
            log("%s -> %s" % (name, result))
            if result.startswith("box ") or result.startswith("complex "):
                # sanity: thin boxes must have Ylen~15
                if result.startswith("box ") and "Ylen=15.00" not in result and "Ylen=15.0" not in result:
                    # allow float formatting
                    if "Ylen=15." not in result:
                        fail += 1
                        log("  WARN unexpected Ylen")
                        continue
                ok += 1
            else:
                fail += 1
        except Exception as e:
            log("%s EXC %s" % (name, e)); fail += 1
    return ok, fail


log("fix_kaykit_floor_collision v2 start")
o1, f1 = process(FLOORS, False)
log("floors ok=%d fail=%d" % (o1, f1))
o2, f2 = process(STAIRS, True)
log("stairs ok=%d fail=%d" % (o2, f2))
log("DONE ok=%d fail=%d" % (o1 + o2, f1 + f2))
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("FIX_V2_OK ok=%d fail=%d" % (o1 + o2, f1 + f2))
