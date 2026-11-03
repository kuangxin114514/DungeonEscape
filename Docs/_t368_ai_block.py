# ===== BEGIN T368_SKELETON_AI =====
# Skeleton minion aggro/chase/attack driven from the same slate tick as shop combat.
# Aggro requires: within AGGRO_RANGE AND clear line-of-sight (line trace). Walls block aggro.
SKELETON_AGGRO_RANGE = 1000.0       # cm — max detect distance
SKELETON_LOSE_RANGE = 1400.0        # cm — drop chase beyond this (even with LOS)
SKELETON_ATTACK_RANGE = 180.0       # cm — melee
SKELETON_CHASE_SPEED = 380.0        # cm/s
SKELETON_ATTACK_DAMAGE = 5.0        # damage to player per hit
SKELETON_ATTACK_COOLDOWN = 1.6      # seconds between attacks
SKELETON_ATTACK_HIT_DELAY = 0.35    # seconds after attack start before applying damage
SKELETON_EYE_Z = 70.0               # cm above actor root for LOS start
SKELETON_PLAYER_CHEST_Z = 60.0      # cm above player root for LOS end
PLAYER_MAX_HEALTH_DEFAULT = 100.0
SKELETON_ANIM_IDLE = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Unarmed_Idle_Rig",
)
SKELETON_ANIM_RUN = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
)
SKELETON_ANIM_ATTACK = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_1H_Melee_Attack_Chop_Rig",
)
_SKELETON_AI = {}  # actor path -> ai state dict
_SKELETON_ANIM_CACHE = {}  # kind -> AnimationSequence or None
_PLAYER_HP_CACHE = {"health": PLAYER_MAX_HEALTH_DEFAULT, "max_health": PLAYER_MAX_HEALTH_DEFAULT, "dead": False}
_SKELETON_AI_ACC = [0.0]
_SKELETON_AI_LOG_ACC = [0.0]


def _load_skeleton_anim(kind):
    """kind: idle|run|attack. Cache first loadable sequence."""
    if kind in _SKELETON_ANIM_CACHE:
        return _SKELETON_ANIM_CACHE[kind]
    paths = SKELETON_ANIM_IDLE
    if kind == "run":
        paths = SKELETON_ANIM_RUN
    elif kind == "attack":
        paths = SKELETON_ANIM_ATTACK
    seq = None
    for p in paths:
        try:
            seq = unreal.load_asset(p)
        except Exception:
            seq = None
        if seq is None:
            try:
                seq = unreal.EditorAssetLibrary.load_asset(p)
            except Exception:
                seq = None
        if seq is not None:
            break
    _SKELETON_ANIM_CACHE[kind] = seq
    if seq is None:
        _log("T368_SKELETON_AI missing anim kind=%s" % kind)
    return seq


def _skeleton_ai_state(actor):
    key = _enemy_cache_key(actor)
    st = _SKELETON_AI.get(key)
    if st is None:
        spawn = None
        try:
            spawn = actor.get_actor_location()
        except Exception:
            spawn = None
        st = {
            "state": "idle",          # idle|chase|attack
            "anim": None,             # idle|run|attack
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,    # when to apply pending damage (0=none)
            "spawn_loc": spawn,
            "aggro": False,
        }
        _SKELETON_AI[key] = st
    return st


def _clear_skeleton_ai():
    try:
        _SKELETON_AI.clear()
    except Exception:
        pass
    _SKELETON_AI_ACC[0] = 0.0
    try:
        _SKELETON_ANIM_CACHE.clear()
    except Exception:
        pass


