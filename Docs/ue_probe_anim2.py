# -*- coding: utf-8 -*-
import unreal

# AnimGraphLibrary methods
agl = unreal.AnimGraphLibrary
methods = [m for m in dir(agl) if not m.startswith("_")]
unreal.log("AnimGraphLibrary methods: " + ",".join(methods))

# AnimationLibrary
al = unreal.AnimationLibrary
methods2 = [m for m in dir(al) if not m.startswith("_")]
unreal.log("AnimationLibrary methods: " + ",".join(methods2[:80]))

# How to get BP mesh / generated class
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.log("bp class="+bp.get_class().get_name())
for attr in ["generated_class","GeneratedClass","parent_class","skeleton","simple_construction_script","UberGraphFunction"]:
    unreal.log("bp has {} = {}".format(attr, hasattr(bp, attr)))
try:
    gc = bp.get_editor_property("generated_class")
    unreal.log("generated_class prop={}".format(gc))
except Exception as e:
    unreal.log("gen prop err "+str(e))

# try load_blueprint_class
try:
    cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/Characters/Player/KayKit/BP_KayKitKnight")
    unreal.log("load_blueprint_class="+str(cls))
    cdo = unreal.get_default_object(cls)
    unreal.log("cdo="+str(cdo))
    mesh = cdo.get_editor_property("mesh")
    unreal.log("mesh="+str(mesh))
    unreal.log("anim_mode="+str(mesh.get_editor_property("animation_mode")))
    try:
        unreal.log("anim_class="+str(mesh.get_editor_property("anim_class")))
    except Exception as e:
        unreal.log("anim_class err "+str(e))
    try:
        ad = mesh.get_editor_property("animation_data")
        unreal.log("animation_data="+str(ad))
        unreal.log("anim_to_play="+str(ad.anim_to_play if hasattr(ad,"anim_to_play") else ad.get_editor_property("anim_to_play")))
    except Exception as e:
        unreal.log("animdata err "+str(e))
except Exception as e:
    unreal.log("lbc err "+str(e))

# Blend space sample API
bsf = unreal.BlendSpaceFactory1D
unreal.log("BS factory props try")
unreal.log("PROBE2_DONE")