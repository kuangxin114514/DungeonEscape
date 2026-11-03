# -*- coding: utf-8 -*-
"""Probe modifying existing box collision dimensions."""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_box_modify.txt"
PATH = "/Game/Environments/KayKitDungeon/Meshes/Floors/SM_floor_tile_large_rocks"
lines = []

def log(m):
    lines.append(str(m))
    unreal.log(str(m))

mesh = unreal.EditorAssetLibrary.load_asset(PATH)
bs = mesh.get_editor_property("body_setup")
ag = bs.get_editor_property("agg_geom")
boxes = list(ag.get_editor_property("box_elems") or [])
log("n_boxes=%d type0=%s" % (len(boxes), type(boxes[0]) if boxes else None))
if not boxes:
    unreal.EditorStaticMeshLibrary.add_simple_collisions(mesh, unreal.ScriptingCollisionShapeType.BOX)
    bs = mesh.get_editor_property("body_setup")
    ag = bs.get_editor_property("agg_geom")
    boxes = list(ag.get_editor_property("box_elems") or [])
    log("after add n=%d" % len(boxes))

b0 = boxes[0]
log("before c=%s x=%s y=%s z=%s" % (
    b0.get_editor_property("center"), b0.get_editor_property("x"),
    b0.get_editor_property("y"), b0.get_editor_property("z")))

# Try in-place set
b0.set_editor_property("center", unreal.Vector(0.0, 2.5, 0.0))
b0.set_editor_property("y", 15.0)
log("after inplace c=%s y=%s" % (b0.get_editor_property("center"), b0.get_editor_property("y")))

# Re-read from mesh
bs2 = mesh.get_editor_property("body_setup")
ag2 = bs2.get_editor_property("agg_geom")
boxes2 = ag2.get_editor_property("box_elems") or []
b2 = boxes2[0]
log("reread c=%s y=%s" % (b2.get_editor_property("center"), b2.get_editor_property("y")))

# Try reassign list
boxes[0] = b0
try:
    ag.set_editor_property("box_elems", boxes)
    bs.set_editor_property("agg_geom", ag)
    mesh.set_editor_property("body_setup", bs)
    log("reassign list ok")
except Exception as e:
    log("reassign list fail: %s" % e)

bs3 = mesh.get_editor_property("body_setup")
b3 = (bs3.get_editor_property("agg_geom").get_editor_property("box_elems") or [None])[0]
log("after reassign c=%s y=%s" % (b3.get_editor_property("center"), b3.get_editor_property("y")))

# Inspect BoxElem / KBoxElem constructors
for name in ["BoxElem", "KBoxElem", "FKBoxElem", "BoxCollision", "OrientedBoxElem"]:
    log("hasattr unreal.%s = %s" % (name, hasattr(unreal, name)))

# Try duplicating via add then modify with mark package dirty
try:
    unreal.EditorAssetLibrary.checkout_loaded_asset(mesh)
except Exception as e:
    log("checkout: %s" % e)

# Use body setup create_physics_meshes or invalidate
try:
    bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
except Exception as e:
    log("flag: %s" % e)

# Another approach: scale the mesh build? no.

# Try getting BoxElem from unreal reflection
try:
    import unreal as u
    # In UE4, structs sometimes via Array
    arr = unreal.Array(type(b0))
    log("Array elem type works type=%s" % type(b0))
except Exception as e:
    log("Array type fail: %s" % e)

# Try copy properties onto new instance via __class__
try:
    New = type(b0)
    nb = New()
    log("constructed via type(b0) ok")
    nb.set_editor_property("center", unreal.Vector(0.0, 2.5, 0.0))
    nb.set_editor_property("x", 400.0)
    nb.set_editor_property("y", 15.0)
    nb.set_editor_property("z", 400.0)
    ag.set_editor_property("box_elems", [nb])
    bs.set_editor_property("agg_geom", ag)
    mesh.set_editor_property("body_setup", bs)
    b4 = mesh.get_editor_property("body_setup").get_editor_property("agg_geom").get_editor_property("box_elems")[0]
    log("new instance assign c=%s y=%s" % (b4.get_editor_property("center"), b4.get_editor_property("y")))
except Exception as e:
    log("type(b0) construct fail: %s" % e)

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("PROBE2_OK")
