# -*- coding: utf-8 -*-
import unreal

bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
bs = unreal.EditorAssetLibrary.load_asset(bs_path)

# Update blend parameter max to 600 to match MaxWalkSpeed
try:
    bps = bs.get_editor_property("blend_parameters")
    unreal.log("blend_parameters len={} type={}".format(len(bps) if bps is not None else None, type(bps)))
    # BlendSpace1D has one axis - may be property blend_parameter
except Exception as e:
    unreal.log("bp ERR {}".format(e))

for prop in ["blend_parameters", "BlendParameters", "axis_to_scale_animation"]:
    try:
        v = bs.get_editor_property(prop)
        unreal.log("{}={}".format(prop, v))
    except Exception as e:
        unreal.log("{} ERR".format(prop))

# Try get Axis display
try:
    # BlendSpaceBase: GetBlendParameter(index)
    p0 = bs.get_blend_parameter(0)
    unreal.log("param0 min={} max={} name={}".format(
        p0.get_editor_property("min"), p0.get_editor_property("max"), p0.get_editor_property("display_name")))
    p0.set_editor_property("max", 600.0)
    bs.set_blend_parameter(0, p0)
    unreal.log("set max 600 via set_blend_parameter")
except Exception as e:
    unreal.log("get_blend_parameter ERR {}".format(e))

# Move run sample from 375 -> 600
sd = list(bs.get_editor_property("sample_data"))
new_sd = []
for s in sd:
    anim = s.get_editor_property("animation")
    val = s.get_editor_property("sample_value")
    rate = s.get_editor_property("rate_scale")
    name = anim.get_name() if anim else ""
    if "Running" in name:
        val = unreal.Vector(600.0, 0.0, 0.0)
        unreal.log("run sample -> 600")
    # rebuild struct
    ns = unreal.BlendSample()
    ns.set_editor_property("animation", anim)
    ns.set_editor_property("sample_value", val)
    ns.set_editor_property("rate_scale", rate)
    new_sd.append(ns)
bs.set_editor_property("sample_data", new_sd)

# verify
sd2 = bs.get_editor_property("sample_data")
for s in sd2:
    unreal.log("final sample {} @ {}".format(
        s.get_editor_property("animation").get_name(),
        s.get_editor_property("sample_value")))

unreal.EditorAssetLibrary.save_asset(bs_path)
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP")
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.log("AXIS_DONE")