# -*- coding: utf-8 -*-
"""T380 engine-style skeleton AI (MoveTo + OrientRotationToMovement).

UE4.27 Python cannot author BP EventGraph nodes (Nodes is protected), so the
decision brain is here, but locomotion uses engine AIController MoveTo / NavMesh
and CharacterMovement facing — not set_actor_location / yaw hacks.
"""
from __future__ import print_function
import math
import unreal

AGGRO_RANGE = 600.0
LOSE_RANGE = 900.0
ATTACK_RANGE = 200.0
ATTACK_DAMAGE = 5.0
ATTACK_COOLDOWN = 1.0
ATTACK_WINDUP = 0.2
ATTACK_HIT_DELAY = 0.5
CHASE_SPEED = 190.0
EYE_Z = 70.0
CHEST_Z = 60.0

ANIM_IDLE = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig"
ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig"  # upright loco (no lean run)
ANIM_WALK = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig"
STOP_BLEND = 0.45  # run -> walk -> idle
ANIM_ATK = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_1H_Melee_Attack_Chop_Rig"
ANIM_HIT = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Hit_A_Rig"

_ANIM_CACHE = {}
_STATE = {}
_LOG_ACC = [0.0]
_CTRL_TRIED = set()


def _log(msg):
    try:
        unreal.log("T380AI: " + str(msg))
    except Exception:
        print("T380AI:", msg)


def _alive(obj):
    if obj is None:
        return False
    try:
        if hasattr(obj, "is_valid") and (not obj.is_valid()):
            return False
    except Exception:
        pass
    try:
        _ = obj.get_name()
        return True
    except Exception:
        return False


def _key(actor):
    try:
        return actor.get_path_name()
    except Exception:
        return str(id(actor))


def _load_anim(path):
    if path in _ANIM_CACHE:
        return _ANIM_CACHE[path]
    seq = None
    try:
        seq = unreal.load_asset(path)
    except Exception:
        seq = None
    if seq is None:
        try:
            seq = unreal.EditorAssetLibrary.load_asset(path)
        except Exception:
            seq = None
    _ANIM_CACHE[path] = seq
    return seq


def _get_mesh(pawn):
    try:
        return pawn.get_editor_property("mesh")
    except Exception:
        pass
    try:
        return pawn.mesh
    except Exception:
        return None



def _anim_length(path):
    seq = _load_anim(path)
    if seq is None:
        return 1.0
    try:
        return max(0.35, float(seq.get_editor_property("sequence_length")))
    except Exception:
        pass
    try:
        return max(0.35, float(seq.sequence_length))
    except Exception:
        return 1.0


def _play_anim(pawn, path, looping):
    mesh = _get_mesh(pawn)
    seq = _load_anim(path)
    if mesh is None or seq is None:
        return False
    try:
        mesh.play_animation(seq, looping)
        return True
    except Exception:
        pass
    try:
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        mesh.play_animation(seq, looping)
        return True
    except Exception as e:
        _log("play_anim fail " + str(e))
        return False


def _dist(a, b):
    try:
        dx = float(a.x) - float(b.x)
        dy = float(a.y) - float(b.y)
        dz = float(a.z) - float(b.z)
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    except Exception:
        return 999999.0


def _trace_clear(world, start, end, ignore, trace_query):
    """True if nothing blocks, or only the player is hit."""
    try:
        result = unreal.SystemLibrary.line_trace_single(
            world,
            start,
            end,
            trace_query,
            True,
            ignore,
            unreal.DrawDebugTrace.NONE,
            True,
            unreal.LinearColor(1, 0, 0, 1),
            unreal.LinearColor(0, 1, 0, 1),
            0.0,
        )
    except Exception:
        return None
    if isinstance(result, (tuple, list)):
        blocking = bool(result[0]) if result else False
        hr = result[1] if len(result) > 1 else None
    else:
        try:
            blocking = bool(getattr(result, "blocking_hit", False))
        except Exception:
            blocking = False
        hr = result
    if not blocking:
        return True
    actor = None
    if hr is not None:
        try:
            actor = hr.get_editor_property("actor")
        except Exception:
            actor = getattr(hr, "actor", None)
    player = None
    try:
        player = ignore[1] if len(ignore) > 1 else None
    except Exception:
        player = None
    return actor is not None and player is not None and actor == player


