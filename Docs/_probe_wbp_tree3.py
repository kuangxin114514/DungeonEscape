import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp3.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
# Create fresh WBP
path="/Game/UI/Shop"
if not unreal.EditorAssetLibrary.does_directory_exist(path):
  unreal.EditorAssetLibrary.make_directory(path)
full=path+"/WBP_ShopProbe"
if unreal.EditorAssetLibrary.does_asset_exist(full):
  unreal.EditorAssetLibrary.delete_asset(full)
factory=unreal.WidgetBlueprintFactory()
try:
  factory.set_editor_property("ParentClass", unreal.UserWidget)
except Exception as e:
  w("parent "+str(e))
tools=unreal.AssetToolsHelpers.get_asset_tools()
wbp=tools.create_asset("WBP_ShopProbe", path, unreal.WidgetBlueprint, factory)
w("wbp="+str(wbp))
unreal.EditorAssetLibrary.save_loaded_asset(wbp)
wbp=unreal.EditorAssetLibrary.load_asset(full)
tree=unreal.find_object(wbp,"WidgetTree")
w("tree="+str(tree))
# try construct_widget
for meth in ("construct_widget","ConstructWidget"):
  w("hasattr "+meth+" "+str(hasattr(tree, meth)))
try:
  canvas=tree.construct_widget(unreal.CanvasPanel, "RootCanvas")
  w("canvas="+str(canvas))
except Exception as e:
  w("construct fail "+repr(e))
# try call_method
try:
  canvas=tree.call_method("ConstructWidget", (unreal.CanvasPanel, "RootCanvas"))
  w("call_method="+str(canvas))
except Exception as e:
  w("call_method fail "+repr(e))
# try new_object under tree
try:
  canvas=unreal.new_object(unreal.CanvasPanel, tree, unreal.Name("RootCanvas"))
  w("new_object="+str(canvas))
except Exception as e:
  w("new_object fail "+repr(e))
# BlueprintEditorLibrary via find
for n in dir(unreal):
  if "Blueprint" in n and "Editor" in n:
    w("found type "+n)
# try load module
try:
  bel=unreal.load_class(None, "/Script/BlueprintEditorLibrary.BlueprintEditorLibrary")
  w("bel class "+str(bel))
except Exception as e:
  w("bel load "+str(e))
try:
  bel=unreal.find_object(None, "/Script/BlueprintGraph.Default__KismetCompilerUtilities")
  w("kc "+str(bel))
except Exception as e:
  w(str(e))
# EditorAssetLibrary does_asset compile?
w([x for x in dir(unreal) if "compile" in x.lower() or "Compile" in x][:30])
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
  print("result", r.get("result"))
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp3.txt",encoding="utf-8").read())
