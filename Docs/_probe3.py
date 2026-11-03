import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.3)
        if remote.remote_nodes:
            nid = remote.remote_nodes[0]["node_id"]; break
    remote.open_command_connection(nid)
    path = r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_mini.py"
    for mode in (re.MODE_EXEC_FILE, re.MODE_EXEC_STATEMENT, re.MODE_EVAL_STATEMENT):
        r = remote.run_command(path, unattended=True, exec_mode=mode)
        print("mode", mode, "success", r.get("success"), "result", str(r.get("result"))[:200])
        for o in (r.get("output") or [])[-3:]:
            print(" ", o.get("type"), (o.get("output") or "")[:200])
    # try ExecuteFile with raw source as command?
    src = open(path, encoding="utf-8").read()
    r = remote.run_command(src, unattended=True, exec_mode=re.MODE_EXEC_FILE)
    print("FILE_as_src success", r.get("success"), "result", str(r.get("result"))[:200])
    for o in (r.get("output") or [])[-5:]:
        print(" ", o.get("type"), (o.get("output") or "")[:200])
    # single-line eval exec
    expr = "exec(compile(open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_mini.py',encoding='utf-8').read(),'mini','exec'))"
    r = remote.run_command(expr, unattended=True, exec_mode=re.MODE_EVAL_STATEMENT)
    print("EVAL exec success", r.get("success"), "result", str(r.get("result"))[:200])
    for o in (r.get("output") or [])[-5:]:
        print(" ", o.get("type"), (o.get("output") or "")[:200])
finally:
    remote.stop()
print("OUT", open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t206.txt",encoding="utf-8",errors="replace").read())