def _has_los(world, enemy, player, controller=None):
    """Simple wall check via Visibility/Camera traces; any wall hit => no aggro."""
    try:
        el = enemy.get_actor_location()
        pl = player.get_actor_location()
        start = unreal.Vector(float(el.x), float(el.y), float(el.z) + EYE_Z)
        end = unreal.Vector(float(pl.x), float(pl.y), float(pl.z) + CHEST_Z)
        ignore = [enemy, player]
        queries = []
        try:
            queries.append(unreal.TraceTypeQuery.TRACE_TYPE_QUERY1)  # Visibility
        except Exception:
            pass
        try:
            queries.append(unreal.TraceTypeQuery.TRACE_TYPE_QUERY2)  # Camera
        except Exception:
            pass
        saw_clear = False
        for q in queries:
            got = _trace_clear(world, start, end, ignore, q)
            if got is None:
                continue
            if not got:
                return False
            saw_clear = True
        if saw_clear:
            return True
        # fallback: AIController LOS if traces unavailable
        if controller is not None:
            try:
                return bool(controller.line_of_sight_to(player))
            except Exception:
                pass
        return False
    except Exception as e:
        _log("los ERR " + str(e))
        return False


def _float_prop(obj, names, default):
    for n in names:
        try:
            v = obj.get_editor_property(n)
            if v is not None:
                return float(v)
        except Exception:
            pass
        try:
            v = getattr(obj, n, None)
            if v is not None:
                return float(v)
        except Exception:
            pass
    return default


def _damage_player(world, player, amount):
    try:
        import shop_interact_runtime as sir
        if hasattr(sir, "_damage_player"):
            sir._damage_player(world, player, amount)
            return
    except Exception:
        pass
    health = _float_prop(player, ("Health", "health", "HP", "Hp"), 100.0)
    maxh = _float_prop(player, ("MaxHealth", "max_health", "MaxHP", "MaxHp"), 100.0)
    health = max(0.0, health - float(amount))
    for name in ("Health", "health", "HP", "Hp"):
        try:
            player.set_editor_property(name, float(health))
        except Exception:
            try:
                setattr(player, name, float(health))
            except Exception:
                pass
    try:
        unreal.SystemLibrary.print_string(
            world,
            u"\u88ab\u51fb\u4e2d -%d  HP %.0f/%.0f" % (int(amount), health, maxh),
            True,
            False,
            unreal.LinearColor(1.0, 0.35, 0.3, 1.0),
            1.2,
        )
    except Exception:
        pass


def _is_skeleton(actor):
    try:
        cn = actor.get_class().get_name() if actor.get_class() else ""
        n = actor.get_name() or ""
    except Exception:
        return False
    return ("BP_Enemy_Skeleton" in cn) or ("Enemy_Skeleton" in cn) or ("BP_Enemy_Skeleton" in n)


def _list_skeletons(world):
    out = []
    for cls in (unreal.Character, unreal.Pawn):
        try:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
                if _alive(a) and _is_skeleton(a) and a not in out:
                    out.append(a)
        except Exception:
            pass
    return out


def _ensure_move_settings(pawn):
    try:
        mov = pawn.get_editor_property("character_movement")
    except Exception:
        mov = None
    if mov is not None:
        try:
            mov.set_editor_property("orient_rotation_to_movement", False)
            mov.set_editor_property("use_controller_desired_rotation", True)
            mov.set_editor_property("max_walk_speed", float(CHASE_SPEED))
            # keyword Rotator: positional args are NOT (pitch,yaw,roll) in UE4.27 Python
            mov.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0, yaw=720.0, roll=0.0))
        except Exception:
            pass
    try:
        pawn.set_editor_property("use_controller_rotation_yaw", False)
    except Exception:
        pass
    mesh = _get_mesh(pawn)
    if mesh is not None:
        try:
            mesh.set_simulate_physics(False)
        except Exception:
            pass


def _get_ai_controller(enemy):
    try:
        ctrl = enemy.get_controller()
    except Exception:
        ctrl = None
    if ctrl is not None and isinstance(ctrl, unreal.AIController):
        return ctrl
    return None



def _set_focus_player(controller, player):
    if controller is None or player is None:
        return
    try:
        controller.set_focus(player)
        return
    except Exception:
        pass
    try:
        controller.set_focal_point(player.get_actor_location())
    except Exception:
        pass


def _clear_focus(controller):
    if controller is None:
        return
    try:
        controller.clear_focus()
    except Exception:
        pass


