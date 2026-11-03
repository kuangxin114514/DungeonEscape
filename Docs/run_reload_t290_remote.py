# -*- coding: utf-8 -*-
import os, sys, time
SCRIPT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/reload_t290_runtime.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t290.txt"
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(20):
        time.sleep(0.5)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]
            print("node", remote.remote_nodes[0].get("project_name"), node_id)
            break
        print("wait", i)
    if not node_id:
        print("NO_NODES")
        sys.exit(2)
    remote.open_command_connection(node_id)
    stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')" % SCRIPT
    r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    for o in (r.get("output") or []):
        print(o.get("type"), o.get("output"))
finally:
    remote.stop()
if os.path.exists(OUT):
    print("====OUT====")
    print(open(OUT, encoding="utf-8").read())
else:
    print("NO_OUT")
