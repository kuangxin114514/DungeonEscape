import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    for i in range(12):
        time.sleep(0.3); nodes = remote.remote_nodes
        if nodes:
            remote.open_command_connection(nodes[0]["node_id"]); break
    print(remote.run_command("p=r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_probe_scs8.py'; exec(compile(open(p,encoding='utf-8').read(),p,'exec'))", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT))
finally:
    remote.stop()