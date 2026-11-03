# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

# Inspect original BS samples in detail
bs = unreal.EditorAssetLibrary.load_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D")
samples = bs.get_editor_property("sample_data")
unreal.log("nsamples={}".format(len(samples)))
for i,s in enumerate(samples):
    try:
        anim = s.get_editor_property("animation")
    except Exception:
        anim = None
    try:
        val = s.get_editor_property("sample_value")
    except Exception:
        val = None
    unreal.log("sample[{}] anim={} val={}".format(i, anim, val))
    # list props via dir on struct - may not work
    try:
        unreal.log("sample fields anim={} rate={}".format(s.animation if hasattr(s,"animation") else "?", getattr(s,"sample_value",None)))
    except Exception as e:
        unreal.log("sample attr err {}".format(e))

params = bs.get_editor_property("blend_parameters")
unreal.log("nparams={}".format(len(params)))
for i,p in enumerate(params):
    for pn in ["display_name","min","max","grid_num"]:
        try:
            unreal.log("param[{}].{}={}".format(i, pn, p.get_editor_property(pn)))
        except Exception as e:
            unreal.log("param[{}].{} ERR {}".format(i, pn, e))

# Duplicate BS
dest_dir = "/Game/Characters/Player/KayKit/Animations"
bs_dest = dest_dir + "/BS_KayKitLocomotion"
if unreal.EditorAssetLibrary.does_asset_exist(bs_dest):
    unreal.EditorAssetLibrary.delete_asset(bs_dest)
ok = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D", dest_dir, "BS_KayKitLocomotion")
unreal.log("dup bs -> {}".format(ok))
bs2 = unreal.EditorAssetLibrary.load_asset(bs_dest)
if bs2:
    try:
        bs2.set_editor_property("skeleton", skel)
        unreal.log("bs2 skeleton set")
    except Exception as e:
        unreal.log("bs2 skeleton ERR {}".format(e))
    # rebuild samples
    new_samples = []
    for anim, x in [(idle, 0.0), (walk, 250.0), (run, 500.0)]:
        s = unreal.BlendSample()
        s.set_editor_property("animation", anim)
        s.set_editor_property("sample_value", unreal.Vector(x, 0.0, 0.0))
        try:
            s.set_editor_property("rate_scale", 1.0)
        except Exception:
            pass
        new_samples.append(s)
    try:
        bs2.set_editor_property("sample_data", new_samples)
        unreal.log("bs2 samples set n={}".format(len(new_samples)))
    except Exception as e:
        unreal.log("bs2 samples ERR {}".format(e))
    # update axis 0 to Speed 0-600 matching max walk
    try:
        params = bs2.get_editor_property("blend_parameters")
        p0 = params[0]
        p0.set_editor_property("display_name", "Speed")
        p0.set_editor_property("min", 0.0)
        p0.set_editor_property("max", 600.0)
        p0.set_editor_property("grid_num", 4)
        params[0] = p0
        bs2.set_editor_property("blend_parameters", params)
        unreal.log("bs2 axis set")
    except Exception as e:
        unreal.log("bs2 axis ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(bs_dest)
    # verify
    bs2 = unreal.EditorAssetLibrary.load_asset(bs_dest)
    unreal.log("verify skel={}".format(bs2.get_editor_property("skeleton")))
    for i,s in enumerate(bs2.get_editor_property("sample_data")):
        unreal.log("verify sample[{}]={}".format(i, s.get_editor_property("animation")))

# Duplicate AnimBP
abp_dest = dest_dir + "/ABP_KayKitKnight"
if unreal.EditorAssetLibrary.does_asset_exist(abp_dest):
    unreal.EditorAssetLibrary.delete_asset(abp_dest)
# delete probe too later
ok = unreal.EditorAssetLibrary.duplicate_asset("/Game/Mannequin/Animations/ThirdPerson_AnimBP", dest_dir, "ABP_KayKitKnight")
unreal.log("dup abp -> {}".format(ok))
abp = unreal.EditorAssetLibrary.load_asset(abp_dest)
if abp:
    try:
        abp.set_editor_property("target_skeleton", skel)
        unreal.log("abp skeleton set")
    except Exception as e:
        unreal.log("abp skeleton ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(abp_dest)

unreal.log("PROBE9_DONE")