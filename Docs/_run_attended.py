import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
script = sys.argv[1]
remote = re.RemoteExecution(); remote.start()
try:
    for i in range(12):
        time.sleep(0.3); nodes = remote.remote_nodes
        if nodes:
            remote.open_command_connection(nodes[0]["node_id"]); break
    else:
        print("NO_REMOTE_NODES"); sys.exit(2)
    cmd = "exec(open(r'%s',encoding='utf-8').read())" % script.replace("\\","/")
    # unattended=False so dialogs can appear
    r = remote.run_command(cmd, unattended=False, exec_mode=re.MODE_EXEC_STATEMENT)
    if isinstance(r, dict):
        for o in (r.get("output") or []):
            try: print(o.get("output"))
            except Exception: print(repr(o.get("output")))
        if not r.get("success"):
            msg = (r.get("result") or "")
            try: print("FAIL", msg[:1200])
            except Exception: print("FAIL", repr(msg[:1200]))
    else:
        print("RAW", r)
finally:
    remote.stop()