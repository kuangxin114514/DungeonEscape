# -*- coding: utf-8 -*-
import unreal
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_verify_cape_plume.log"
open(LOG,"w",encoding="utf-8").write("begin\n")
def flog(m):
    print(m)
    open(LOG,"a",encoding="utf-8").write(str(m)+"\n")

mat = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Materials/M_KayKitKnight")
sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
flog("mat=%s sk=%s" % (mat, sk))

# Try multiple material assignment paths for SK
applied = 0
if sk and mat:
    # 1) set_material
    for i in range(16):
        try:
            sk.set_material(i, mat); applied += 1
        except Exception as e:
            flog("set_material[%d] %s" % (i, e)); break
    flog("set_material applied=%d" % applied)
    # 2) materials / soft materials arrays via EditorProperty
    for prop in ("materials", "materials", "sections"):
        try:
            val = sk.get_editor_property(prop)
            flog("prop %s type=%s len=%s" % (prop, type(val), (len(val) if hasattr(val,'__len__') else '?')))
        except Exception as e:
            flog("prop %s err %s" % (prop, e))
    try:
        mats = sk.materials
        flog("sk.materials len=%s" % (len(mats) if mats is not None else None))
        if mats is not None:
            for i, slot in enumerate(list(mats)):
                try:
                    flog(" slot%d = %s" % (i, slot))
                except Exception as e:
                    flog(" slot%d err %s" % (i, e))
    except Exception as e:
        flog("sk.materials access %s" % e)
    # 3) LodMaterials via AssetImportData / MeshDescription not available; use EditorAssetLibrary
    try:
        # UE4 SkeletalMesh: Materials is TArray<FSkeletalMaterial>
        skel_mats = sk.get_editor_property("materials")
        new_slots = []
        for i, smat in enumerate(skel_mats):
            try:
                # FSkeletalMaterial has material_interface
                smat.set_editor_property("material_interface", mat)
                new_slots.append(smat)
                flog("patched skeletal material slot %d" % i)
            except Exception as e:
                flog("patch slot %d %s" % (i, e))
                new_slots.append(smat)
        if new_slots:
            sk.set_editor_property("materials", new_slots)
            flog("wrote materials array n=%d" % len(new_slots))
    except Exception as e:
        flog("materials array path %s" % e)

unreal.EditorAssetLibrary.save_loaded_asset(sk, False)

# BP CDO materials + component static meshes
cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(cls)
mesh = cdo.get_editor_property("mesh")
mesh.set_editor_property("skeletal_mesh", sk)
for i in range(16):
    try: mesh.set_material(i, mat)
    except Exception: break
flog("bp mesh materials painted")
try:
    comps = cdo.get_components_by_class(unreal.StaticMeshComponent)
    for comp in comps:
        sm = None
        try: sm = comp.get_editor_property("static_mesh")
        except Exception: pass
        name = str(sm.get_name()) if sm else ""
        flog("SMC %s" % name)
        if sm and mat:
            for i in range(8):
                try: comp.set_material(i, mat)
                except Exception: break
except Exception as e:
    flog("smc %s" % e)

unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
unreal.EditorAssetLibrary.save_loaded_asset(sk, False)

# Bounds / name dump to confirm cape gone (can't easily list section names in py)
try:
    bounds = sk.get_bounds()
    flog("sk bounds box=%s sphere=%s" % (bounds.box_extent, bounds.sphere_radius))
except Exception as e:
    flog("bounds %s" % e)
try:
    # imported mesh names sometimes in asset import data
    aid = sk.get_editor_property("asset_import_data")
    flog("import_data=%s" % aid)
    if aid:
        try:
            flog("source=%s" % aid.get_first_filename())
        except Exception as e:
            flog("src err %s" % e)
except Exception as e:
    flog("aid %s" % e)

try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.open_editor_for_assets([bp])
except Exception as e:
    flog("reopen %s" % e)

flog("VERIFY_DONE")