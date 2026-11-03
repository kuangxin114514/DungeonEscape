import os,sys,time
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
    # tiny test
    r=remote.run_command("open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_tiny.txt','w',encoding='utf-8').write('hi\\n'); print(123)", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("tiny success", r.get("success"), r.get("result"))
    for o in (r.get("output") or [])[-10:]:
        print(o.get("type"), o.get("output"))
    # try exec file with error dump in same statement via nested exec
    stmt = "exec('''open(r\"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2_err.txt\",\"w\",encoding=\"utf-8\").write(\"start\\n\")\\nimport traceback\\ntry:\\n p=r\"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2.py\"\\n exec(compile(open(p,encoding=\"utf-8-sig\").read(),p,\"exec\"))\\n open(r\"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2_err.txt\",\"a\",encoding=\"utf-8\").write(\"ok\\n\")\\nexcept Exception:\\n open(r\"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/diag_health_hud2_err.txt\",\"a\",encoding=\"utf-8\").write(traceback.format_exc())\\n''')"
    r2=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("wrap success", r2.get("success"), r2.get("result"))
    for o in (r2.get("output") or [])[-20:]:
        print(o.get("type"), (o.get("output") or "")[:300])
finally:
    try: remote.stop()
    except Exception: pass
print('tiny', open(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_tiny.txt').read() if os.path.exists(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_tiny.txt') else 'missing')
print('err', open(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2_err.txt',encoding='utf-8',errors='replace').read() if os.path.exists(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2_err.txt') else 'missing')
print('out', open(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2.txt',encoding='utf-8',errors='replace').read() if os.path.exists(r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_health_hud2.txt') else 'missing')
