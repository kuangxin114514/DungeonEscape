# -*- coding: utf-8 -*-
import unreal
import os

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
folder = "/Game/Characters/Player/KayKit/Animations"
bs_path = folder + "/BS_KayKitLocomotion"
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
unreal.log("bs={}".format(bs))

# 1) Replace sample animations in place
samples = bs.get_editor_property("sample_data")
unreal.log("nsamples={}".format(len(samples)))
anims = [idle, walk, run]
values = [unreal.Vector(0,0,0), unreal.Vector(93.75,0,0), unreal.Vector(375,0,0)]
new_list = []
for i in range(3):
    s = unreal.BlendSample()
    try:
        s.set_editor_property("animation", anims[i])
        s.set_editor_property("sample_value", values[i])
        unreal.log("sample{} set via props".format(i))
    except Exception as e:
        unreal.log("sample{} prop ERR {}".format(i, e))
        # try attributes
        try:
            s.animation = anims[i]
            s.sample_value = values[i]
            unreal.log("sample{} set via attrs".format(i))
        except Exception as e2:
            unreal.log("sample{} attr ERR {}".format(i, e2))
    new_list.append(s)

try:
    bs.set_editor_property("sample_data", new_list)
    unreal.log("set sample_data OK")
except Exception as e:
    unreal.log("set sample_data ERR {}".format(e))

# verify
samples2 = bs.get_editor_property("sample_data")
for i, s in enumerate(samples2):
    try:
        a = s.get_editor_property("animation")
        v = s.get_editor_property("sample_value")
        unreal.log("verify[{}] anim={} val={}".format(i, a.get_name() if a else None, v))
    except Exception as e:
        unreal.log("verify[{}] ERR {}".format(i, e))

# 2) Same-length skeleton path: duplicate KayKit skeleton
# Mannequin: /Game/Mannequin/Character/Mesh/UE4_Mannequin_Skeleton  (49 chars)
# Target:    /Game/Mannequin/Character/Mesh/KayKitKnightSkeleton     (49 chars)
src_skel = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
alias = "/Game/Mannequin/Character/Mesh/KayKitKnightSkeleton"
m_path = "/Game/Mannequin/Character/Mesh/UE4_Mannequin_Skeleton"
unreal.log("len mannequin={} alias={}".format(len(m_path), len(alias)))
if not unreal.EditorAssetLibrary.does_asset_exist(alias):
    dupsk = unreal.EditorAssetLibrary.duplicate_asset(src_skel, alias)
    unreal.log("dup skel={}".format(dupsk))
else:
    dupsk = unreal.EditorAssetLibrary.load_asset(alias)
    unreal.log("alias exists {}".format(dupsk))

# Save BS before binary patch
unreal.EditorAssetLibrary.save_asset(bs_path)

# Also try setting skeleton if we unload - won't work via API
unreal.log("STEP1_DONE")