# -*- coding: utf-8 -*-
"""Fix KayKit doorway/open wall collision: Use Complex as Simple so openings are walkable.
Does NOT touch solid walls, Map_Hub, or rearrange Map_Dungeon actors.
"""
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_kaykit_doorway_collision.txt"
WALLS = "/Game/Environments/KayKitDungeon/Meshes/Walls"

# Openings the player should be able to pass (or whose hole must not be a solid box).
# Gated/barred meshes also get complex-as-simple so bars collide and gaps stay open.
OPEN_MESHES = [
    "SM_wall_doorway",
    "SM_wall_doorway_door",
    "SM_wall_doorway_scaffold",
    "SM_wall_doorway_scaffold_door",
    "SM_wall_doorway_sides",
    "SM_wall_doorway_Tsplit",
    "SM_wall_gated",
    "SM_wall_open_scaffold",
    "SM_wall_arched",
    "SM_wall_archedwindow_open",
    "SM_wall_archedwindow_gated",
    "SM_wall_archedwindow_gated_scaffold",
    "SM_wall_window_open",
    "SM_wall_window_open_scaffold",
    "SM_wall_broken",
    "SM_wall_corner_gated",
]

lines = []

def log(msg):
    lines.append(msg)
    unreal.log(msg)


def fix_mesh(asset_path):
    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        return "missing"
    mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not mesh or not isinstance(mesh, unreal.StaticMesh):
        return "not_sm"

    before_flag = None
    before_simple = None
    try:
        bs = mesh.get_editor_property("body_setup")
        if bs:
            before_flag = str(bs.get_editor_property("collision_trace_flag"))
            try:
                aggs = bs.get_editor_property("agg_geom")
                before_simple = {
                    "spheres": len(aggs.get_editor_property("sphere_elems") or []),
                    "boxes": len(aggs.get_editor_property("box_elems") or []),
                    "sphyls": len(aggs.get_editor_property("sphyl_elems") or []),
                    "convex": len(aggs.get_editor_property("convex_elems") or []),
                }
            except Exception as e:
                before_simple = {"err": str(e)}
    except Exception as e:
        before_flag = "err:" + str(e)

    # Remove auto-generated simple collision that fills the opening.
    try:
        unreal.EditorStaticMeshLibrary.remove_collisions(mesh)
    except Exception as e:
        log("  remove_collisions warn: " + str(e))

    # Prefer complex (render mesh) as simple collision so the hole is open.
    try:
        bs = mesh.get_editor_property("body_setup")
        if bs is None:
            # Ensure body setup exists
            try:
                unreal.EditorStaticMeshLibrary.set_allow_cpu_access(mesh, True)
            except Exception:
                pass
            bs = mesh.get_editor_property("body_setup")
        if bs:
            bs.set_editor_property(
                "collision_trace_flag",
                unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE,
            )
        else:
            return "no_body_setup before=%s simple=%s" % (before_flag, before_simple)
    except Exception as e:
        return "set_flag_fail: %s before=%s" % (e, before_flag)

    # Build / notify so collision updates in editor and PIE after restart/reload.
    try:
        unreal.EditorStaticMeshLibrary.build_static_meshes([mesh])
    except Exception:
        try:
            # Older helper name / signature
            mesh.build()
        except Exception as e:
            log("  build warn: " + str(e))

    after_flag = None
    after_simple = None
    try:
        bs = mesh.get_editor_property("body_setup")
        after_flag = str(bs.get_editor_property("collision_trace_flag"))
        aggs = bs.get_editor_property("agg_geom")
        after_simple = {
            "spheres": len(aggs.get_editor_property("sphere_elems") or []),
            "boxes": len(aggs.get_editor_property("box_elems") or []),
            "sphyls": len(aggs.get_editor_property("sphyl_elems") or []),
            "convex": len(aggs.get_editor_property("convex_elems") or []),
        }
    except Exception as e:
        after_flag = "err:" + str(e)

    unreal.EditorAssetLibrary.save_asset(asset_path)
    return "ok before_flag=%s before_simple=%s after_flag=%s after_simple=%s" % (
        before_flag, before_simple, after_flag, after_simple
    )


def main():
    log("fix_kaykit_doorway_collision start")
    ok = 0
    fail = 0
    for name in OPEN_MESHES:
        path = WALLS + "/" + name
        result = fix_mesh(path)
        log("%s -> %s" % (name, result))
        if result.startswith("ok"):
            ok += 1
        else:
            fail += 1
    log("DONE ok=%d fail=%d" % (ok, fail))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


main()
