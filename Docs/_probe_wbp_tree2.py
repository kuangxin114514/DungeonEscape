import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp2.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
mm=unreal.EditorAssetLibrary.load_asset("/Game/UI/Menus/WBP_MainMenu")
tree=unreal.find_object(mm,"WidgetTree")
w("tree=%s"%tree)
w("dir="+str([x for x in dir(tree) if not x.startswith("_")]))
# root
for n in ("root_widget","RootWidget"):
  try:
    w("%s=%s"%(n, tree.get_editor_property(n)))
  except Exception as e:
    w("%s fail %s"%(n,e))
# list children of tree
for o in unreal.ObjectIterator():
  try:
    if o.get_outer()==tree:
      w("tchild %s %s"%(o.get_name(), o.get_class().get_name()))
  except Exception:
    pass
# BlueprintEditorLibrary availability
try:
  w("BEL="+str(unreal.BlueprintEditorLibrary))
except Exception as e:
  w("BEL fail "+str(e))
try:
  import importlib
  w("has compile "+str(hasattr(unreal,"BlueprintEditorLibrary")))
except Exception as e:
  w(str(e))
# check EditorAssetLibrary compile?
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
  print("success", r.get("success"), "result", r.get("result"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp2.txt",encoding="utf-8").read())
