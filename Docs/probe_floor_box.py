# -*- coding: utf-8 -*-
"""Probe: add thin box collision to one floor mesh; print before/after."""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_floor_box.txt"
PATH = "/Game/Environments/KayKitDungeon/Meshes/Floors/SM_floor_tile_small"
lines = []

def log(m):
    lines.append(str(m))
    unreal.log(str(m))

mesh = unreal.EditorAssetLibrary.load_asset(PATH)
bb = mesh.get_bounding_box()
log("bb min=%s max=%s" % (bb.min, bb.max))
bs = mesh.get_editor_property("body_setup")
ag = bs.get_editor_property("agg_geom")
log("before flag=%s convex=%d boxes=%d" % (
    bs.get_editor_property("collision_trace_flag"),
    len(ag.get_editor_property("convex_elems") or []),
    len(ag.get_editor_property("box_elems") or []),
))

# Try remove + add box via several methods
unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
bs = mesh.get_editor_property("body_setup")
log("after remove convex=%d boxes=%d" % (
    len(bs.get_editor_property("agg_geom").get_editor_property("convex_elems") or []),
    len(bs.get_editor_property("agg_geom").get_editor_property("box_elems") or []),
))

# Method A: EditorStaticMeshLibrary.add_simple_collisions BOX (full AABB)
try:
    n = unreal.EditorStaticMeshLibrary.add_simple_collisions(mesh, unreal.ScriptingCollisionShapeType.BOX)
    log("add_simple_collisions BOX returned %s" % n)
except Exception as e:
    log("add_simple_collisions fail: %s" % e)

bs = mesh.get_editor_property("body_setup")
ag = bs.get_editor_property("agg_geom")
boxes = ag.get_editor_property("box_elems") or []
log("after A boxes=%d" % len(boxes))
if boxes:
    b0 = boxes[0]
    for prop in ("center", "x", "y", "z", "rotation", "Center", "X", "Y", "Z"):
        try:
            log("  box.%s = %s" % (prop, b0.get_editor_property(prop)))
        except Exception as e:
            log("  box.%s ERR %s" % (prop, e))

# Clear again and try manual BoxElem
unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
bs = mesh.get_editor_property("body_setup")
WALK_TOP = 5.0
WALK_BOT = -10.0
cx = (bb.min.x + bb.max.x) * 0.5
cz = (bb.min.z + bb.max.z) * 0.5
cy = (WALK_TOP + WALK_BOT) * 0.5
x_len = abs(bb.max.x - bb.min.x)
z_len = abs(bb.max.z - bb.min.z)
y_len = WALK_TOP - WALK_BOT

box = unreal.BoxElem()
ok_sets = []
for prop, val in [
    ("center", unreal.Vector(cx, cy, cz)),
    ("x", float(x_len)),
    ("y", float(y_len)),
    ("z", float(z_len)),
]:
    try:
        box.set_editor_property(prop, val)
        ok_sets.append(prop)
    except Exception as e:
        log("set %s fail: %s" % (prop, e))
log("ok_sets %s" % ok_sets)

# Try assign
ag = bs.get_editor_property("agg_geom")
assigned = False
for method in ("list", "array"):
    try:
        if method == "list":
            ag.set_editor_property("box_elems", [box])
        else:
            arr = unreal.Array(unreal.BoxElem)
            arr.append(box)
            ag.set_editor_property("box_elems", arr)
        bs.set_editor_property("agg_geom", ag)
        mesh.set_editor_property("body_setup", bs)
        assigned = True
        log("assign via %s OK" % method)
        break
    except Exception as e:
        log("assign via %s fail: %s" % (method, e))

bs = mesh.get_editor_property("body_setup")
ag = bs.get_editor_property("agg_geom")
boxes = ag.get_editor_property("box_elems") or []
log("final boxes=%d convex=%d" % (len(boxes), len(ag.get_editor_property("convex_elems") or [])))
if boxes:
    b0 = boxes[0]
    log("final box center=%s x=%s y=%s z=%s" % (
        b0.get_editor_property("center"),
        b0.get_editor_property("x"),
        b0.get_editor_property("y"),
        b0.get_editor_property("z"),
    ))

# Don't save probe permanently - restore via re-add default? Leave modified for now; full fix will overwrite.
# Actually restore: remove and add_simple BOX then we'll fix properly
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("PROBE_OK")
