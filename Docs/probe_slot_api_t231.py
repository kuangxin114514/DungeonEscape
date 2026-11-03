# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_slot_api_t231.txt"
lines=[]
def L(m): lines.append(str(m))
def flush(): open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

def main():
    # AnimInstance methods related to slot/montage
    ai = unreal.AnimInstance
    meths = [x for x in dir(ai) if ("slot" in x.lower() or "montage" in x.lower() or "play" in x.lower())]
    L("AnimInstance relevant: %s" % meths)
    for m in meths:
        try:
            L("  %s doc=%s" % (m, getattr(ai, m).__doc__))
        except Exception as e:
            L("  %s ERR %s" % (m, e))

    # SkeletalMeshComponent
    smc = unreal.SkeletalMeshComponent
    meths2 = [x for x in dir(smc) if ("slot" in x.lower() or "montage" in x.lower() or "anim" in x.lower())]
    L("SMC relevant sample: %s" % meths2[:50])

    # AnimationLibrary / create montage
    for name in ("AnimationLibrary", "AnimSequenceFactory", "AnimMontageFactory", "AssetToolsHelpers"):
        try:
            L("unreal.%s=%s" % (name, getattr(unreal, name)))
        except Exception as e:
            L("unreal.%s ERR %s" % (name, e))

    # Try find/create montage
    chop = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig")
    L("chop=%s skel=%s" % (chop, chop.get_editor_property("skeleton") if chop else None))
    existing = unreal.load_asset("/Game/Characters/Player/KayKit/Animations/AM_KayKit_1H_Chop")
    L("existing AM=%s" % existing)
    if existing:
        for p in ("slot_name", "SlotName", "composite_sections", "slot_anim_tracks", "sequence_length"):
            try:
                L("  AM.%s=%s" % (p, existing.get_editor_property(p)))
            except Exception as e:
                L("  AM.%s ERR %s" % (p, e))

    # AssetTools create AnimMontage
    try:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.AnimMontageFactory()
        L("factory=%s" % factory)
        for p in ("target_skeleton", "TargetSkeleton", "source_animation", "SourceAnimation"):
            try:
                L(" factory has %s" % p)
            except Exception:
                pass
        # set skeleton
        sk = chop.get_editor_property("skeleton") if chop else None
        for p in ("target_skeleton", "TargetSkeleton"):
            try:
                factory.set_editor_property(p, sk)
                L("set factory.%s OK" % p)
            except Exception as e:
                L("set factory.%s ERR %s" % (p, e))
        for p in ("source_animation", "SourceAnimation"):
            try:
                factory.set_editor_property(p, chop)
                L("set factory.%s OK" % p)
            except Exception as e:
                L("set factory.%s ERR %s" % (p, e))
        # Does AM already exist? if so skip create
        path = "/Game/Characters/Player/KayKit/Animations"
        name = "AM_KayKit_1H_Chop_Slot"
        # delete old test if any
        full = path + "/" + name
        try:
            if unreal.EditorAssetLibrary.does_asset_exist(full):
                L("exists %s" % full)
            else:
                asset = at.create_asset(name, path, unreal.AnimMontage, factory)
                L("created %s" % asset)
                if asset:
                    unreal.EditorAssetLibrary.save_asset(full)
        except Exception as e:
            L("create AM ERR %s" % e)
    except Exception as e:
        L("AssetTools ERR %s" % e)

    # Check new montage
    am2 = unreal.load_asset("/Game/Characters/Player/KayKit/Animations/AM_KayKit_1H_Chop_Slot")
    L("AM2=%s" % am2)
    if am2:
        for p in dir(am2):
            if p.startswith("_"): continue
        for p in ("slot_name","SlotName","sequence_length","composite_sections","slot_anim_tracks",
                  "blend_in","blend_out"):
            try:
                L("  AM2.%s=%s" % (p, am2.get_editor_property(p)))
            except Exception as e:
                L("  AM2.%s ERR %s" % (p, e))

    flush(); print("WROTE", OUT)
main()
