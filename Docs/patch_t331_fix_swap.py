# -*- coding: utf-8 -*-
import ast, shutil
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copyfile(p, p + ".pre_t331_fix_swap")
t = open(p, encoding="utf-8").read()

# Replace _class_path_matches with strict match
old_match = '''def _class_path_matches(obj, class_path):
    if obj is None or not class_path:
        return False
    try:
        cp = obj.get_class().get_path_name()
    except Exception:
        cp = ""
    if cp == class_path:
        return True
    base = class_path.replace("_C", "").split(".")[-1]
    try:
        cn = obj.get_class().get_name()
    except Exception:
        cn = ""
    return base in cn or cn in class_path
'''
new_match = '''def _class_path_matches(obj, class_path):
    if obj is None or not class_path:
        return False
    try:
        cp = obj.get_class().get_path_name()
    except Exception:
        cp = ""
    if cp == class_path:
        return True
    try:
        cn = obj.get_class().get_name()
    except Exception:
        cn = ""
    want = class_path.split(".")[-1]  # BP_KayKitKnight_Sword1_C
    # Exact generated-class name only (avoid BP_KayKitKnight matching *Sword1*)
    return cn == want or cn == want.replace("_C", "")
'''
if old_match not in t:
    raise SystemExit("match fn missing")
t = t.replace(old_match, new_match, 1)

# Replace ensure_equipped_pawn_class with more robust spawn + mesh fallback
a = t.find("def ensure_equipped_pawn_class")
b = t.find("def apply_equipped_sword_to_pawn")
if a < 0 or b < 0:
    raise SystemExit("ensure bounds missing")

