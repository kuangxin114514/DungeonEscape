import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal, os
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_out.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
w([x for x in dir(unreal.EditorSkeletalMeshLibrary) if not x.startswith("_")])
bp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
for o in unreal.ObjectIterator(unreal.Object):
  try:
    if o.get_outer()==bp:
      w("CHILD %s %s"%(o.get_name(), o.get_class().get_name()))
  except Exception as e:
    pass
# try get GeneratedClass property (Pascal)
for n in ("GeneratedClass","ParentClass","SimpleConstructionScript","Status"):
  try:
    w("PROP %s = %s"%(n, bp.get_editor_property(n)))
  except Exception as e:
    w("PROPFAIL %s %s"%(n,e))
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  node_id=None
  for i in range(8):
    time.sleep(0.5)
    if remote.remote_nodes: node_id=remote.remote_nodes[0]["node_id"]; break
  remote.open_command_connection(node_id)
  r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
  print("success", r.get("success"), "result", r.get("result"))
finally:
  remote.stop()
print("---file---")
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_out.txt",encoding="utf-8").read())
