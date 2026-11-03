import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    for i in range(60):
        time.sleep(2)
        nodes = remote.remote_nodes
        print("try", i, "n", len(nodes) if nodes else 0)
        if nodes:
            print("READY", nodes[0].get("project_name"), nodes[0]["node_id"])
            sys.exit(0)
    print("TIMEOUT")
    sys.exit(2)
finally:
    remote.stop()