new_ensure = r'''def ensure_equipped_pawn_class(world_ctx, force=False):
    """Swap possessed pawn between default knight / sword1 knight by equipped item."""
    if world_ctx is None:
        return False
    ensure_player_meta(world_ctx)
    want = desired_knight_class_path(world_ctx)
    pc = unreal.GameplayStatics.get_player_controller(world_ctx, 0)
    if pc is None:
        return False
    try:
        pawn = pc.get_controlled_pawn()
    except Exception:
        pawn = None
    if pawn is None:
        return False
    if _class_path_matches(pawn, want):
        # Still force sword mesh if this is the sword1 BP (template may not have applied).
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            _force_sword1_mesh_on_pawn(pawn)
        return True
    cls = unreal.load_class(None, want)
    if cls is None:
        _log("pawn swap FAIL load " + want)
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            return _force_sword1_mesh_on_pawn(pawn)
        return False
    try:
        loc = pawn.get_actor_location()
        rot = pawn.get_actor_rotation()
    except Exception as e:
        _log("pawn swap get xform " + str(e))
        return False
    try:
        ctrl = pc.get_control_rotation()
    except Exception:
        ctrl = rot
    xf = unreal.Transform(rot, loc, unreal.Vector(1.0, 1.0, 1.0))
    new_pawn = None
    # Preferred: deferred spawn (works in PIE)
    try:
        deferred = unreal.GameplayStatics.begin_deferred_actor_spawn_from_class(
            world_ctx, cls, xf, unreal.ESpawnActorCollisionHandlingMethod.ALWAYS_SPAWN
        )
        if deferred is not None:
            new_pawn = unreal.GameplayStatics.finish_spawning_actor(deferred, xf)
    except Exception as e:
        _log("pawn swap deferred " + str(e))
        new_pawn = None
    if new_pawn is None:
        try:
            new_pawn = world_ctx.spawn_actor(cls, loc, rot)
        except Exception as e:
            _log("pawn swap spawn_actor " + str(e))
            new_pawn = None
    if new_pawn is None:
        try:
            new_pawn = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)
        except Exception as e:
            _log("pawn swap editor_spawn " + str(e))
            new_pawn = None
    if new_pawn is None:
        _log("pawn swap spawn None; fallback mesh on current pawn")
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            return _force_sword1_mesh_on_pawn(pawn)
        return False
    old = pawn
    try:
        pc.possess(new_pawn)
    except Exception as e:
        _log("pawn swap possess " + str(e))
        try:
            new_pawn.destroy_actor()
        except Exception:
            pass
        if get_equipped_sword(world_ctx) == SWORD1_ITEM:
            return _force_sword1_mesh_on_pawn(old)
        return False
    try:
        pc.set_control_rotation(ctrl)
    except Exception:
        pass
    try:
        # Keep level-placed default knight if present: only destroy if not the same as new
        if old != new_pawn:
            old.destroy_actor()
    except Exception as e:
        _log("pawn swap destroy old " + str(e))
    if get_equipped_sword(world_ctx) == SWORD1_ITEM:
        _force_sword1_mesh_on_pawn(new_pawn)
    _PAWN_SWAP_KEY[0] = None
    _log("pawn swap OK -> %s equipped=%s" % (want, get_equipped_sword(world_ctx)))
    return True


def _force_sword1_mesh_on_pawn(pawn):
    """Guarantee SM_KayKitSword_2H on the right-hand static mesh (scale from SWORD1_SCALE)."""
    if pawn is None:
        return False
    mesh = _load_sword_mesh_asset(SWORD1_MESH)
    if mesh is None:
        _log("force sword1 mesh FAIL load")
        return False
    scale = float(SWORD1_SCALE)
    # Prefer relative authored on sword1 BP if present; still set mesh asset.
    comps = []
    try:
        comps = list(pawn.get_components_by_class(unreal.StaticMeshComponent.static_class()) or [])
    except Exception:
        comps = []
    # Also scan by path if empty
    if not comps:
        try:
            base = pawn.get_path_name()
            for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
                try:
                    if base in o.get_path_name():
                        comps.append(o)
                except Exception:
                    pass
        except Exception:
            pass
    ok = 0
    for c in comps:
        try:
            cur = c.get_editor_property("static_mesh")
        except Exception:
            cur = None
        try:
            cname = c.get_name() or ""
        except Exception:
            cname = ""
        cur_name = cur.get_name() if cur else ""
        is_sword = (
            cur_name in ("SM_KayKitSword", "SM_KayKitSword_2H", "SM_KayKitSword_2H_Color")
            or "Sword" in cname
            or (cname.startswith("StaticMesh") and "StaticMesh1" not in cname and cur_name != "SM_KayKitShield")
        )
        if not is_sword:
            continue
        if cur_name == "SM_KayKitShield":
            continue
        try:
            c.set_static_mesh(mesh)
        except Exception:
            try:
                c.set_editor_property("static_mesh", mesh)
            except Exception as e:
                _log("force mesh " + str(e))
                continue
        try:
            c.set_relative_scale3d(unreal.Vector(scale, scale, scale))
        except Exception:
            try:
                c.set_editor_property("relative_scale3d", unreal.Vector(scale, scale, scale))
            except Exception:
                pass
        ok += 1
    _log("force sword1 mesh comps=%d scale=%s" % (ok, scale))
    return ok > 0


'''

t = t[:a] + new_ensure + t[b:]

# Use a more visible default scale for sword1 until user tunes BP — current 0.1 is tiny;
# screenshot looked like default sword, so mesh likely never applied. Keep 0.45 for visibility.
t = t.replace("SWORD1_SCALE = 0.1  # 2H mesh used as 1H on handslot_r", "SWORD1_SCALE = 0.45  # 2H mesh used as 1H on handslot_r", 1)

if "T331_FIX_SWAP" not in t:
    t = t.replace("T330_MULTI_CHAR", "T330_MULTI_CHAR T331_FIX_SWAP", 1)

open(p, "w", encoding="utf-8").write(t)
ast.parse(t)
print("SYNTAX_OK")
print("force", "def _force_sword1_mesh_on_pawn" in t)
print("deferred", "begin_deferred_actor_spawn_from_class" in t)
print("scale", "SWORD1_SCALE = 0.45" in t)
