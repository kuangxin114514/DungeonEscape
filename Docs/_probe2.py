import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
print("modes", re.MODE_EXEC_FILE, re.MODE_EXEC_STATEMENT, re.MODE_EVAL_STATEMENT)
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(20):
        time.sleep(0.5)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]; break
    remote.open_command_connection(node_id)
    # EXEC statement simple
    r = remote.run_command("import unreal\nunreal.log('T206_PING')\n", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("exec1 success", r.get("success"), "result", r.get("result"))
    for o in (r.get("output") or [])[-8:]:
        print(o.get("type"), (o.get("output") or "")[:250])
    # write file via exec
    stmt = "open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/fix_t206.txt','w',encoding='utf-8').write('probe2\\n')\n"
    r2 = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("exec2 success", r2.get("success"), "result", r2.get("result"))
    for o in (r2.get("output") or [])[-5:]:
        print(o.get("type"), (o.get("output") or "")[:250])
    # exec file
    p = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/fix_t206_e_shop.py"
    stmt3 = (
        "p=r'%s'\n"
        "ns={}\n"
        "exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'), ns, ns)\n"
    ) % p.replace("\\", "/")
    r3 = remote.run_command(stmt3, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("exec3 success", r3.get("success"), "result", str(r3.get("result"))[:200])
    outs = r3.get("output") or []
    print("n_output", len(outs))
    for o in outs[-15:]:
        print(o.get("type"), (o.get("output") or "")[:300])
finally:
    remote.stop()
print("====OUT====")
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t206.txt",encoding="utf-8",errors="replace").read())