def _ensure_player_hp(pawn):
    """Make sure player has Health/MaxHealth (default 100). Returns (health, maxh)."""
    if pawn is None:
        return float(_PLAYER_HP_CACHE["health"]), float(_PLAYER_HP_CACHE["max_health"])
    maxh = _float_prop(pawn, ("MaxHealth", "max_health", "MaxHP", "MaxHp"), None)
    health = _float_prop(pawn, ("Health", "health", "HP", "Hp"), None)
    if maxh is None or maxh <= 0.0001:
        maxh = float(_PLAYER_HP_CACHE.get("max_health", PLAYER_MAX_HEALTH_DEFAULT) or PLAYER_MAX_HEALTH_DEFAULT)
    if health is None:
        health = float(_PLAYER_HP_CACHE.get("health", maxh))
    if health > maxh:
        health = maxh
    _PLAYER_HP_CACHE["health"] = float(health)
    _PLAYER_HP_CACHE["max_health"] = float(maxh)
    for name, val in (("Health", health), ("MaxHealth", maxh), ("health", health), ("max_health", maxh)):
        try:
            pawn.set_editor_property(name, float(val))
        except Exception:
            try:
                setattr(pawn, name, float(val))
            except Exception:
                pass
    return float(health), float(maxh)


def _set_player_hp(pawn, health, maxh=None):
    if maxh is None:
        maxh = float(_PLAYER_HP_CACHE.get("max_health", PLAYER_MAX_HEALTH_DEFAULT))
    health = max(0.0, float(health))
    maxh = float(maxh) if float(maxh) > 0.0001 else PLAYER_MAX_HEALTH_DEFAULT
    if health > maxh:
        health = maxh
    _PLAYER_HP_CACHE["health"] = health
    _PLAYER_HP_CACHE["max_health"] = maxh
    if pawn is not None:
        for name, val in (("Health", health), ("MaxHealth", maxh), ("health", health), ("max_health", maxh)):
            try:
                pawn.set_editor_property(name, float(val))
            except Exception:
                try:
                    setattr(pawn, name, float(val))
                except Exception:
                    pass
    return health, maxh


def _reset_player_hp(pawn=None):
    _PLAYER_HP_CACHE["health"] = PLAYER_MAX_HEALTH_DEFAULT
    _PLAYER_HP_CACHE["max_health"] = PLAYER_MAX_HEALTH_DEFAULT
    _PLAYER_HP_CACHE["dead"] = False
    if pawn is not None:
        _set_player_hp(pawn, PLAYER_MAX_HEALTH_DEFAULT, PLAYER_MAX_HEALTH_DEFAULT)


def _damage_player(world, pawn, amount):
    """Apply skeleton attack damage; print; mark dead at 0 (minimal — no hard reset)."""
    if pawn is None or _PLAYER_HP_CACHE.get("dead"):
        return
    health, maxh = _ensure_player_hp(pawn)
    health = max(0.0, health - float(amount))
    _set_player_hp(pawn, health, maxh)
    _print(world, u"被骷髅击中 -%d  HP %.0f/%.0f" % (int(amount), health, maxh), (1.0, 0.35, 0.3, 1.0), 1.2)
    _log("T368_SKELETON_AI player hit -%s HP=%.0f/%.0f" % (amount, health, maxh))
    if health <= 0.0001:
        _PLAYER_HP_CACHE["dead"] = True
        _print(world, u"你倒下了（HP 0）— 停掉 PIE 再进可重置", (1.0, 0.2, 0.2, 1.0), 4.0)
        _log("T368_SKELETON_AI player dead")


def _skeleton_play_anim(actor, kind, looping):
    """Play idle/run/attack on skeleton mesh via Animation Single Node."""
    mesh = _get_pawn_mesh(actor)
    if mesh is None:
        return False
    seq = _load_skeleton_anim(kind)
    if seq is None:
        return False
    try:
        try:
            mesh.set_editor_property("anim_class", None)
        except Exception:
            pass
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception as e:
        _log("T368 anim mode " + str(e))
    used = ""
    try:
        mesh.override_animation_data(seq, bool(looping), bool(looping), 0.0, 1.0)
        used = "override"
    except Exception:
        try:
            mesh.set_animation(seq)
            if looping:
                try:
                    mesh.play(True)
                except Exception:
                    mesh.play_animation(seq, True)
            else:
                mesh.play_animation(seq, False)
            used = "play_animation"
        except Exception as e2:
            _log("T368 play anim fail kind=%s %s" % (kind, e2))
            return False
    st = _skeleton_ai_state(actor)
    st["anim"] = kind
    return True


