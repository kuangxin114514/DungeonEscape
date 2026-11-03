import sys,time
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/anim_verify_final.py"
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.4)
        if remote.remote_nodes: break
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    r=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%SCRIPT, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success") if r else None)
finally:
    remote.stop()