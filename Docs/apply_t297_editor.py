# -*- coding: utf-8 -*-
"""T297 editor: enlarge BP_Enemy_Skeleton capsule + reload shop_interact_runtime (no enemy HP bars)."""
from __future__ import print_function
import unreal
import importlib
import sys
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\apply_t297.txt"
BP_PATH = "/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("T297: " + str(m))
    except Exception:
        print(m)

def save_asset(asset):
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(asset)
        return True
    except Exception as e:
        log("save_loaded_asset " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(BP_PATH)
        return True
    except Exception as e2:
        log("save_asset " + str(e2))
    return False

def enlarge_capsule():
    """Bump capsule radius (main anti-clip); slight half-height; keep feet on ground."""
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if bp is None:
        log("FAIL load BP " + BP_PATH)
        return False
    cls = unreal.load_class(None, BP_PATH + ".BP_Enemy_Skeleton_C")
    if cls is None:
        # try generated class from BP
        try:
            cls = bp.generated_class()
        except Exception:
            cls = None
    if cls is None:
        log("FAIL no class")
        return False
    cdo = unreal.get_default_object(cls)
    cap = None
    for getter in (
        lambda: cdo.get_editor_property("capsule_component"),
        lambda: getattr(cdo, "capsule_component", None),
        lambda: cdo.get_editor_property("CapsuleComponent"),
    ):
        try:
            cap = getter()
            if cap is not None:
                break
        except Exception:
            cap = None
    if cap is None:
        log("FAIL no capsule on CDO")
        return False

    def read_f(obj, names, default=None):
        for n in names:
            try:
                v = obj.get_editor_property(n)
                if v is not None:
                    return float(v)
            except Exception:
                pass
        return default

    old_r = read_f(cap, ("capsule_radius", "CapsuleRadius"), 34.0)
    old_h = read_f(cap, ("capsule_half_height", "CapsuleHalfHeight"), 88.0)
    log("capsule before r=%.2f h=%.2f" % (old_r, old_h))

    # Horizontal block is what stops camera diving into mesh; keep height almost same.
    new_r = max(old_r * 1.45, old_r + 16.0)
    new_h = max(old_h * 1.08, old_h + 6.0)
    # Clamp to sane Character sizes
    if new_r > 70.0:
        new_r = 70.0
    if new_h > 120.0:
        new_h = 120.0

    try:
        cap.set_editor_property("capsule_radius", float(new_r))
        cap.set_editor_property("capsule_half_height", float(new_h))
    except Exception as e:
        log("set capsule props " + str(e))
        try:
            cap.set_capsule_size(float(new_r), float(new_h), True)
            log("used set_capsule_size")
        except Exception as e2:
            log("FAIL set_capsule_size " + str(e2))
            return False

    # Keep mesh feet on floor: relative Z ~= -half_height
    mesh = None
    for getter in (
        lambda: cdo.get_editor_property("mesh"),
        lambda: getattr(cdo, "mesh", None),
    ):
        try:
            mesh = getter()
            if mesh is not None:
                break
        except Exception:
            mesh = None
    if mesh is not None:
        try:
            loc = mesh.get_editor_property("relative_location")
            old_z = float(loc.z)
            # Prefer -new_h if previously near -old_h; else shift by delta
            if abs(old_z + old_h) < 8.0:
                new_z = -float(new_h)
            else:
                new_z = old_z - (float(new_h) - float(old_h))
            mesh.set_editor_property("relative_location", unreal.Vector(float(loc.x), float(loc.y), new_z))
            log("mesh rel Z %.2f -> %.2f" % (old_z, new_z))
        except Exception as e:
            log("mesh z adjust " + str(e))

    # Ensure capsule blocks pawn/camera (BlockAllDynamic / Block pawns)
    try:
        cap.set_collision_profile_name("Pawn")
        log("capsule collision profile Pawn")
    except Exception as e:
        log("collision profile " + str(e))
    try:
        cap.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except Exception as e:
        log("collision enabled " + str(e))

    ok = save_asset(bp)
    # Also compile BP if possible
    try:
        if hasattr(unreal, "KismetSystemLibrary"):
            pass
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        log("compiled BP")
    except Exception as e:
        log("compile skip " + str(e))
    ok2 = save_asset(bp)
    log("capsule after r=%.2f h=%.2f save=%s/%s" % (new_r, new_h, ok, ok2))

    # Apply to placed instances in current editor world (PIE or editor)
    try:
        world = None
        try:
            world = unreal.EditorLevelLibrary.get_editor_world()
        except Exception:
            world = None
        n = 0
        if world is not None and cls is not None:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
                try:
                    acap = a.get_editor_property("capsule_component")
                    if acap is None:
                        acap = getattr(a, "capsule_component", None)
                    if acap is not None:
                        try:
                            acap.set_capsule_size(float(new_r), float(new_h), True)
                        except Exception:
                            acap.set_editor_property("capsule_radius", float(new_r))
                            acap.set_editor_property("capsule_half_height", float(new_h))
                        n += 1
                except Exception:
                    pass
        log("updated %d live skeleton capsules in editor world" % n)
    except Exception as e:
        log("live instance update " + str(e))
    return True

def reload_runtime():
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path:
        sys.path.insert(0, py)
    dst = os.path.join(py, "shop_interact_runtime.py")
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
        log("reloaded shop_interact_runtime")
    else:
        import shop_interact_runtime as m
        log("imported shop_interact_runtime")
    enabled = getattr(m, "ENEMY_HP_BARS_ENABLED", "MISSING")
    log("ENEMY_HP_BARS_ENABLED=%s" % enabled)
    tag = "NO"
    try:
        t = open(dst, encoding="utf-8").read()
        if "T297_NO_ENEMY_HP" in t and "ENEMY_HP_BARS_ENABLED = False" in t:
            tag = "T297_NO_ENEMY_HP"
    except Exception as e:
        tag = "readerr " + str(e)
    log("file_tag=" + tag)
    fn = getattr(m, "bootstrap", None)
    if callable(fn):
        try:
            fn()
            log("bootstrap ok")
        except Exception as e:
            log("bootstrap err " + str(e))
    try:
        clr = getattr(m, "_clear_enemy_bars", None)
        if callable(clr):
            clr(True)
            log("cleared enemy bars")
    except Exception as e:
        log("clear err " + str(e))
    try:
        purge = getattr(m, "_purge_enemy_viewport_widgets", None)
        if callable(purge):
            purge()
            log("purged viewport enemy widgets")
    except Exception as e:
        log("purge err " + str(e))
    return tag

def main():
    log("BEGIN T297")
    try:
        enlarge_capsule()
    except Exception as e:
        log("capsule EXC " + str(e))
    try:
        tag = reload_runtime()
        log("reload_tag=" + str(tag))
    except Exception as e:
        log("reload EXC " + str(e))
    log("DONE")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("WROTE", OUT)

main()
