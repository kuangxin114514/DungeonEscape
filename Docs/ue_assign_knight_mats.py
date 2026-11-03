# -*- coding: utf-8 -*-
import unreal, os
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_assign_knight_mats.log"
open(LOG,"w",encoding="utf-8").write("begin\n")
def flog(m):
    print(m)
    with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")

SK_PATH = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
MAT_PATH = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"
SWORD = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword"
SHIELD = "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"
BP_PATH = "/Game/Characters/Player/KayKit/BP_KayKitKnight"

mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
sword = unreal.EditorAssetLibrary.load_asset(SWORD)
shield = unreal.EditorAssetLibrary.load_asset(SHIELD)
flog("mat=%s sk=%s" % (mat, sk))

def save(a):
    try: unreal.EditorAssetLibrary.save_loaded_asset(a, False)
    except Exception:
        try: unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e: flog("save err "+str(e))

# Inspect SK material API
flog("sk dirs sample: " + ",".join([x for x in dir(sk) if "mat" in x.lower() or "Mat" in x][:40]))
try:
    mats = sk.get_editor_property("materials")
    flog("materials len=%s type=%s" % (len(mats) if mats is not None else None, type(mats)))
    if mats:
        flog("slot0=%s" % mats[0])
        flog("slot0 props=%s" % [p for p in dir(mats[0]) if not p.startswith("_")][:30])
except Exception as e:
    flog("get materials err "+str(e))

# Try assign via materials array
try:
    mats = list(sk.get_editor_property("materials"))
    new_mats = []
    for i, slot in enumerate(mats):
        try:
            # SkeletalMaterial
            mi = unreal.SkeletalMaterial()
            # copy slot name if present
            try:
                sn = slot.get_editor_property("material_slot_name")
                mi.set_editor_property("material_slot_name", sn)
            except Exception:
                pass
            try:
                mi.set_editor_property("imported_material_slot_name", slot.get_editor_property("imported_material_slot_name"))
            except Exception:
                pass
            mi.set_editor_property("material_interface", mat)
            new_mats.append(mi)
            flog("prepared slot %d" % i)
        except Exception as e:
            flog("prep slot %d %s" % (i, e))
            new_mats.append(slot)
    if new_mats:
        sk.set_editor_property("materials", new_mats)
        flog("set materials array len=%d" % len(new_mats))
except Exception as e:
    flog("array assign err "+str(e))

# Also try set_material on StaticMeshes again (already worked)
for a, name in ((sword,"sword"), (shield,"shield")):
    if not a: continue
    n=0
    for i in range(8):
        try:
            a.set_material(i, mat); n+=1
        except Exception:
            break
    flog("%s set_material count=%d" % (name, n))
    # also materials array
    try:
        smats = list(a.get_editor_property("static_materials"))
        flog("%s static_materials len=%d" % (name, len(smats)))
        out=[]
        for slot in smats:
            try:
                slot.set_editor_property("material_interface", mat)
                out.append(slot)
            except Exception:
                try:
                    ns = unreal.StaticMaterial()
                    ns.set_editor_property("material_interface", mat)
                    out.append(ns)
                except Exception as e2:
                    flog("sm slot "+str(e2)); out.append(slot)
        if out:
            a.set_editor_property("static_materials", out)
            flog("%s static_materials set" % name)
    except Exception as e:
        flog("%s static_materials err %s" % (name, e))
    save(a)

save(sk)

# BP CDO mesh materials
try:
    cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    for i in range(16):
        try: mesh.set_material(i, mat)
        except Exception: break
    flog("bp mesh materials done")
    # find static mesh comps without mutating SCS graph
    try:
        comps = cdo.get_components_by_class(unreal.StaticMeshComponent)
        flog("bp smc count=%d" % len(list(comps)))
        for comp in comps:
            sm = None
            try: sm = comp.get_editor_property("static_mesh")
            except Exception: pass
            nm = sm.get_name() if sm else "?"
            for i in range(8):
                try: comp.set_material(i, mat)
                except Exception: break
            flog("bp smc mat " + str(nm))
    except Exception as e:
        flog("smc "+str(e))
except Exception as e:
    flog("bp "+str(e))

bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
save(bp)
save(sk)
try:
    unreal.EditorAssetLibrary.save_directory("/Game/Characters/Player/KayKit", False, True)
except Exception as e:
    flog("save_dir "+str(e))

# reopen SK + BP for visual check
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.open_editor_for_assets([sk, bp])
    flog("opened sk+bp")
except Exception as e:
    flog("open "+str(e))

flog("DONE")
print("ASSIGN_MATS_DONE")