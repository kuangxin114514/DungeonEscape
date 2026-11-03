import unreal

SK="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
MAT="/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"
TEX="/Game/Characters/Player/KayKit/Textures/T_KayKitKnight"
BP="/Game/Characters/Player/KayKit/BP_KayKitKnight"
IDLE="/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig"
GM_HUB="/Game/Core/GameFlow/GM_Hub"
TP_GM="/Game/ThirdPersonBP/Blueprints/ThirdPersonGameMode"

def log(m): unreal.log("FIX2: "+str(m))
def warn(m): unreal.log_warning("FIX2: "+str(m))
def save(a):
    try: unreal.EditorAssetLibrary.save_loaded_asset(a)
    except Exception as e: warn("save "+str(e))

sk=unreal.EditorAssetLibrary.load_asset(SK)
mat=unreal.EditorAssetLibrary.load_asset(MAT)
tex=unreal.EditorAssetLibrary.load_asset(TEX)
idle=unreal.EditorAssetLibrary.load_asset(IDLE)

# rebuild material with texture
if mat and tex:
    try:
        unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
        ts=unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -400, 0)
        ts.set_editor_property("texture", tex)
        unreal.MaterialEditingLibrary.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        save(mat)
        log("mat_rebuilt")
    except Exception as e:
        warn("mat "+str(e))

# assign material to every skeletal slot (replace list)
if sk and mat:
    try:
        old=list(sk.get_editor_property("materials"))
        log("old_slots=%d"%len(old))
        new_list=[]
        for i, slot in enumerate(old if old else [None]):
            sm=unreal.SkeletalMaterial()
            sm.set_editor_property("material_interface", mat)
            # keep slot name if any
            try:
                if slot is not None:
                    sn=slot.get_editor_property("material_slot_name")
                    if sn: sm.set_editor_property("material_slot_name", sn)
            except Exception:
                pass
            new_list.append(sm)
        if not new_list:
            sm=unreal.SkeletalMaterial()
            sm.set_editor_property("material_interface", mat)
            new_list=[sm]
        sk.set_editor_property("materials", new_list)
        save(sk)
        # verify
        for i,s in enumerate(list(sk.materials)):
            log("slot%d=%s"%(i, s.material_interface))
    except Exception as e:
        warn("slots "+str(e))
        # fallback set_material
        for i in range(8):
            try: sk.set_material(i, mat)
            except Exception: break
        save(sk)

# BP mesh transform + single node idle
bp=unreal.EditorAssetLibrary.load_asset(BP)
cls=None
try: cls=unreal.load_class(None, BP+".BP_KayKitKnight_C")
except Exception: pass
if not cls:
    try: cls=unreal.load_object(None, BP+".BP_KayKitKnight_C")
    except Exception as e: warn("load_object "+str(e))
if cls:
    cdo=unreal.get_default_object(cls)
    mesh=cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    # named kwargs avoid axis mixups
    mesh.set_editor_property("relative_rotation", unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0))
    mesh.set_editor_property("relative_scale3d", unreal.Vector(0.75, 0.75, 0.75))
    mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -90.0))
    if idle:
        try: mesh.set_animation(idle); log("idle_set")
        except Exception as e: warn("idle "+str(e))
    try:
        cap=cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", 90.0)
        cap.set_editor_property("capsule_radius", 34.0)
    except Exception as e: warn("cap "+str(e))
    save(bp)
    # re-read
    rot=mesh.get_editor_property("relative_rotation")
    log("rot pitch=%s yaw=%s roll=%s"%(rot.pitch, rot.yaw, rot.roll))
else:
    warn("no bp class")

# default pawn via load_class
pawn_cls=None
try: pawn_cls=unreal.load_class(None, BP+".BP_KayKitKnight_C")
except Exception: pass
for gpath in (GM_HUB, TP_GM):
    name=gpath.rsplit("/",1)[-1]
    gcls=None
    try: gcls=unreal.load_class(None, gpath+"."+name+"_C")
    except Exception: pass
    if gcls and pawn_cls:
        cdo=unreal.get_default_object(gcls)
        try:
            cdo.set_editor_property("default_pawn_class", pawn_cls)
            save(unreal.EditorAssetLibrary.load_asset(gpath))
            log("pawn_on "+gpath+" -> "+str(cdo.get_editor_property("default_pawn_class")))
        except Exception as e:
            warn("pawn "+gpath+" "+str(e))
    else:
        warn("skip gm %s gcls=%s pawn=%s"%(gpath,gcls,pawn_cls))

log("DONE")