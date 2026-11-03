# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\brighten_t436.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
try:
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNo=True")
except Exception as e:
    L("ws ERR "+str(e))

fire=unreal.Color(255, 160, 60, 255)
n=0
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
        # bright but not blown: ~2500 cd torch-ish for dungeon
        comp.set_editor_property("intensity", 2500.0)
        comp.set_editor_property("light_color", fire)
        try:
            comp.set_editor_property("use_temperature", False)
        except Exception:
            pass
        try:
            comp.set_editor_property("attenuation_radius", 2500.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("indirect_lighting_intensity", 0.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("cast_shadows", True)
        except Exception:
            pass
        try:
            comp.set_visibility(True)
        except Exception:
            pass
        L("bright %s inten=2500 atten=2500"%a.get_name())
        n+=1
    except Exception as e:
        L("ERR "+str(e))

# soft fill so whole map is not pitch black between torches
try:
    has_fill=False
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            if a.get_actor_label()=="Dungeon_FillLight":
                has_fill=True
                fill=a
                break
        except Exception:
            pass
    if not has_fill:
        fill=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(0.0,0.0,400.0), unreal.Rotator(0,0,0))
        fill.set_actor_label("Dungeon_FillLight")
        L("spawned Dungeon_FillLight")
    else:
        L("reuse Dungeon_FillLight")
    fc=fill.light_component
    fc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    try:
        fc.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
    except Exception:
        pass
    fc.set_editor_property("intensity", 1200.0)
    fc.set_editor_property("light_color", unreal.Color(255, 200, 150, 255))
    try:
        fc.set_editor_property("attenuation_radius", 8000.0)
    except Exception:
        pass
    try:
        fc.set_editor_property("cast_shadows", False)
    except Exception:
        pass
    try:
        fc.set_editor_property("indirect_lighting_intensity", 0.0)
    except Exception:
        pass
except Exception as e:
    L("fill ERR "+str(e))

try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))
L("fixed=%d"%n)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
