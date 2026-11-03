# -*- coding: utf-8 -*-
import ast
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
t=open(p,encoding="utf-8").read()
a=t.find("def ensure_equipped_pawn_class")
b=t.find("def _force_sword1_mesh_on_pawn")
if b<0: b=t.find("def apply_equipped_sword_to_pawn")
if a<0 or b<0: raise SystemExit("bounds %s %s"%(a,b))
new='''def ensure_equipped_pawn_class(world_ctx, force=False):
    """Possess BP_KayKitKnight or BP_KayKitKnight_Sword1. Never edits sword transforms — use authored BP."""
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
    # force=True always respawn so latest BP edits (your tuned sword) apply
    if (not force) and _class_path_matches(pawn, want):
        return True
    if force and _class_path_matches(pawn, want):
        # same class: still respawn from BP to pick up saved component transforms
        pass
    elif _class_path_matches(pawn, want):
        return True
    cls = unreal.load_class(None, want)
    if cls is None:
        _log("pawn swap FAIL load " + want)
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
    xf = unreal.Transform(loc, rot, unreal.Vector(1.0, 1.0, 1.0))
    new_pawn = None
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
        _log("pawn swap spawn None")
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
        return False
    try:
        pc.set_control_rotation(ctrl)
    except Exception:
        pass
    try:
        if old != new_pawn:
            old.destroy_actor()
    except Exception as e:
        _log("pawn swap destroy old " + str(e))
    _PAWN_SWAP_KEY[0] = None
    _log("pawn swap OK -> %s (trust BP transforms)" % want)
    return True


'''
# If _force exists, keep function but unused; replace ensure only through apply shim
c=t.find("def apply_equipped_sword_to_pawn")
if c>a:
    t=t[:a]+new+t[c:]
else:
    t=t[:a]+new+t[b:]
# buy always force=True already
if "T339_TRUST_USER_BP" not in t:
    t=t.replace("T334_TRUST_BP","T334_TRUST_BP T339_TRUST_USER_BP",1)
open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("SYNTAX_OK")
