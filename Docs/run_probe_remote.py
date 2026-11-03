# -*- coding: utf-8 -*-
import os, sys, time
ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
SCRIPT = os.path.join(ROOT, "Docs", "probe_scs_apis.py").replace("\\", "/")
REMOTE_MOD = r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
sys.path.insert(0, REMOTE_MOD)
import remote_execution as re
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(12):
        time.sleep(0.7)
        nodes = remote.remote_nodes
        print("try", i, "n", len(nodes) if nodes else 0)
        if nodes:
            node_id = nodes[0]["node_id"]
            print("node", nodes[0].get("project_name"), node_id)
            break
    if not node_id:
        print("NO_NODES"); raise SystemExit(2)
    remote.open_command_connection(node_id)
    stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8').read(),p,'exec')); print('PROBE_REMOTE_DONE')" % SCRIPT
    result = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("RESULT", result)
finally:
    try: remote.stop()
    except Exception: pass
