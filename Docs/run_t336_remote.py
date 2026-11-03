# -*- coding: utf-8 -*-
import os, sys, time
SCRIPT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/t336_scale.py"
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    node_id = None
    for i in range(30):
        time.sleep(0.4)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]; break
    remote.open_command_connection(node_id)
    stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')" % SCRIPT
    r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    for o in (r.get("output") or []):
        print(o.get("type"), o.get("output"))
    r2 = remote.run_command("p=r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/reload_t323_buy_sword1.py'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'))", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("reload", r2.get("success"))
finally:
    remote.stop()
