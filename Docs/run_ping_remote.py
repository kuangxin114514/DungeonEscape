import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(15):
        time.sleep(0.4)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; print("NODES", len(remote.remote_nodes)); break
    if not node_id:
        print("NO_NODES")
    else:
        remote.open_command_connection(node_id)
        r=remote.run_command("import unreal; open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/ping.txt','w').write('pong\\n'); print('PONG')", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
        print("success", r.get("success"), "result", r.get("result"))
finally:
    remote.stop()
