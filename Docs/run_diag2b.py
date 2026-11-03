import os,sys,time,json,traceback
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2.py"
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(30):
        time.sleep(0.3)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; print("node", node_id); break
    if not node_id: raise SystemExit("NO_NODES")
    remote.open_command_connection(node_id)
    stmt = (
        "import traceback\n"
        "p=r'%s'\n"
        "try:\n"
        "    exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec'))\n"
        "    print('OK')\n"
        "except Exception:\n"
        "    traceback.print_exc()\n"
        "    open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2_err.txt','w',encoding='utf-8').write(traceback.format_exc())\n"
    ) % SCRIPT
    r=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"), "result", r.get("result"))
    for o in (r.get("output") or [])[-40:]:
        print(o.get("type"), (o.get("output") or "")[:500])
finally:
    try: remote.stop()
    except Exception: pass
for f in [r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2.txt', r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2_err.txt']:
    print('====', f, '====')
    if os.path.exists(f):
        print(open(f,encoding='utf-8',errors='replace').read())
    else:
        print('missing')
