# -*- coding: utf-8 -*-
import os,sys,time
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/clear_bake_t438b.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t438b.txt"
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
  r=remote.run_command("exec(compile(open(r'%s',encoding='utf-8-sig').read(),'t438b','exec'))"%SCRIPT,unattended=True,exec_mode=re.MODE_EXEC_STATEMENT)
  print("ok", bool(r.get("success")))
  for o in (r.get("output") or [])[:30]:
    print(o.get("type"), (o.get("output") or "").encode("ascii","replace").decode("ascii")[:300])
finally: remote.stop()
print(open(OUT,encoding="utf-8",errors="replace").read() if os.path.exists(OUT) else "NO")
print("---DISK---")
print(os.path.exists(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Maps\Dungeon\Map_Dungeon2_BuiltData.uasset"))
