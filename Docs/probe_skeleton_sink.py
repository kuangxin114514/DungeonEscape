# -*- coding: utf-8 -*-
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_skeleton_sink.txt"
lines = []

def L(s):
    lines.append(str(s))
    print(s)

BP_PATH = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
SK_PATH = "/Game/Characters/Enemies/Skeleton/Mesh/SK_SkeletonMinion"
MAP = "/Game/Maps/Map_Dungeon"

bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
L("bp=%s" % bp)
sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
L("sk=%s" % sk)

# bounds
try:
    bounds = sk.get_bounds()
    L("sk_bounds=%s" % bounds)
except Exception as e:
    L("bounds_err=%s" % e)
try:
    # UE4.27 SkeletalMesh imported bounds
    ib = sk.get_editor_property("imported_bounds")
    L("imported_bounds=%s" % ib)
except Exception as e:
    L("imported_bounds_err=%s" % e)
try:
    box = sk.get_bounds()
except Exception:
    pass
try:
    # get_mesh_scale_and_offset? try extend
    for prop in ("positive_bounds_extension","negative_bounds_extension"):
        try:
            L("%s=%s" % (prop, sk.get_editor_property(prop)))
        except Exception as e:
            L("%s err %s" % (prop, e))
except Exception:
    pass

# CDO
gc = None
try:
    gc = bp.generated_class()
except Exception:
    pass
if not gc:
    try:
        gc = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
    except Exception as e:
        L("load_bp_class err %s" % e)
L("generated_class=%s" % gc)
cdo = unreal.get_default_object(gc) if gc else None
L("cdo=%s" % cdo)

def dump_comp(name, comp):
    if not comp:
        L("%s=None" % name); return
    L("%s class=%s" % (name, comp.get_class().get_name()))
    for p in ("relative_location","relative_rotation","relative_scale3d","capsule_half_height","capsule_radius",
              "animation_mode","anim_class","skeletal_mesh","visibility_based_anim_tick_option"):
        try:
            L("  %s=%s" % (p, comp.get_editor_property(p)))
        except Exception as e:
            pass
    try:
        L("  loc=%s scale=%s" % (comp.get_relative_location(), comp.get_relative_scale3d()))
    except Exception:
        pass

if cdo:
    try:
        dump_comp("capsule", cdo.get_editor_property("capsule_component"))
    except Exception as e:
        L("cap err %s" % e)
    try:
        dump_comp("mesh", cdo.get_editor_property("mesh"))
    except Exception as e:
        L("mesh err %s" % e)
    try:
        dump_comp("char_move", cdo.get_editor_property("character_movement"))
    except Exception as e:
        L("move err %s" % e)

# world actors
try:
    unreal.EditorLevelLibrary.load_level(MAP)
except Exception as e:
    L("load_level %s" % e)

acts = unreal.EditorLevelLibrary.get_all_level_actors()
for a in acts:
    n = a.get_name()
    if "Skeleton" in n or "skeleton" in n:
        L("ACTOR %s class=%s loc=%s" % (n, a.get_class().get_name(), a.get_actor_location()))
        try:
            comps = a.get_components_by_class(unreal.SceneComponent)
            for c in comps:
                cn = c.get_name()
                if "Capsule" in cn or "Mesh" in cn or "Camera" in cn or cn in ("CollisionCylinder",):
                    try:
                        L("  comp %s rel=%s scale=%s" % (cn, c.get_relative_location(), c.get_relative_scale3d()))
                    except Exception:
                        L("  comp %s" % cn)
                    for p in ("capsule_half_height","capsule_radius","skeletal_mesh","animation_mode"):
                        try:
                            L("    %s=%s" % (p, c.get_editor_property(p)))
                        except Exception:
                            pass
        except Exception as e:
            L("  comps err %s" % e)

# knight for reference
KN = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
try:
    kgc = unreal.EditorAssetLibrary.load_blueprint_class(KN)
    kcdo = unreal.get_default_object(kgc)
    L("KNIGHT ref:")
    dump_comp("k_cap", kcdo.get_editor_property("capsule_component"))
    dump_comp("k_mesh", kcdo.get_editor_property("mesh"))
except Exception as e:
    L("knight ref err %s" % e)

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
L("WROTE " + OUT)
