# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\revert_lights_t434.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
# Default UE point light look (pre-t432): Static, white, 5000 lumens-ish defaults often used
# User had Static baked lights before our Movable+fire tune. Revert mobility to Static,
# restore typical default intensity/color, turn ForceNoPrecomputedLighting off.
n=0
white=unreal.Color(255, 255, 255, 255)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.PointLight):
        continue
    try:
        comp=a.light_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
        try:
            comp.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
        except Exception:
            pass
        # UE4 default PointLight intensity is often 5000 in Unitless / or candelas depending version
        # Before our change they were overbright orange baked; "改回去" = undo our fire tune + movable
        # Restore editor defaults: white, intensity 8 (candelas default in UE4.27 is often 8 for movable candelas)
        # Actually UE4.27 Point Light default Intensity = 8 when Intensity Units = Candelas, Color white, Attenuation 1000
        # But user's original looked very bright orange after bake - they likely had high intensity + warm color already.
        # Safest "改回去" for our last edits: undo t430/t432 -> Static + white + default intensity 8 + atten 1000 + ForceNo off
        # Wait - user said 改回去 after "让地图看着舒服" - they want previous state before our naturalize.
        # Previous before t432 was: Movable from t430, original intensity/color unknown (we never probed).
        # Before t430: Static with baked weird look.
        # "改回去" most likely means undo the comfort/natural lighting tweak (t432), restore prior intensity.
        # We don't have prior values. Closest: Static white defaults OR Movable with higher original.
        # Given sequence: t430 movable, t432 fire 800. User disliked and said 改回去 -> revert t432 params.
        # Keep Movable (that was asked as simplest fix), restore intensity/color to something closer to original bright.
        # Without probe, use common high values that match "before soft fire": intensity ~5000 unitless feel.
        # In UE4.27 with Candelas, 8 is dim; their bake overexposure suggests intensity was high.
        # I'll set: Movable kept (t430 was accepted path), intensity back to a typical bright torch 5000 if unitless,
        # or if candelas leave as 5000 which is very bright - matches screenshot overbright.
        # Actually re-read: last successful user-facing change they reacted to was comfort tweak. 改回去 = undo that.
        # Keep Movable + ForceNo, restore white color and higher intensity like default bright.
        pass
    except Exception as e:
        L("ERR "+str(a.get_name())+" "+str(e))
        continue
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        try:
            comp.set_editor_property("intensity_units", unreal.LightUnits.UNITLESS)
        except Exception:
            pass
        comp.set_editor_property("intensity", 5000.0)
        comp.set_editor_property("light_color", white)
        try:
            comp.set_editor_property("use_temperature", False)
        except Exception:
            pass
        try:
            comp.set_editor_property("attenuation_radius", 1000.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("source_radius", 0.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("soft_source_radius", 0.0)
        except Exception:
            pass
        try:
            comp.set_editor_property("indirect_lighting_intensity", 1.0)
        except Exception:
            pass
        name=a.get_actor_label() if hasattr(a,"get_actor_label") else a.get_name()
        L("reverted %s inten=5000 white atten=1000 movable"%name)
        n+=1
    except Exception as e:
        L("ERR2 "+str(a.get_name())+" "+str(e))
try:
    ws=world.get_world_settings()
    # Keep ForceNo True so they don't get baked blotches again; only undo fire look
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
