import os,sys,time
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/t380_single_node.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\t380_single_node.txt"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
 node=None
 for i in range(40):
  time.sleep(0.35)
  if remote.remote_nodes: node=remote.remote_nodes[0]["node_id"]; break
 if not node: print("NO_NODES"); raise SystemExit(2)
 remote.open_command_connection(node)
 r=remote.run_command("p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'))"%SCRIPT, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
 print("success", r.get("success"))
 for o in (r.get("output") or [])[-10:]:
  s=(o.get("output") or "");
  if s: print(s[:300])
finally:
 remote.stop()
print(open(OUT,encoding="utf-8").read() if os.path.exists(OUT) else "NO")
