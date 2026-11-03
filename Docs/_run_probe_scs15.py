import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    for i in range(12):
        time.sleep(0.3); nodes = remote.remote_nodes
        if nodes:
            remote.open_command_connection(nodes[0]["node_id"]); break
    # Use exec_mode that minimizes return payload - script writes its own log
    r = remote.run_command("exec(open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_probe_scs15.py',encoding='utf-8').read()); print('OK')", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    if isinstance(r, dict):
        print("success", r.get("success"))
        for o in (r.get("output") or [])[:30]:
            print(o.get("output"))
        if not r.get("success"):
            print("FAIL", (r.get("result") or "")[:500])
    else:
        print(r)
finally:
    remote.stop()