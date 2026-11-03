import os,sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ROOT_CAUSE_CREATE_WIDGET.txt"
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/fix_root_note.py"
remote=re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(24):
        time.sleep(0.35)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; print("node ok"); break
    if not node_id: print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    stmt="p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('RN_DONE')"%SCRIPT
    r=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:300])
finally:
    try: remote.stop()
    except Exception: pass
print(open(OUT,encoding="utf-8").read() if os.path.exists(OUT) else "NO_OUT")
