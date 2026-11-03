import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT=r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_verify_sk.txt"
def w(m):
  open(LOG,"a",encoding="utf-8").write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
sk=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
w("lods="+str(unreal.EditorSkeletalMeshLibrary.get_lod_count(sk)))
w("verts0="+str(unreal.EditorSkeletalMeshLibrary.get_num_verts(sk,0)))
w("sections0="+str(unreal.EditorSkeletalMeshLibrary.get_num_sections(sk,0)))
sword=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
shield=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield")
w("sword="+str(sword))
w("shield="+str(shield))
cls=unreal.load_class(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo=unreal.get_default_object(cls)
mesh=cdo.get_editor_property("mesh")
w("bp_sk="+str(mesh.get_editor_property("skeletal_mesh")))
w("bp_mode="+str(mesh.get_editor_property("animation_mode")))
w("bp_loc="+str(mesh.get_editor_property("relative_location")))
w("bp_rot="+str(mesh.get_editor_property("relative_rotation")))
w("bp_scale="+str(mesh.get_editor_property("relative_scale3d")))
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  for i in range(8):
    time.sleep(0.4)
    if remote.remote_nodes:
      remote.open_command_connection(remote.remote_nodes[0]["node_id"]); break
  print(remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE).get("success"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_verify_sk.txt",encoding="utf-8").read())
