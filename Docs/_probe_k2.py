import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_k2.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
for n in ["K2Node_Event","K2Node_InputAction","K2Node_CallFunction","K2Node_CreateWidget","EdGraph","EdGraphNode","BlueprintEditorLibrary","WidgetTree","KismetEditorUtilities","SubobjectDataSubsystem"]:
  w("%s %s"%(n, hasattr(unreal,n)))
# try load K2Node class
for path in [
 "/Script/BlueprintGraph.K2Node_Event",
 "/Script/BlueprintGraph.K2Node_InputAction",
 "/Script/UnrealEd.KismetEditorUtilities",
]:
  try:
    c=unreal.load_class(None, path)
    w("load_class %s -> %s"%(path,c))
  except Exception as e:
    w("load_class %s %s"%(path,e))
# uclass test
try:
  @unreal.uclass()
  class ShopHelper(unreal.Actor):
    @unreal.ufunction(override=True)
    def receive_begin_play(self):
      unreal.log("ShopHelper begin play")
  w("uclass ok "+str(ShopHelper))
  a=unreal.EditorLevelLibrary.spawn_actor_from_class(ShopHelper, unreal.Vector(0,0,200), unreal.Rotator())
  w("spawned helper "+str(a))
except Exception as e:
  w("uclass fail "+repr(e))
# PIE world helpers
w([x for x in dir(unreal.EditorLevelLibrary) if "pie" in x.lower() or "play" in x.lower() or "game" in x.lower()][:40])
w([x for x in dir(unreal) if "pie" in x.lower() or "Pie" in x or "register_" in x][:50])
w("DONE")
'''
remote=re.RemoteExecution(); remote.start()
try:
  node_id=None
  for i in range(10):
    time.sleep(0.5)
    if remote.remote_nodes:
      node_id=remote.remote_nodes[0]["node_id"]; break
  remote.open_command_connection(node_id)
  r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
  print("success", r.get("success"))
  print("result", (r.get("result") or "")[:800])
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_k2.txt",encoding="utf-8").read())
