# -*- coding: utf-8 -*-
"""Inspect KayKit floor/stairs StaticMesh bounds + collision (no edits)."""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\inspect_kaykit_floor_collision.txt"
FLOORS = "/Game/Environments/KayKitDungeon/Meshes/Floors"
STAIRS = "/Game/Environments/KayKitDungeon/Meshes/Stairs"
lines = []

def log(m):
    lines.append(m)

def inspect_dir(folder):
    assets = unreal.EditorAssetLibrary.list_assets(folder, True, False)
    log("DIR %s count=%d" % (folder, len(assets)))
    rows = []
    for path in sorted(assets):
        name = path.split(".")[-1] if "." in path else path.rsplit("/", 1)[-1]
        # list_assets returns object path like /Game/.../SM_x.SM_x
        asset_path = path.split(".")[0]
        mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not mesh or not isinstance(mesh, unreal.StaticMesh):
            log("SKIP %s" % asset_path)
            continue
        bb = mesh.get_bounding_box()
        mn, mx = bb.min, bb.max
        sx = abs(mx.x - mn.x); sy = abs(mx.y - mn.y); sz = abs(mx.z - mn.z)
        flag = "?"
        simple = {}
        try:
            bs = mesh.get_editor_property("body_setup")
            if bs:
                flag = str(bs.get_editor_property("collision_trace_flag"))
                ag = bs.get_editor_property("agg_geom")
                simple = {
                    "spheres": len(ag.get_editor_property("sphere_elems") or []),
                    "boxes": len(ag.get_editor_property("box_elems") or []),
                    "sphyls": len(ag.get_editor_property("sphyl_elems") or []),
                    "convex": len(ag.get_editor_property("convex_elems") or []),
                }
                # Try read convex / box extents if present
                try:
                    convexes = ag.get_editor_property("convex_elems") or []
                    if convexes:
                        c0 = convexes[0]
                        # FKConvexElem may expose elem_box
                        try:
                            eb = c0.get_editor_property("elem_box")
                            simple["convex0_box"] = "min=(%.2f,%.2f,%.2f) max=(%.2f,%.2f,%.2f)" % (
                                eb.min.x, eb.min.y, eb.min.z, eb.max.x, eb.max.y, eb.max.z)
                        except Exception as e:
                            simple["convex0_box"] = "na:" + str(e)[:60]
                    boxes = ag.get_editor_property("box_elems") or []
                    if boxes:
                        b0 = boxes[0]
                        simple["box0"] = "c=(%.2f,%.2f,%.2f) XYZ=(%.2f,%.2f,%.2f)" % (
                            b0.get_editor_property("center").x,
                            b0.get_editor_property("center").y,
                            b0.get_editor_property("center").z,
                            b0.get_editor_property("x"),
                            b0.get_editor_property("y"),
                            b0.get_editor_property("z"),
                        )
                except Exception as e:
                    simple["detail_err"] = str(e)[:80]
        except Exception as e:
            flag = "err:" + str(e)
        row = "%s meshZ[%.2f,%.2f] h=%.2f size=(%.1f,%.1f,%.1f) flag=%s simple=%s" % (
            name, mn.z, mx.z, sz, sx, sy, sz, flag, simple)
        log(row)
        rows.append((name, mn.z, mx.z, sz))
    if rows:
        zs = [r[2] for r in rows]  # max z
        log("SUMMARY maxZ min=%.2f max=%.2f spread=%.2f" % (min(zs), max(zs), max(zs)-min(zs)))
        # group by roughly
        for name, z0, z1, h in sorted(rows, key=lambda r: r[2]):
            log("  sort_by_zmax %s zmax=%.2f zmin=%.2f h=%.2f" % (name, z1, z0, h))

inspect_dir(FLOORS)
log("==== STAIRS ====")
inspect_dir(STAIRS)
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("INSPECT_OK lines=%d" % len(lines))
