# -*- coding: utf-8 -*-
import unreal

bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")

# Rebuild blend parameters with Speed max=600
p0 = unreal.BlendParameter()
p0.set_editor_property("display_name", "Speed")
p0.set_editor_property("min", 0.0)
p0.set_editor_property("max", 600.0)
p0.set_editor_property("grid_num", 4)

p1 = unreal.BlendParameter()
p1.set_editor_property("display_name", "")
p1.set_editor_property("min", 0.0)
p1.set_editor_property("max", 100.0)
p1.set_editor_property("grid_num", 4)

p2 = unreal.BlendParameter()
p2.set_editor_property("display_name", "")
p2.set_editor_property("min", 0.0)
p2.set_editor_property("max", 100.0)
p2.set_editor_property("grid_num", 4)

try:
    bs.set_editor_property("blend_parameters", [p0, p1, p2])
    unreal.log("set list OK")
except Exception as e:
    unreal.log("set list ERR {}".format(e))

bps = bs.get_editor_property("blend_parameters")
unreal.log("verify max={}".format(bps[0].get_editor_property("max")))

# Ensure run sample still at 600 and within range
sd = bs.get_editor_property("sample_data")
for s in sd:
    unreal.log("sample {} @ {}".format(s.get_editor_property("animation").get_name(), s.get_editor_property("sample_value")))

unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
unreal.log("BPMAX2_DONE")