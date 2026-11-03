# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_lights_t432.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
n=0
fire=unreal.Color(255, 140, 40, 255)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.PointLight):
        continue
    try:
        comp=a.light_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        try:
            comp.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
        except Exception:
            pass
        comp.set_editor_property("intensity", 800.0)
        comp.set_editor_property("light_color", fire)
        try:
            comp.set_editor_property("use_temperature", False)
        except Exception:
            pass
        try:
            comp.set_editor_property("attenuation_radius", 1200.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("source_radius", 8.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("soft_source_radius", 4.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("indirect_lighting_intensity", 0.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("volumetric_scattering_intensity", 0.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("cast_shadows", True)
        except Exception:
            pass
        name=a.get_actor_label() if hasattr(a,"get_actor_label") else a.get_name()
        L("ok %s inten=800 atten=1200 color=255,140,40"%name)
        n+=1
    except Exception as e:
        L("ERR "+str(a.get_name())+" "+str(e))
try:
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNoPrecomputedLighting=True")
except Exception as e:
    L("ws ERR "+str(e))
try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))
L("fixed=%d"%n)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
