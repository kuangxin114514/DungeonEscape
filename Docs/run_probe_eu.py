# -*- coding: utf-8 -*-
import os, sys, time
SCRIPT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_eu.py"
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(12):
        time.sleep(0.6)
        nodes=remote.remote_nodes
        if nodes:
            node_id=nodes[0]["node_id"]; print("node", node_id); break
        print("try",i,"n",len(nodes) if nodes else 0)
    if not node_id: raise SystemExit(2)
    remote.open_command_connection(node_id)
    stmt="p=r'%s'; exec(compile(open(p,encoding='utf-8').read(),p,'exec')); print('EU_REMOTE_DONE')"%SCRIPT
    print(remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT))
finally:
    remote.stop()