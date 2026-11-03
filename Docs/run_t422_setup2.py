# -*- coding: utf-8 -*-
import os,sys,time,traceback
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/setup_d2_d3_t422.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_d2_d3_t422.txt"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
 node=None
 for i in range(50):
  time.sleep(0.4)
  if remote.remote_nodes: node=remote.remote_nodes[0]["node_id"]; break
 print("nodes", remote.remote_nodes)
 if not node: print("NO_NODES")
 else:
  remote.open_command_connection(node)
  # simpler first
  r=remote.run_command("print('hi_ue')",unattended=True,exec_mode=re.MODE_EXEC_STATEMENT)
  print("hi", r)
  cmd="exec(compile(open(r'%s',encoding='utf-8-sig').read(),'setup','exec'))"%SCRIPT.replace("\\","/")
  r=remote.run_command(cmd,unattended=True,exec_mode=re.MODE_EXEC_STATEMENT)
  print("ok",r.get("success"), "result", r)
  for o in (r.get("output") or [])[:60]:
    print(o.get("type"), (o.get("output") or "")[:400])
finally:
 remote.stop()
print("OUT", open(OUT,encoding="utf-8",errors="replace").read() if os.path.exists(OUT) else "NO")
