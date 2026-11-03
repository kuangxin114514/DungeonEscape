# -*- coding: utf-8 -*-
import os,sys,time
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/clear_bake_t438c.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t438c.txt"
DISK=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Maps\Dungeon\Map_Dungeon2_BuiltData.uasset"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
 node=None
 for i in range(40):
  time.sleep(0.4)
  if remote.remote_nodes: node=remote.remote_nodes[0]["node_id"]; break
 if not node: print("NO_NODES")
 else:
  remote.open_command_connection(node)
  r=remote.run_command("exec(compile(open(r'%s',encoding='utf-8-sig').read(),'t438c','exec'))"%SCRIPT,unattended=True,exec_mode=re.MODE_EXEC_STATEMENT)
  print("ok", bool(r.get("success")))
  for o in (r.get("output") or [])[:30]:
    print(o.get("type"), (o.get("output") or "").encode("ascii","replace").decode("ascii")[:300])
  # After switching to D1, try delete file from disk
  time.sleep(1)
  try:
    if os.path.exists(DISK):
      os.remove(DISK)
      print("DISK_REMOVED")
    else:
      print("DISK_ALREADY_GONE")
  except Exception as e:
    print("DISK_ERR", e)
  # reload dungeon2 + force no
  SCRIPT2=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/clear_bake_t438d.py"
  open(SCRIPT2,"w",encoding="utf-8").write("""# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r'C:\\\\Users\\\\86178\\\\Documents\\\\Unreal Projects\\\\DungeonEscape\\\\Docs\\\\clear_bake_t438d.txt'
lines=[]
def L(s):
 lines.append(str(s)); print(s)
unreal.EditorLevelLibrary.load_level('/Game/Maps/Dungeon/Map_Dungeon2')
world=unreal.EditorLevelLibrary.get_editor_world()
L('world='+str(world.get_path_name() if world else None))
ws=world.get_world_settings()
ws.set_editor_property('force_no_precomputed_lighting', True)
L('ForceNo=True')
# invalidate lighting build data on world if property exists
try:
 unreal.SystemLibrary.execute_console_command(world, 'r.ForceDebugViewModes 0')
except Exception:
 pass
try:
 unreal.EditorLevelLibrary.save_current_level()
 L('saved')
except Exception as e:
 L('save ERR '+str(e))
built='/Game/Maps/Dungeon/Map_Dungeon2_BuiltData'
L('BuiltData exists='+str(unreal.EditorAssetLibrary.does_asset_exist(built)))
open(OUT,'w',encoding='utf-8').write('\\n'.join(lines))
""")
  r2=remote.run_command("exec(compile(open(r'%s',encoding='utf-8-sig').read(),'t438d','exec'))"%SCRIPT2,unattended=True,exec_mode=re.MODE_EXEC_STATEMENT)
  print("ok2", bool(r2.get("success")))
  for o in (r2.get("output") or [])[:20]:
    print(o.get("type"), (o.get("output") or "").encode("ascii","replace").decode("ascii")[:300])
finally: remote.stop()
print(open(OUT,encoding="utf-8",errors="replace").read() if os.path.exists(OUT) else "NO")
print("disk_exists", os.path.exists(DISK))
