# -*- coding: utf-8 -*-
import os, sys, time
SCRIPT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_call_method_t231.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_call_method_t231.txt"
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(30):
        time.sleep(0.3)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; print("node", node_id); break
    if not node_id: print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    open(OUT,"w",encoding="utf-8").write("pending\n")
    stmt="p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')"%SCRIPT
    r=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    for o in (r.get("output") or [])[-10:]:
        print(o.get("type"), (o.get("output") or "")[:250])
finally:
    remote.stop()
time.sleep(0.2)
print(open(OUT,encoding="utf-8",errors="replace").read())
