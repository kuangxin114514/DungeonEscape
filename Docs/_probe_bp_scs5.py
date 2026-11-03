import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT=r'''
import unreal
# try console to reload editor scripting
try:
  unreal.PythonScriptLibrary.execute_python_command("import unreal; print(hasattr(unreal,\"BlueprintEditorLibrary\"))")
except Exception as e:
  print("psl", e)
print([x for x in dir(unreal) if x.startswith("Editor")][:60])
# path_name method on object
bp=unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
print("methods", [x for x in dir(bp) if "path" in x.lower() or "outer" in x.lower() or "name" in x.lower()][:40])
print("get_name", bp.get_name())
print("get_path_name_m", bp.get_path_name() if hasattr(bp,"get_path_name") else "no")
# iterate with get_name
n=0
for o in unreal.ObjectIterator(unreal.Object):
  try:
    if o.get_outer()==bp:
      print("ch", o.get_name(), o.get_class().get_name())
      n+=1
  except Exception:
    pass
print("n", n)
'''
remote=re.RemoteExecution(); remote.start()
try:
  node_id=None
  for i in range(8):
    time.sleep(0.5)
    if remote.remote_nodes: node_id=remote.remote_nodes[0]["node_id"]; break
  remote.open_command_connection(node_id)
  r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
  print("ok", r.get("success"), r.get("result"))
  for o in r.get("output") or []: print(o.get("output"))
finally:
  remote.stop()
