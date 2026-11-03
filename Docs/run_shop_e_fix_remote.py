# -*- coding: utf-8 -*-
import os,sys,time
ROOT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
SCRIPT=os.path.join(ROOT,"Docs","shop_e_fix.py").replace("\\","/")
LOG=os.path.join(ROOT,"Docs","shop_e_fix_remote.log")
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
  node_id=None
  for i in range(20):
    time.sleep(0.4)
    if remote.remote_nodes:
      node_id=remote.remote_nodes[0]["node_id"]; print("node", node_id); break
  if not node_id:
    open(LOG,"w").write("NO_NODES\n"); raise SystemExit(2)
  remote.open_command_connection(node_id)
  stmt="p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')"%SCRIPT
  r=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
  open(LOG,"w",encoding="utf-8").write(str(r)+"\n")
  print("success", r.get("success"))
  if r.get("output"):
    for o in r["output"]:
      if o.get("type") in ("Info","Warning","Error"):
        print(o.get("type"), o.get("output"))
finally:
  remote.stop()
print("---LOG---")
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_e_fix.txt",encoding="utf-8").read())