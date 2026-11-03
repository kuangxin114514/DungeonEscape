# -*- coding: utf-8 -*-
import unreal
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_verify_no_plume.log"
open(LOG, "w", encoding="utf-8").write("begin\n")
def flog(m):
    print(m)
    open(LOG, "a", encoding="utf-8").write(str(m) + "\n")
sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
flog("sk=%s" % sk)
try:
    res = sk.get_imported_resource()
    lod = res.lod_models[0]
    flog("sections=%d" % len(lod.sections))
    n = 0
    for s in lod.sections:
        n += s.num_vertices
        flog("sec mat=%s verts=%s" % (s.material_index, s.num_vertices))
    flog("total_section_verts=%d" % n)
except Exception as e:
    flog("lod err " + str(e))
try:
    mats = sk.get_editor_property("materials")
    flog("mat_slots=%d" % len(mats))
    for i, m in enumerate(mats):
        flog("slot%d=%s" % (i, m.get_editor_property("material_interface")))
except Exception as e:
    flog("mats " + str(e))
flog("DONE")
print("VERIFY_NO_PLUME_DONE")