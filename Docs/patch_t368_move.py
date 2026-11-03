# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re
RUNTIME = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t368_move.txt"
log=[]
def L(m):
    log.append(str(m)); print(m)
with io.open(RUNTIME,"r",encoding="utf-8") as f:
    src=f.read()

old = '''def _move_actor_toward(actor, target_loc, speed, dt):
    """Simple chase: face target and set_actor_location with sweep. Returns dist left."""
    try:
        al = actor.get_actor_location()
    except Exception:
        return 99999.0
    dx = float(target_loc.x) - float(al.x)
    dy = float(target_loc.y) - float(al.y)
    dz = 0.0  # keep ground height; Z from current
    dist_xy = (dx * dx + dy * dy) ** 0.5
    if dist_xy < 1.0:
        return dist_xy
    _look_at_xy(actor, target_loc)
    step = float(speed) * float(dt)
    if step > dist_xy:
        step = dist_xy
    nx = float(al.x) + dx / dist_xy * step
    ny = float(al.y) + dy / dist_xy * step
    nz = float(al.z)
    # Prefer CharacterMovement add_movement_input when available (smoother); fallback teleport-sweep
    moved = False
    try:
        if isinstance(actor, unreal.Character):
            direction = unreal.Vector(dx / dist_xy, dy / dist_xy, 0.0)
            scale = min(1.0, step / max(1.0, float(speed) * max(float(dt), 0.001)))
            # scale ~1 when full speed; CharacterMovement uses input each tick
            actor.add_movement_input(direction, 1.0, False)
            # Also bump max walk speed if we can
            try:
                mc = actor.get_movement_component()
                if mc is not None:
                    try:
                        mc.set_editor_property("max_walk_speed", float(speed))
                    except Exception:
                        try:
                            mc.max_walk_speed = float(speed)
                        except Exception:
                            pass
            except Exception:
                pass
            moved = True
    except Exception:
        moved = False
    if not moved:
        try:
            actor.set_actor_location(unreal.Vector(nx, ny, nz), True, False)
            moved = True
        except Exception:
            try:
                actor.set_actor_location(unreal.Vector(nx, ny, nz), False, True)
            except Exception as e:
                _log("T368 move fail " + str(e))
    try:
        al2 = actor.get_actor_location()
        dx2 = float(target_loc.x) - float(al2.x)
        dy2 = float(target_loc.y) - float(al2.y)
        return (dx2 * dx2 + dy2 * dy2) ** 0.5
    except Exception:
        return dist_xy
'''

new = '''def _move_actor_toward(actor, target_loc, speed, dt):
    """Simple chase: face target and set_actor_location with sweep (slate-tick safe). Returns dist left."""
    try:
        al = actor.get_actor_location()
    except Exception:
        return 99999.0
    dx = float(target_loc.x) - float(al.x)
    dy = float(target_loc.y) - float(al.y)
    dist_xy = (dx * dx + dy * dy) ** 0.5
    if dist_xy < 1.0:
        return dist_xy
    _look_at_xy(actor, target_loc)
    step = float(speed) * float(dt)
    if step > dist_xy:
        step = dist_xy
    nx = float(al.x) + dx / dist_xy * step
    ny = float(al.y) + dy / dist_xy * step
    nz = float(al.z)
    # Slate post-tick: CharacterMovement already ran, so drive with swept set_actor_location.
    # Still nudge max_walk_speed / add_movement_input as a soft assist if present.
    try:
        if isinstance(actor, unreal.Character):
            try:
                mc = actor.get_movement_component()
                if mc is not None:
                    try:
                        mc.set_editor_property("max_walk_speed", float(speed))
                    except Exception:
                        try:
                            mc.max_walk_speed = float(speed)
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                actor.add_movement_input(unreal.Vector(dx / dist_xy, dy / dist_xy, 0.0), 1.0, False)
            except Exception:
                pass
    except Exception:
        pass
    try:
        actor.set_actor_location(unreal.Vector(nx, ny, nz), True, False)
    except Exception:
        try:
            actor.set_actor_location(unreal.Vector(nx, ny, nz), False, True)
        except Exception as e:
            _log("T368 move fail " + str(e))
    try:
        al2 = actor.get_actor_location()
        dx2 = float(target_loc.x) - float(al2.x)
        dy2 = float(target_loc.y) - float(al2.y)
        return (dx2 * dx2 + dy2 * dy2) ** 0.5
    except Exception:
        return dist_xy
'''

if old not in src:
    L("OLD move fn not exact match — trying regex replace")
    m = re.search(r"def _move_actor_toward\(actor, target_loc, speed, dt\):\n(?:.*\n)*?    except Exception:\n        return dist_xy\n", src)
    if not m:
        L("FAIL find _move_actor_toward")
        open(OUT,"w",encoding="utf-8").write("\n".join(log)); raise SystemExit(1)
    src = src[:m.start()] + new + src[m.end():]
    L("replaced via regex")
else:
    src = src.replace(old, new, 1)
    L("replaced exact move fn")

with io.open(RUNTIME,"w",encoding="utf-8",newline="\n") as f:
    f.write(src)
L("ok slate-tick set_actor_location chase")
open(OUT,"w",encoding="utf-8").write("\n".join(log)+"\n")
