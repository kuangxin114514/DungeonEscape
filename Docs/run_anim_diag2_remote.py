import os,sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/anim_diag2.py"
remote=re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(20):
        time.sleep(0.5)
        nodes=remote.remote_nodes
        if nodes:
            node_id=nodes[0]["node_id"]; break
    if not node_id: raise SystemExit(2)
    remote.open_command_connection(node_id)
    stmt="p=r'%s'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'))"%SCRIPT
    result=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", result.get("success") if result else None)
    # print only last outputs briefly
    if result and result.get("output"):
        for o in result["output"][-15:]:
            print(o.get("output"))
finally:
    remote.stop()