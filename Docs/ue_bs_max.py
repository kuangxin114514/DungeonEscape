# -*- coding: utf-8 -*-
import unreal

bs = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
bps = bs.get_editor_property("blend_parameters")
unreal.log("n={}".format(len(bps)))
for i, p in enumerate(bps):
    try:
        unreal.log("p{} name={} min={} max={} grid={}".format(
            i,
            p.get_editor_property("display_name"),
            p.get_editor_property("min"),
            p.get_editor_property("max"),
            p.get_editor_property("grid_num")))
    except Exception as e:
        unreal.log("p{} ERR {}".format(i, e))
        # dump props
        for n in ["DisplayName", "display_name", "Min", "min", "Max", "max", "GridNum", "grid_num"]:
            try:
                unreal.log("  {}={}".format(n, p.get_editor_property(n)))
            except Exception:
                pass

# Set axis 0 max to 600
try:
    p0 = bps[0]
    p0.set_editor_property("max", 600.0)
    # write back - FixedArray may need full replace
    # try mutate in place first
    unreal.log("after mutate max={}".format(p0.get_editor_property("max")))
    bs.set_editor_property("blend_parameters", bps)
    unreal.log("set blend_parameters OK")
except Exception as e:
    unreal.log("set bp ERR {}".format(e))

bps2 = bs.get_editor_property("blend_parameters")
unreal.log("verify max={}".format(bps2[0].get_editor_property("max")))
unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
unreal.log("BPMAX_DONE")