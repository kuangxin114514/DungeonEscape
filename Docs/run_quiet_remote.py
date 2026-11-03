# -*- coding: utf-8 -*-
"""Run a UE python file via remote exec; read OUT txt (avoids huge JSON)."""
import os, sys, time
SCRIPT = sys.argv[1]
OUT = sys.argv[2]
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
# suppress unreal log flood by writing OUT only from script
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(30):
        time.sleep(0.5)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]
            print("node", remote.remote_nodes[0].get("project_name"), node_id)
            break
        print("wait", i)
    if not node_id:
        print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    # clear out first
    open(OUT, "w", encoding="utf-8").write("pending\n")
    stmt = (
        "p=r'%s'\n"
        "ns={}\n"
        "exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'), ns, ns)\n"
        "'OK'\n"
    ) % SCRIPT.replace("\\", "/")
    try:
        r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
        print("success", r.get("success"))
        outs = r.get("output") or []
        print("n_output", len(outs))
        for o in outs[-5:]:
            print(o.get("type"), (o.get("output") or "")[:180])
    except Exception as e:
        print("remote_exc", type(e).__name__, e)
finally:
    remote.stop()
time.sleep(0.3)
print("====OUT====")
print(open(OUT, encoding="utf-8", errors="replace").read() if os.path.exists(OUT) else "NO_OUT")