def _add_input_toward(pawn, target_loc):
    """Fallback chase using CharacterMovement (OrientRotationToMovement faces walk dir)."""
    try:
        loc = pawn.get_actor_location()
        dx = float(target_loc.x) - float(loc.x)
        dy = float(target_loc.y) - float(loc.y)
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1.0:
            return False
        direction = unreal.Vector(dx / dist, dy / dist, 0.0)
        pawn.add_movement_input(direction, 1.0, False)
        return True
    except Exception:
        try:
            loc = pawn.get_actor_location()
            dx = float(target_loc.x) - float(loc.x)
            dy = float(target_loc.y) - float(loc.y)
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 1.0:
                return False
            direction = unreal.Vector(dx / dist, dy / dist, 0.0)
            pawn.add_movement_input(direction, 1.0)
            return True
        except Exception as e:
            _log("add_movement_input ERR " + str(e))
            return False


def _move_to(controller, player, pawn=None):
    if controller is not None:
        try:
            controller.move_to_actor(player, float(ATTACK_RANGE) * 0.45)
            return True
        except Exception:
            pass
        try:
            controller.move_to_location(player.get_actor_location(), float(ATTACK_RANGE) * 0.45)
            return True
        except Exception:
            pass
        try:
            liber = unreal.AIBlueprintHelperLibrary
            liber.simple_move_to_actor(controller, player)
            return True
        except Exception:
            pass
    if pawn is not None:
        try:
            return _add_input_toward(pawn, player.get_actor_location())
        except Exception:
            return False
    return False


def _stop_move(controller):
    try:
        controller.stop_movement()
    except Exception:
        pass


def _state_for(pawn):
    k = _key(pawn)
    st = _STATE.get(k)
    if st is None:
        st = {
            "aggro": False,
            "anim": None,
            "in_melee_since": 0.0,
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,
            "attack_until": 0.0,
            "hit_until": 0.0,
            "flinch_left": 2,
            "stop_until": 0.0,
            "t": 0.0,
        }
        _STATE[k] = st
    return st


def notify_hit(pawn):
    """Player hit: flinch up to 2 times (can interrupt attack); then armored until attack ends."""
    if pawn is None or (not _alive(pawn)):
        return False
    st = _state_for(pawn)
    now = float(st.get("t", 0.0) or 0.0)
    # out of flinch budget => hyper armor (even mid-attack)
    if int(st.get("flinch_left", 2) or 0) <= 0:
        return False
    dur = _anim_length(ANIM_HIT)
    st["hit_until"] = now + dur
    st["attack_hit_due"] = 0.0
    st["attack_until"] = 0.0  # interrupt attack if any
    st["last_attack_t"] = now
    st["in_melee_since"] = 0.0
    st["flinch_left"] = int(st.get("flinch_left", 2)) - 1
    _play_anim(pawn, ANIM_HIT, False)
    st["anim"] = "hit"
    try:
        ctrl = _get_ai_controller(pawn)
        if ctrl:
            _stop_move(ctrl)
    except Exception:
        pass
    return True



def _go_idle(pawn, st, now):
    """Run/stop: brief walk then idle so lean does not pop upright."""
    if st.get("anim") in ("run", "stop"):
        if st.get("anim") != "stop":
            _play_anim(pawn, ANIM_WALK, True)
            st["anim"] = "stop"
        st["stop_until"] = float(now) + float(STOP_BLEND)
        return
    if st.get("anim") != "idle":
        _play_anim(pawn, ANIM_IDLE, True)
        st["anim"] = "idle"
        st["stop_until"] = 0.0


def clear_state():
    _STATE.clear()
    _ANIM_CACHE.clear()
    _CTRL_TRIED.clear()


