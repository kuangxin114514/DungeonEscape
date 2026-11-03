# -*- coding: utf-8 -*-
import os,sys,time,json
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_shop_btns.py"
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_shop_btns.txt"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(30):
        time.sleep(0.5)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; break
    if not node_id: print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    # write result to file only to avoid huge JSON
    r=remote.run_command("p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'))"%SCRIPT, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
finally:
    remote.stop()
print(open(OUT,encoding="utf-8").read() if os.path.exists(OUT) else "NO_OUT")