def _look_at_xy(actor, target_loc):
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 1.0:
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx))
        actor.set_actor_rotation(unreal.Rotator(0.0, yaw, 0.0), False)
    except Exception:
        pass


def _move_actor_toward(actor, target_loc, speed, dt):
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


def _has_line_of_sight(world, enemy, pawn):
    """True if Visibility line trace from enemy eye to player chest is clear (or hits player).
    Walls/geometry blocking the trace => False. Radius is checked by caller.
    """
    if world is None or enemy is None or pawn is None:
        return False
    try:
        el = enemy.get_actor_location()
        pl = pawn.get_actor_location()
    except Exception:
        return False
    start = unreal.Vector(float(el.x), float(el.y), float(el.z) + float(SKELETON_EYE_Z))
    end = unreal.Vector(float(pl.x), float(pl.y), float(pl.z) + float(SKELETON_PLAYER_CHEST_Z))
    ignore = None
    try:
        ignore = unreal.Array(unreal.Actor)
        ignore.append(enemy)
        # Do NOT ignore pawn first — if we hit pawn, that is still "seen".
        # Also append nothing else.
    except Exception:
        ignore = []
    hit = None
    try:
        hit = unreal.SystemLibrary.line_trace_single(
            world,
            start,
            end,
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
            False,
            ignore,
            unreal.DrawDebugTrace.NONE,
            True,
        )
    except Exception as e:
        _log("T368 LOS trace fail " + str(e))
        # Fail closed? Prefer fail open for course playability if API quirks — but user asked for walls.
        # On API error, treat as NO sight to avoid false aggro through walls when channel wrong.
        return False
    if hit is None:
        return True  # no blocking hit along segment
    # Hit something — allow if it is the player (or owned by player)
    hit_actor = None
    for getter in (
        lambda: hit.actor,
        lambda: hit.get_editor_property("actor"),
        lambda: getattr(hit, "actor", None),
    ):
        try:
            hit_actor = getter()
            if hit_actor is not None:
                break
        except Exception:
            hit_actor = None
    # Some bindings wrap actor as weak ptr / HitActor
    if hit_actor is None:
        for name in ("HitActor", "hit_actor"):
            try:
                hit_actor = hit.get_editor_property(name)
                if hit_actor is not None:
                    break
            except Exception:
                pass
    if hit_actor is None:
        # Got a hit struct but cannot resolve actor — treat as blocked (safer for walls)
        blocking = True
        try:
            blocking = bool(hit.get_editor_property("blocking_hit"))
        except Exception:
            try:
                blocking = bool(getattr(hit, "blocking_hit", True))
            except Exception:
                blocking = True
        return (not blocking)
    # Same actor as pawn?
    try:
        if hit_actor == pawn:
            return True
    except Exception:
        pass
    try:
        if hit_actor.get_path_name() == pawn.get_path_name():
            return True
    except Exception:
        pass
    # Owned by pawn / attach parent
    try:
        outer = hit_actor.get_attach_parent_actor()
        if outer == pawn:
            return True
    except Exception:
        pass
    return False


def _skeleton_can_aggro(world, enemy, pawn, dist):
    if dist > float(SKELETON_AGGRO_RANGE):
        return False
    return _has_line_of_sight(world, enemy, pawn)


