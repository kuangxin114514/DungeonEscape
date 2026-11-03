import os,sys,time
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/setup_t380_engine_ai.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t380_engine_ai.txt"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
 node=None
 for i in range(50):
  time.sleep(0.4)
  if remote.remote_nodes: node=remote.remote_nodes[0]["node_id"]; break
 if not node:
  print("NO_NODES"); raise SystemExit(2)
 remote.open_command_connection(node)
 # long-running: maps + compile
 r=remote.run_command("p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('SETUP_DONE')"%SCRIPT, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
 print("success", r.get("success"))
 for o in (r.get("output") or [])[-30:]:
  s=(o.get("output") or "")
  if s: print(s[:400])
finally:
 remote.stop()
print("---OUT---")
print(open(OUT,encoding="utf-8").read() if os.path.exists(OUT) else "NO_OUT")
