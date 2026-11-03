# -*- coding: utf-8 -*-
import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
  for i in range(12):
    time.sleep(0.5); nodes=remote.remote_nodes
    if nodes:
      remote.open_command_connection(nodes[0]["node_id"]); print("node", nodes[0]["node_id"]); break
  stmt="exec(compile(open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/ue_assign_knight_mats.py',encoding='utf-8').read(),'ue_assign_knight_mats.py','exec'))"
  print(remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT))
  stmt2=r'''
import unreal, os
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_verify_no_plume.log"
open(LOG,"w",encoding="utf-8").write("begin\n")
def flog(m):
    print(m)
    open(LOG,"a",encoding="utf-8").write(str(m)+"\n")
sk=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
flog("sk=%s"%sk)
try:
    lod=sk.get_imported_resource().lod_models[0]
    flog("sections=%d"%len(lod.sections))
    n=0
    for s in lod.sections:
        n+=s.num_vertices
        flog("sec mat=%s verts=%s"% (s.material_index, s.num_vertices))
    flog("total_section_verts=%d"%n)
except Exception as e:
    flog("lod err "+str(e))
try:
    mats=sk.get_editor_property("materials")
    flog("mat_slots=%d"%len(mats))
    for i,m in enumerate(mats[:8]):
        flog("slot%d=%s"%(i, m.get_editor_property("material_interface")))
except Exception as e:
    flog("mats "+str(e))
flog("DONE")
'''
  print(remote.run_command(stmt2, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT))
finally:
  remote.stop()
