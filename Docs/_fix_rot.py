import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT=r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_fix_rot.txt"
def w(m):
  open(LOG,"a",encoding="utf-8").write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
cls=unreal.load_class(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo=unreal.get_default_object(cls)
mesh=cdo.get_editor_property("mesh")
w("before "+str(mesh.get_editor_property("relative_rotation")))
# UE Rotator(Pitch, Yaw, Roll) — want Yaw -90 (Z)
r = unreal.Rotator()
r.pitch = 0.0
r.yaw = -90.0
r.roll = 0.0
mesh.set_editor_property("relative_rotation", r)
mesh.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -90.0))
mesh.set_editor_property("relative_scale3d", unreal.Vector(0.75, 0.75, 0.75))
w("after "+str(mesh.get_editor_property("relative_rotation")))
w("loc "+str(mesh.get_editor_property("relative_location")))
w("scale "+str(mesh.get_editor_property("relative_scale3d")))
bp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.EditorAssetLibrary.save_loaded_asset(bp)
# also save via directory
unreal.EditorAssetLibrary.save_directory("/Game/Characters/Player/KayKit", True, True)
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  for i in range(8):
    time.sleep(0.4)
    if remote.remote_nodes:
      remote.open_command_connection(remote.remote_nodes[0]["node_id"]); break
  print("ok", remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE).get("success"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_fix_rot.txt",encoding="utf-8").read())
