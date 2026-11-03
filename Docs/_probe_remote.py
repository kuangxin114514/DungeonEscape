import sys, time, json
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(30):
        time.sleep(0.5)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]
            print("node", remote.remote_nodes[0])
            break
    if not node_id:
        print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    # simple probe
    r = remote.run_command("import unreal; unreal.log('T206_PING'); 'PING_OK'", unattended=True, exec_mode=re.MODE_EVAL_STATEMENT)
    print("eval success", r.get("success"), "result", r.get("result"))
    for o in (r.get("output") or [])[-10:]:
        print(o.get("type"), (o.get("output") or "")[:300])
    # try exec file read
    stmt = "open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/fix_t206.txt','w',encoding='utf-8').write('probe\\n'); 'WROTE'"
    r2 = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EVAL_STATEMENT)
    print("write success", r2.get("success"), "result", r2.get("result"))
    for o in (r2.get("output") or [])[-5:]:
        print(o.get("type"), (o.get("output") or "")[:300])
finally:
    remote.stop()
print("file", open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t206.txt",encoding="utf-8",errors="replace").read())
