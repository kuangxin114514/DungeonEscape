# -*- coding: utf-8 -*-
import os, sys, time, json
SCRIPT = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_skeleton_sink.py"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_skeleton_sink.txt"
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
# write probe script first via this same runner after we create it
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(40):
        time.sleep(0.4)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]
            print("node", remote.remote_nodes[0].get("project_name"), node_id)
            break
        print("wait", i)
    if not node_id:
        print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    open(OUT, "w", encoding="utf-8").write("pending\n")
    stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')" % SCRIPT
    r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("RAW", json.dumps({k: r.get(k) for k in ("success","result")}, ensure_ascii=False)[:2000])
    for o in (r.get("output") or [])[-60:]:
        print(o.get("type"), (o.get("output") or "")[:800])
finally:
    try: remote.stop()
    except Exception: pass
time.sleep(0.3)
print("====OUT====")
print(open(OUT, encoding="utf-8", errors="replace").read() if os.path.exists(OUT) else "NO_OUT")
