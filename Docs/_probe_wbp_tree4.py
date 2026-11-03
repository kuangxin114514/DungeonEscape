import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp4.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
full="/Game/UI/Shop/WBP_ShopProbe"
wbp=unreal.EditorAssetLibrary.load_asset(full)
tree=unreal.find_object(wbp,"WidgetTree")
# recreate clean-ish
canvas=unreal.find_object(tree,"RootCanvas")
if not canvas:
  canvas=unreal.new_object(unreal.CanvasPanel, tree, unreal.Name("RootCanvas"))
w("canvas="+str(canvas))
# set root
for attempt in [
  lambda: tree.set_editor_property("RootWidget", canvas),
  lambda: tree.set_editor_property("root_widget", canvas),
  lambda: setattr(tree, "root_widget", canvas),
  lambda: tree.call_method("set_editor_property", ("RootWidget", canvas)),
]:
  try:
    attempt(); w("set root OK "+str(attempt))
  except Exception as e:
    w("set root fail "+repr(e))
# try with EditorUtility or WidgetBlueprint
try:
  # unreal.SystemLibrary / PropertyAccess?
  w(str(tree.__dict__ if hasattr(tree,"__dict__") else "no dict"))
except Exception as e:
  w(str(e))
# try duplicate MainMenu WBP as base then mutate children
src="/Game/UI/Menus/WBP_MainMenu"
dst_dir="/Game/UI/Shop"
dst_name="WBP_ShopFromMenu"
dst=dst_dir+"/"+dst_name
if unreal.EditorAssetLibrary.does_asset_exist(dst):
  unreal.EditorAssetLibrary.delete_asset(dst)
ok=unreal.EditorAssetLibrary.duplicate_asset(dst_name, dst_dir, src)
w("dup="+str(ok))
dup=unreal.EditorAssetLibrary.load_asset(dst)
dtree=unreal.find_object(dup,"WidgetTree")
w("dup tree children:")
for o in unreal.ObjectIterator():
  try:
    if o.get_outer()==dtree or (o.get_outer() and o.get_outer().get_outer()==dtree):
      w("  %s %s outer=%s"%(o.get_name(), o.get_class().get_name(), o.get_outer().get_name()))
  except Exception:
    pass
# TextBlock set text on existing
for o in unreal.ObjectIterator(unreal.TextBlock):
  try:
    if str(o.get_path_name()).startswith(dst):
      w("TB %s textprop..."%o.get_name())
      try:
        o.set_editor_property("text", unreal.Text("TEST"))
        w("  set text ok")
      except Exception as e:
        w("  set text "+repr(e))
  except Exception:
    pass
# Button rename?
# Check add_child_to_canvas
try:
  w("canvas methods via call")
  slot=canvas.add_child_to_canvas(unreal.new_object(unreal.TextBlock, tree, unreal.Name("T1")))
  w("add_child="+str(slot))
except Exception as e:
  w("add_child fail "+repr(e))
# Compile blueprint alternatives
for n in dir(unreal):
  if "Compile" in n or "compile" in n:
    w("compile-ish "+n)
# KismetEditorUtilities?
for n in dir(unreal):
  if "Kismet" in n and "Editor" in n:
    w("kismet "+n)
try:
  kue=unreal.KismetEditorUtilities
  w("KUE="+str(kue)+" dir="+str([x for x in dir(kue) if "comp" in x.lower() or "blue" in x.lower()][:40]))
except Exception as e:
  w("KUE "+repr(e))
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
  print("result", (r.get("result") or "")[:500])
finally:
  remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp4.txt",encoding="utf-8").read())
