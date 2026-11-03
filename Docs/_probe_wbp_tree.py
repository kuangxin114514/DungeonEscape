import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
# existing main menu
mm=unreal.EditorAssetLibrary.load_asset("/Game/UI/Menus/WBP_MainMenu")
w("mm=%s cls=%s"%(mm, mm.get_class().get_name() if mm else None))
if mm:
  w("dir_widgetish="+str([x for x in dir(mm) if "widget" in x.lower() or "tree" in x.lower()][:40]))
  for o in unreal.ObjectIterator():
    try:
      if o.get_outer()==mm:
        w("child %s %s"%(o.get_name(), o.get_class().get_name()))
    except Exception:
      pass
  # find WidgetTree by path
  for name in ("WidgetTree","WidgetTree_0"):
    try:
      o=unreal.find_object(mm, name)
      w("find %s -> %s"%(name,o))
    except Exception as e:
      w("find fail %s %s"%(name,e))
  try:
    o=unreal.load_object(mm, "WidgetTree")
    w("load_object WidgetTree %s"%o)
  except Exception as e:
    w("load_object fail %s"%e)
# check WidgetBlueprintLibrary / Editor
w("has WBL "+str(hasattr(unreal,"WidgetBlueprintLibrary")))
w("bel methods "+str([x for x in dir(unreal.BlueprintEditorLibrary) if "widget" in x.lower()][:30]))
names=[x for x in dir(unreal) if "Widget" in x]
w("unreal widget types sample "+str(names[:50]))
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
  for o in r.get("output") or []:
    print(o.get("type"), o.get("output"))
finally:
  remote.stop()
print("---file---")
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp.txt",encoding="utf-8").read())
