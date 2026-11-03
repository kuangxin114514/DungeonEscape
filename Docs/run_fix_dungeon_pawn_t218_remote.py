# -*- coding: utf-8 -*-
import os, sys, time, shutil
ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
SCRIPT_NAME = "fix_map_dungeon_pawn_t218.py"
SRC = os.path.join(r"C:\Users\86178\agent-tools", SCRIPT_NAME)
# also try Docs if already copied
SCRIPT = os.path.join(ROOT, "Docs", SCRIPT_NAME)
OUT = os.path.join(ROOT, "Docs", "fix_map_dungeon_pawn_t218.txt")
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re

# Prefer Docs copy
if not os.path.exists(SCRIPT):
    if os.path.exists(SRC):
        shutil.copy2(SRC, SCRIPT)
    else:
        print("NO_SCRIPT", SCRIPT, SRC)
        sys.exit(3)

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
        print("NO_NODES")
        sys.exit(2)
    remote.open_command_connection(node_id)
    open(OUT, "w", encoding="utf-8").write("pending\n")
    r0 = remote.run_command("print('PING_OK')", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("ping_success", r0.get("success"))
    for o in (r0.get("output") or [])[-5:]:
        print("ping", o.get("type"), (o.get("output") or "")[:200])
    stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')" % SCRIPT.replace("\\", "/")
    r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    print("result", r.get("result"))
    for o in (r.get("output") or []):
        print(o.get("type"), (o.get("output") or "")[:500])
finally:
    remote.stop()
time.sleep(0.5)
print("====OUT====")
if os.path.exists(OUT):
    print(open(OUT, encoding="utf-8", errors="replace").read())
else:
    print("NO_OUT")
