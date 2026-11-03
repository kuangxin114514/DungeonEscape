import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution()
remote.start()
try:
    node_id = None
    for i in range(90):
        time.sleep(2)
        if remote.remote_nodes:
            n = remote.remote_nodes[0]
            print("READY", i*2, "s", n.get("project_name"), n.get("node_id"))
            node_id = n["node_id"]
            break
        if i % 5 == 0:
            print("wait", i*2, "s")
    if not node_id:
        print("NO_NODES"); sys.exit(2)
finally:
    remote.stop()