def update_skeleton_ai(world, pawn, dt):
    """T368_SKELETON_AI: Idle -> (range+LOS) Chase(run anim) -> Attack(anim+5 dmg). Walls block aggro."""
    if world is None or pawn is None:
        return
    if _PLAYER_HP_CACHE.get("dead"):
        # Still allow anim idle; stop chasing
        pass
    try:
        _ensure_player_hp(pawn)
    except Exception:
        pass
    try:
        pl = pawn.get_actor_location()
    except Exception:
        return
    now = time.time()
    dt = float(dt) if dt and float(dt) > 0.0 else 0.016
    if dt > 0.1:
        dt = 0.05  # slate hitch clamp
    for enemy in _list_live_enemy_actors(world):
        if enemy is None or (not _uobj_alive(enemy)):
            continue
        # Skip dead enemies already at 0 HP in cache
        try:
            est = _get_enemy_hp_state(enemy)
            if float(est.get("health", 1.0)) <= 0.0001:
                continue
        except Exception:
            pass
        try:
            el = enemy.get_actor_location()
        except Exception:
            continue
        dist = _dist(pl, el)
        st = _skeleton_ai_state(enemy)
        # Pending attack damage apply
        if st.get("attack_hit_due", 0.0) and now >= float(st["attack_hit_due"]):
            st["attack_hit_due"] = 0.0
            if dist <= float(SKELETON_ATTACK_RANGE) * 1.35 and (not _PLAYER_HP_CACHE.get("dead")):
                try:
                    _damage_player(world, pawn, SKELETON_ATTACK_DAMAGE)
                except Exception as e:
                    _log("T368 dmg " + str(e))
        # Lose aggro if too far
        if dist > float(SKELETON_LOSE_RANGE):
            if st["state"] != "idle" or st.get("aggro"):
                st["state"] = "idle"
                st["aggro"] = False
                st["attack_hit_due"] = 0.0
                if st.get("anim") != "idle":
                    _skeleton_play_anim(enemy, "idle", True)
            continue
        want_aggro = False
        if not _PLAYER_HP_CACHE.get("dead"):
            if st.get("aggro"):
                # Stay aggro while in lose-range IF still have LOS; lose if wall interposed for a bit
                if _has_line_of_sight(world, enemy, pawn):
                    want_aggro = True
                else:
                    # Lost sight — drop aggro (hide behind wall)
                    want_aggro = False
            else:
                want_aggro = _skeleton_can_aggro(world, enemy, pawn, dist)
        st["aggro"] = bool(want_aggro)
        if not want_aggro:
            if st["state"] != "idle":
                st["state"] = "idle"
                st["attack_hit_due"] = 0.0
            if st.get("anim") != "idle":
                _skeleton_play_anim(enemy, "idle", True)
            continue
        # Aggroed
        if dist <= float(SKELETON_ATTACK_RANGE):
            # Attack if cooldown ready
            if (now - float(st.get("last_attack_t", 0.0))) >= float(SKELETON_ATTACK_COOLDOWN):
                st["state"] = "attack"
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + float(SKELETON_ATTACK_HIT_DELAY)
                _look_at_xy(enemy, pl)
                _skeleton_play_anim(enemy, "attack", False)
            else:
                # Hold in place facing player; keep last attack anim or idle stance
                st["state"] = "attack" if st.get("anim") == "attack" else "chase"
                _look_at_xy(enemy, pl)
                # After attack anim finishes, show idle/run briefly — if not mid-attack window, play idle-ish
                if st.get("anim") == "attack" and (now - float(st.get("last_attack_t", 0.0))) > 0.9:
                    if st.get("anim") != "idle":
                        _skeleton_play_anim(enemy, "idle", True)
        else:
            st["state"] = "chase"
            _move_actor_toward(enemy, pl, SKELETON_CHASE_SPEED, dt)
            if st.get("anim") != "run":
                _skeleton_play_anim(enemy, "run", True)


def _purge_dead_skeleton_ai_keys(world):
    live = set()
    for a in _list_live_enemy_actors(world):
        try:
            live.add(_enemy_cache_key(a))
        except Exception:
            pass
    dead = [k for k in list(_SKELETON_AI.keys()) if k not in live]
    for k in dead:
        _SKELETON_AI.pop(k, None)

# ===== END T368_SKELETON_AI =====
