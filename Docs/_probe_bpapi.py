import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_bpapi.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
# find libraries
for n in sorted(dir(unreal)):
  if any(k in n for k in ("KismetEditor","Blueprint","EditorAsset","Subobject","Compile","SCS","SimpleConstruction")):
    w(n)
# try load BlueprintEditorLibrary class from plugin
for path in [
  "/Script/BlueprintEditorLibrary.BlueprintEditorLibrary",
  "/Script/EditorScriptingUtilities.EditorAssetLibrary",
]:
  try:
    c=unreal.load_object(None, path)
    w("load_object %s -> %s"%(path,c))
  except Exception as e:
    w("load_object %s fail %s"%(path,e))
  try:
    c=unreal.load_class(None, path)
    w("load_class %s -> %s"%(path,c))
  except Exception as e:
    w("load_class %s %s"%(path,e))
# console py to access BEL?
try:
  unreal.SystemLibrary.execute_console_command(None, r'py "import unreal; print(\"BEL\", hasattr(unreal,\"BlueprintEditorLibrary\")); print([x for x in dir(unreal) if \"BlueprintEditor\" in x])"')
  w("console richer py issued")
except Exception as e:
  w(repr(e))
# Create TriggerBox BP
path="/Game/Core/Interact"
if not unreal.EditorAssetLibrary.does_directory_exist(path):
  unreal.EditorAssetLibrary.make_directory(path)
full=path+"/BP_ShopProbe"
if unreal.EditorAssetLibrary.does_asset_exist(full):
  unreal.EditorAssetLibrary.delete_asset(full)
factory=unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.TriggerBox)
bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_ShopProbe", path, None, factory)
w("bp="+str(bp))
unreal.EditorAssetLibrary.save_loaded_asset(bp)
# gen class
try:
  g=bp.generated_class(); w("gen="+str(g))
except Exception as e:
  w("gen fail "+repr(e))
try:
  g=unreal.load_class(None, full+".BP_ShopProbe_C"); w("load_class gen="+str(g))
except Exception as e:
  w("load_class gen "+repr(e))
# ubergraph
try:
  pages=list(bp.ubergraph_pages); w("ubergraph_pages="+str(pages))
except Exception as e:
  w("ubergraph_pages fail "+repr(e))
for o in unreal.ObjectIterator(unreal.EdGraph):
  try:
    if o.get_outer()==bp:
      w("graph %s"%o.get_name())
  except Exception:
    pass
# Try add variable via K2Schema?
try:
  w("EdGraphSchema_K2="+str(unreal.EdGraphSchema_K2))
except Exception as e:
  w(repr(e))
# tags on actor instead of variables - can set default tags on CDO?
# Instance editable via...
# Check if we can set Actor tags on CDO
try:
  g=unreal.load_class(None, full+".BP_ShopProbe_C")
  cdo=unreal.get_default_object(g)
  w("cdo="+str(cdo))
  box=cdo.get_component_by_class(unreal.BoxComponent)
  w("box="+str(box))
  if box:
    try:
      box.set_box_extent(unreal.Vector(200,200,150), True)
      w("extent ok")
    except Exception as e:
      w("extent "+repr(e))
    try:
      box.set_editor_property("box_extent", unreal.Vector(200,200,160))
      w("extent prop ok")
    except Exception as e:
      w("extent prop "+repr(e))
except Exception as e:
  w("cdo cfg "+repr(e))
# Input mapping via python?
try:
  sett=unreal.InputSettings.get_input_settings()
  w("input settings="+str(sett))
  w("actions methods "+str([x for x in dir(sett) if "Action" in x or "action" in x][:30]))
except Exception as e:
  w("input "+repr(e))
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
  print("result", (r.get("result") or "")[:1000])
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_bpapi.txt",encoding="utf-8").read())
