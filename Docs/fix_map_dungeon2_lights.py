# -*- coding: utf-8 -*-
"""Fix Map_Dungeon2 lighting: ensure Movable Directional + SkyLight so viewport is lit without bake."""
from __future__ import print_function
import traceback
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_map_dungeon2_lights.txt"
DUNGEON2 = "/Game/Maps/Dungeon/Map_Dungeon2"
_lines = []


def log(msg):
    s = str(msg)
    _lines.append(s)
    try:
        unreal.log("FixD2Lights: " + s)
    except Exception:
        print("FixD2Lights:", s)


def flush():
    try:
        open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")
    except Exception:
        pass


def spawn(cls, loc, rot=None):
    if rot is None:
        rot = unreal.Rotator(0.0, 0.0, 0.0)
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        return sub.spawn_actor_from_class(cls, loc, rot)
    except Exception:
        return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)


def actors_by_label():
    out = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            out[a.get_actor_label() or ""] = a
        except Exception:
            pass
    return out


def light_comp(actor):
    for name in (
        "directional_light_component",
        "sky_light_component",
        "point_light_component",
        "spot_light_component",
        "light_component",
        "root_component",
    ):
        try:
            c = getattr(actor, name, None)
            if c:
                return c
        except Exception:
            pass
    try:
        return actor.get_component_by_class(unreal.LightComponentBase.static_class())
    except Exception:
        return None


def set_movable(actor, intensity=None, extra=None):
    c = light_comp(actor)
    if not c:
        log("no light comp for " + str(actor.get_actor_label()))
        return
    for prop, val in (
        ("mobility", unreal.ComponentMobility.MOVABLE),
        ("Mobility", unreal.ComponentMobility.MOVABLE),
    ):
        try:
            c.set_editor_property(prop, val)
            log("set %s mobility MOVABLE" % (actor.get_actor_label() or "?"))
            break
        except Exception as e:
            log("mobility %s fail %s" % (prop, e))
    if intensity is not None:
        for prop in ("intensity", "Intensity"):
            try:
                c.set_editor_property(prop, float(intensity))
                log("set %s intensity=%s" % (actor.get_actor_label() or "?", intensity))
                break
            except Exception as e:
                log("intensity %s fail %s" % (prop, e))
    if extra:
        for prop, val in extra.items():
            try:
                c.set_editor_property(prop, val)
                log("set %s %s=%s" % (actor.get_actor_label() or "?", prop, val))
            except Exception as e:
                log("extra %s fail %s" % (prop, e))


def ensure_label(cls, label, loc, rot=None):
    by = actors_by_label()
    if label in by:
        log("keep " + label)
        return by[label]
    # also reuse any actor of same class if unlabeled duplicate exists? no, spawn clean
    a = spawn(cls, loc, rot)
    if a:
        try:
            a.set_actor_label(label)
        except Exception:
            pass
        log("spawn " + label)
    else:
        log("FAIL spawn " + label)
    return a


def find_by_class_substr(substr):
    found = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            cn = a.get_class().get_name()
        except Exception:
            cn = ""
        if substr in cn:
            found.append(a)
    return found


def main():
    log("BEGIN fix Map_Dungeon2 lights")
    try:
        w = unreal.EditorLevelLibrary.get_editor_world()
        prev = w.get_path_name() if w else None
        log("prev_world=" + str(prev))
    except Exception as e:
        prev = None
        log("prev fail " + str(e))

    if not unreal.EditorAssetLibrary.does_asset_exist(DUNGEON2):
        log("FAIL Map_Dungeon2 missing")
        flush()
        return

    unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON2)
    log("loaded Map_Dungeon2")

    # inventory
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cn = a.get_class().get_name()
        if "Light" in cn or "Atmosphere" in cn or "Fog" in cn:
            log("have %s label=%s" % (cn, a.get_actor_label()))

    sun = None
    dirs = find_by_class_substr("DirectionalLight")
    if dirs:
        sun = dirs[0]
        try:
            sun.set_actor_label("Dungeon2_Sun")
        except Exception:
            pass
        log("reuse DirectionalLight count=%d" % len(dirs))
    else:
        sun = ensure_label(
            unreal.DirectionalLight,
            "Dungeon2_Sun",
            unreal.Vector(0.0, 0.0, 800.0),
            unreal.Rotator(-50.0, -35.0, 0.0),
        )
    if sun:
        set_movable(sun, intensity=8.0)
        try:
            sun.set_actor_rotation(unreal.Rotator(-50.0, -35.0, 0.0), False)
        except Exception:
            pass

    sky = None
    skys = find_by_class_substr("SkyLight")
    if skys:
        sky = skys[0]
        try:
            sky.set_actor_label("Dungeon2_SkyLight")
        except Exception:
            pass
        log("reuse SkyLight count=%d" % len(skys))
    else:
        sky = ensure_label(unreal.SkyLight, "Dungeon2_SkyLight", unreal.Vector(0.0, 0.0, 600.0))
    if sky:
        set_movable(
            sky,
            intensity=1.5,
            extra={
                "real_time_capture": True,
                "RealTimeCapture": True,
                "source_type": unreal.SkyLightSourceType.SLS_CAPTURED_SCENE,
                "SourceType": unreal.SkyLightSourceType.SLS_CAPTURED_SCENE,
            },
        )
        # force recapture
        c = light_comp(sky)
        if c:
            for meth in ("recapture_sky", "RecaptureSky"):
                try:
                    getattr(c, meth)()
                    log("recapture_sky ok")
                    break
                except Exception as e:
                    log("recapture %s fail %s" % (meth, e))

    try:
        atms = find_by_class_substr("SkyAtmosphere")
        if not atms:
            ensure_label(unreal.SkyAtmosphere, "Dungeon2_SkyAtmosphere", unreal.Vector(0.0, 0.0, 0.0))
        else:
            log("keep SkyAtmosphere")
    except Exception as e:
        log("SkyAtmosphere skip " + str(e))

    # Fix any PointLights: Movable + brighter so no bake needed
    for pl in find_by_class_substr("PointLight"):
        lab = pl.get_actor_label() or "PointLight"
        log("fix PointLight " + lab)
        set_movable(
            pl,
            intensity=8000.0,
            extra={
                "attenuation_radius": 2500.0,
                "AttenuationRadius": 2500.0,
                "cast_shadows": True,
                "CastShadows": True,
            },
        )

    unreal.EditorLevelLibrary.save_current_level()
    try:
        unreal.EditorAssetLibrary.save_asset(DUNGEON2)
        log("saved Map_Dungeon2")
    except Exception as e:
        log("save asset " + str(e))

    # final inventory
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        cn = a.get_class().get_name()
        if "Light" in cn or "Atmosphere" in cn:
            log("final %s label=%s" % (cn, a.get_actor_label()))

    log("DONE stay on Map_Dungeon2")
    flush()
    print("WROTE", OUT)


try:
    main()
except Exception as e:
    log("FATAL " + str(e))
    log(traceback.format_exc())
    flush()
