# -*- coding: utf-8 -*-
import unreal, os
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_verify_no_helmet.log"
open(LOG,"w",encoding="utf-8").write("begin\n")
def flog(m):
    print(m)
    open(LOG,"a",encoding="utf-8").write(str(m)+"\n")

sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
mat = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Materials/M_KayKitKnight")
sword = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")

mats = list(sk.get_editor_property("materials"))
flog("sk_slots=%d" % len(mats))
for i,s in enumerate(mats):
    mi = s.get_editor_property("material_interface")
    sn = s.get_editor_property("material_slot_name")
    flog("sk_slot[%d] name=%s mat=%s" % (i, sn, mi.get_path_name() if mi else None))

for name,a in (("sword",sword),("shield",shield)):
    smats = list(a.get_editor_property("static_materials"))
    for i,s in enumerate(smats):
        mi = s.get_editor_property("material_interface")
        flog("%s_slot[%d]=%s" % (name, i, mi.get_path_name() if mi else None))

# vertex / section probe
for attr in ("get_num_vertices","get_num_lods","get_lod_num","lod_info","get_imported_bounds"):
    if hasattr(sk, attr):
        flog("has "+attr)
try:
    flog("num_lods=%s" % sk.get_num_lods())
except Exception as e:
    flog("num_lods err "+str(e))
try:
    b = sk.get_imported_bounds()
    flog("bounds box=%s sphere=%s" % (b.box_extent, b.sphere_radius))
except Exception as e:
    flog("bounds "+str(e))

# Compile BP safely
try:
    unreal.KismetEditorUtilities.compile_blueprint(bp)
    flog("compiled bp")
except Exception as e:
    flog("compile "+str(e))

# Inspect SCS node names without ctypes mutation
try:
    cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    flog("cdo skeletal=%s" % mesh.get_editor_property("skeletal_mesh").get_path_name())
    try:
        ovm = mesh.get_editor_property("override_materials")
        flog("cdo override_materials=%s" % [ (m.get_path_name() if m else None) for m in list(ovm) ])
    except Exception as e:
        flog("ovm "+str(e))
except Exception as e:
    flog("cdo "+str(e))

try:
    scs = bp.simple_construction_script
    nodes = scs.get_all_nodes()
    flog("scs nodes=%d" % len(list(nodes)))
    for n in nodes:
        try:
            flog("scs node=%s var=%s" % (n.get_class().get_name(), n.get_variable_name()))
        except Exception as e:
            flog("scs node err "+str(e))
except Exception as e:
    flog("scs "+str(e))

# Open SK asset editor focused
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.open_editor_for_assets([sk])
    flog("opened SK")
except Exception as e:
    flog("open "+str(e))

flog("DONE")
print("VERIFY_DONE")