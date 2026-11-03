# -*- coding: utf-8 -*-
import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
  for i in range(10):
    time.sleep(0.4); nodes=remote.remote_nodes
    if nodes:
      remote.open_command_connection(nodes[0]["node_id"]); break
  print(remote.run_command("exec(compile(open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_bgc.py',encoding='utf-8').read(),'probe_bgc.py','exec'))", unattended=True, exec_mode=re.MODE_EXEC_STATEMENT))
finally:
  remote.stop()