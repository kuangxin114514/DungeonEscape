# -*- coding: utf-8 -*-
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skeleton_ground.txt"
lines = []

def L(s):
    lines.append(str(s))
    print(s)

BP_PATH = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
MAP = "/Game/Maps/Map_Dungeon"
HALF = 55.0
# Mesh origin near feet (bounds bottom ~+1uu). Put feet at capsule bottom.
MESH_Z = -HALF  # -55
SCALE = 0.85

L("=== fix skeleton ground ===")

bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
L("bp=%s" % bp)
gc = None
try:
    gc = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
except Exception as e:
    L("load_bp_class %s" % e)
L("gc=%s" % gc)
cdo = unreal.get_default_object(gc) if gc else None
L("cdo=%s" % cdo)

mesh = None
cap = None
if cdo:
    try:
        mesh = cdo.get_editor_property("mesh")
    except Exception as e:
        L("mesh get %s" % e)
    try:
        cap = cdo.get_editor_property("capsule_component")
    except Exception as e:
        L("cap get %s" % e)

if cap:
    try:
        cap.set_editor_property("capsule_half_height", HALF)
        cap.set_editor_property("capsule_radius", 28.0)
        L("capsule half=%s radius=28" % HALF)
    except Exception as e:
        L("cap set %s" % e)

if mesh:
    try:
        old = mesh.get_editor_property("relative_location")
        L("old mesh rel=%s scale=%s" % (old, mesh.get_editor_property("relative_scale3d")))
    except Exception as e:
        L("old read %s" % e)
    # Keep X/Y and yaw from TP template (Y tiny offset, yaw 270)
    new_loc = unreal.Vector(0.0, 0.0, MESH_Z)
    try:
        mesh.set_editor_property("relative_location", new_loc)
    except Exception as e:
        L("set rel prop %s" % e)
        try:
            mesh.set_relative_location(new_loc, False, False)
        except Exception as e2:
            L("set_relative_location %s" % e2)
    try:
        mesh.set_editor_property("relative_scale3d", unreal.Vector(SCALE, SCALE, SCALE))
    except Exception as e:
        L("scale %s" % e)
    # Ensure no anim BP fighting; keep single-node idle if set
    try:
        L("new mesh rel=%s scale=%s anim_mode=%s" % (
            mesh.get_editor_property("relative_location"),
            mesh.get_editor_property("relative_scale3d"),
            mesh.get_editor_property("animation_mode"),
        ))
    except Exception as e:
        L("verify %s" % e)

# Also mark blueprint dirty / compile best-effort
for attempt in (
    lambda: unreal.KismetEditorUtilities.compile_blueprint(bp),
    lambda: __import__("unreal").BlueprintEditorLibrary.compile_blueprint(bp),
):
    try:
        attempt()
        L("compiled")
        break
    except Exception as e:
        L("compile skip: %s" % e)

# Fix placed previews: clear instance overrides of mesh relative loc, set Z to PlayerStart height
try:
    unreal.EditorLevelLibrary.load_level(MAP)
except Exception as e:
    L("load_level %s" % e)

ps = None
acts = unreal.EditorLevelLibrary.get_all_level_actors()
for a in acts:
    if a.get_class().get_name().startswith("PlayerStart"):
        ps = a
        break
ps_z = 150.0
ps_loc = None
if ps:
    ps_loc = ps.get_actor_location()
    ps_z = ps_loc.z
    L("PlayerStart %s" % ps_loc)

previews = []
for a in acts:
    n = a.get_name()
    if n.startswith("Preview_Skeleton") or "BP_Enemy_Skeleton" in a.get_class().get_name():
        # only our previews / enemy class
        if "Knight" in n:
            continue
        previews.append(a)

L("preview_count=%d" % len(previews))
for a in previews:
    loc = a.get_actor_location()
    # keep XY, snap Z to PlayerStart capsule height so they spawn above floor like player
    new_actor_loc = unreal.Vector(loc.x, loc.y, ps_z)
    try:
        a.set_actor_location(new_actor_loc, False, True)
    except Exception:
        try:
            unreal.EditorLevelLibrary.set_actor_location(a, new_actor_loc)
        except Exception as e:
            L("set actor loc %s %s" % (a.get_name(), e))
    # push mesh relative on instance too
    try:
        comps = a.get_components_by_class(unreal.SkeletalMeshComponent)
        for c in comps:
            try:
                c.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, MESH_Z))
            except Exception:
                try:
                    c.set_relative_location(unreal.Vector(0.0, 0.0, MESH_Z), False, False)
                except Exception as e:
                    L("inst mesh %s" % e)
            try:
                c.set_editor_property("relative_scale3d", unreal.Vector(SCALE, SCALE, SCALE))
            except Exception:
                pass
            L("inst %s mesh rel=%s" % (a.get_name(), c.get_relative_location()))
    except Exception as e:
        L("inst comps %s" % e)
    L("placed %s @ %s" % (a.get_name(), a.get_actor_location()))

# save
try:
    unreal.EditorAssetLibrary.save_asset(BP_PATH)
    L("saved BP")
except Exception as e:
    L("save bp %s" % e)
try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved level")
except Exception as e:
    L("save level %s" % e)

# final CDO verify
try:
    cdo2 = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH))
    m2 = cdo2.get_editor_property("mesh")
    c2 = cdo2.get_editor_property("capsule_component")
    L("FINAL mesh_rel=%s cap_half=%s" % (
        m2.get_editor_property("relative_location"),
        c2.get_editor_property("capsule_half_height"),
    ))
except Exception as e:
    L("final verify %s" % e)

L("DONE cause=mesh Z was -95 vs capsule half 55 (feet 40uu below floor)")
L("fix=mesh relative Z set to %s to match capsule bottom" % MESH_Z)
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