def tick_skeleton_engine_ai(world, player, dt):
    if world is None or player is None or (not _alive(player)):
        return
    dt = float(dt) if dt and dt > 0.0 else 0.016
    skeletons = _list_skeletons(world)
    _LOG_ACC[0] += dt
    do_log = _LOG_ACC[0] >= 2.5
    if do_log:
        _LOG_ACC[0] = 0.0
        _log("tick skeletons=%d" % len(skeletons))

    for enemy in skeletons:
        if (not _alive(enemy)) or enemy == player:
            continue
        st = _state_for(enemy)
        st["t"] = float(st.get("t", 0.0)) + dt
        now = st["t"]
        _ensure_move_settings(enemy)
        ctrl = _get_ai_controller(enemy)
        if ctrl is None:
            k = _key(enemy)
            if k not in _CTRL_TRIED:
                _CTRL_TRIED.add(k)
                if do_log:
                    _log("no AIController on " + enemy.get_name() + " (AutoPossessAI / NavMesh?)")

        # No damage resolve while flinching
        hit_until_early = float(st.get("hit_until", 0.0) or 0.0)
        due = float(st.get("attack_hit_due", 0.0) or 0.0)
        if due > 0.0 and now >= due:
            st["attack_hit_due"] = 0.0
            if hit_until_early <= 0.0 or now >= hit_until_early:
                try:
                    d = _dist(enemy.get_actor_location(), player.get_actor_location())
                except Exception:
                    d = 9999.0
                if d <= ATTACK_RANGE * 1.35:
                    _damage_player(world, player, ATTACK_DAMAGE)

        try:
            dist = _dist(enemy.get_actor_location(), player.get_actor_location())
        except Exception:
            continue

        # Hit react: play Hit_A, no attack / no chase until clip ends
        hit_until = float(st.get("hit_until", 0.0) or 0.0)
        if hit_until > 0.0 and now < hit_until:
            if ctrl:
                _stop_move(ctrl)
                _set_focus_player(ctrl, player)
            st["attack_hit_due"] = 0.0
            st["attack_until"] = 0.0
            if st.get("anim") != "hit":
                _play_anim(enemy, ANIM_HIT, False)
                st["anim"] = "hit"
            continue
        if hit_until > 0.0 and now >= hit_until:
            st["hit_until"] = 0.0
            if st.get("anim") == "hit":
                st["anim"] = None

        # Keep playing full attack clip once triggered (no early cut to run/idle)
        atk_until = float(st.get("attack_until", 0.0) or 0.0)
        if atk_until > 0.0 and now < atk_until:
            if ctrl:
                _stop_move(ctrl)
                _set_focus_player(ctrl, player)
            st["anim"] = "attack"
            continue
        if atk_until > 0.0 and now >= atk_until:
            st["attack_until"] = 0.0
            st["flinch_left"] = 2  # attack done: allow 2 flinches again
            if st.get("anim") == "attack":
                st["anim"] = None

        # Finish run-stop blend into idle
        stop_until = float(st.get("stop_until", 0.0) or 0.0)
        if st.get("anim") == "stop":
            if now < stop_until:
                if ctrl:
                    _stop_move(ctrl)
                continue
            _play_anim(enemy, ANIM_IDLE, True)
            st["anim"] = "idle"
            st["stop_until"] = 0.0

        if dist > LOSE_RANGE:
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            st["flinch_left"] = 2
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            _go_idle(enemy, st, now)
            continue

        los_ok = _has_los(world, enemy, player, ctrl)
        if not st["aggro"]:
            if dist <= AGGRO_RANGE and los_ok:
                st["aggro"] = True
                if ctrl:
                    _set_focus_player(ctrl, player)
                if do_log:
                    _log("aggro " + enemy.get_name())
            else:
                _go_idle(enemy, st, now)
                continue
        elif not los_ok:
            # simplest: wall / no sight => drop aggro, don't chase through walls
            st["aggro"] = False
            st["in_melee_since"] = 0.0
            st["flinch_left"] = 2
            if ctrl:
                _stop_move(ctrl)
                _clear_focus(ctrl)
            _go_idle(enemy, st, now)
            continue

        if dist <= ATTACK_RANGE:
            if ctrl:
                _stop_move(ctrl)
                _set_focus_player(ctrl, player)
            if float(st.get("in_melee_since", 0.0) or 0.0) <= 0.0:
                st["in_melee_since"] = now
            windup_ok = (now - float(st["in_melee_since"])) >= ATTACK_WINDUP
            cd_ok = (now - float(st.get("last_attack_t", 0.0))) >= ATTACK_COOLDOWN
            if windup_ok and cd_ok and float(st.get("attack_hit_due", 0.0) or 0.0) <= 0.0 and float(st.get("hit_until", 0.0) or 0.0) <= now:
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + ATTACK_HIT_DELAY
                st["attack_until"] = now + _anim_length(ANIM_ATK)
                _play_anim(enemy, ANIM_ATK, False)
                st["anim"] = "attack"
            elif st.get("anim") != "attack":
                # windup: stand idle (not run) until chop starts
                if st.get("anim") != "idle":
                    _play_anim(enemy, ANIM_IDLE, True)
                    st["anim"] = "idle"
            continue

        st["in_melee_since"] = 0.0
        if ctrl:
            _set_focus_player(ctrl, player)
        _move_to(ctrl, player, enemy)
        if st.get("anim") != "run":
            if st.get("anim") == "attack" and float(st.get("attack_until", 0.0) or 0.0) > now:
                pass
            else:
                _play_anim(enemy, ANIM_RUN, True)
                st["anim"] = "run"
