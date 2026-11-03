import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp5.txt"
def w(m):
  with open(LOG,"a",encoding="utf-8") as f: f.write(str(m)+"\n")
open(LOG,"w",encoding="utf-8").write("begin\n")
wbp=unreal.EditorAssetLibrary.load_asset("/Game/UI/Shop/WBP_ShopProbe")
raw=unreal.find_object(wbp,"WidgetTree")
w("raw type="+str(type(raw))+" cls="+raw.get_class().get_name())
# cast
try:
  tree=unreal.WidgetTree.cast(raw)
  w("cast="+str(tree)+" type="+str(type(tree)))
  w("dir="+str([x for x in dir(tree) if not x.startswith("_")]))
except Exception as e:
  w("cast fail "+repr(e))
# try WidgetBlueprint cast
try:
  wb=unreal.WidgetBlueprint.cast(wbp)
  w("wb cast="+str(wb))
  w("wb dir widget="+str([x for x in dir(wb) if "widget" in x.lower() or "tree" in x.lower()]))
except Exception as e:
  w("wb cast "+repr(e))
# duplicate_asset signature
w("dup sig try")
try:
  # UE4: duplicate_asset(source_asset_path, destination_asset_path) OR (name, path, ...)
  w(str(unreal.EditorAssetLibrary.duplicate_asset))
except Exception as e:
  w(repr(e))
src="/Game/UI/Menus/WBP_MainMenu"
dst="/Game/UI/Shop/WBP_ShopFromMenu"
if unreal.EditorAssetLibrary.does_asset_exist(dst):
  unreal.EditorAssetLibrary.delete_asset(dst)
try:
  ok=unreal.EditorAssetLibrary.duplicate_asset(src, dst)
  w("dup2arg="+str(ok))
except Exception as e:
  w("dup2arg fail "+repr(e))
# AssetTools duplicate
try:
  tools=unreal.AssetToolsHelpers.get_asset_tools()
  data=unreal.AssetRenameData(unreal.EditorAssetLibrary.load_asset(src), "/Game/UI/Shop", "WBP_ShopFromMenu2")
  # better: duplicate via asset tools
  w("asset tools methods "+str([x for x in dir(tools) if "dup" in x.lower() or "Dup" in x]))
except Exception as e:
  w(repr(e))
try:
  tools=unreal.AssetToolsHelpers.get_asset_tools()
  # duplicate_asset(asset, destination_path, newname?) 
  a=unreal.EditorAssetLibrary.load_asset(src)
  for args in [
    lambda: tools.duplicate_asset("WBP_ShopFromMenu2", "/Game/UI/Shop", a),
  ]:
    try:
      r=args(); w("tools dup="+str(r))
    except Exception as e:
      w("tools dup fail "+repr(e))
except Exception as e:
  w(repr(e))
# pyexec console?
w("has execute_console_command "+str(hasattr(unreal.SystemLibrary,"execute_console_command")))
# try EditorLevelLibrary editor play?
# KismetSystemLibrary execute console to run py?
try:
  unreal.SystemLibrary.execute_console_command(None, 'py "print(123)"')
  w("console py tried")
except Exception as e:
  w("console "+repr(e))
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
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_wbp5.txt",encoding="utf-8").read())
