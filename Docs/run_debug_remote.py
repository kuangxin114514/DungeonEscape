import sys,time,json
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
SCRIPT=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/anim_skel_persist.py"
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.5)
        if remote.remote_nodes: break
    print("nodes", remote.remote_nodes)
    if not remote.remote_nodes:
        print("NO NODES"); sys.exit(1)
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    # First: tiny ping writing file
    ping=r'''
open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_ping.txt","w").write("pong\n")
print("PING_OK")
'''
    r=remote.run_command(ping, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("ping", json.dumps(r, default=str)[:2000])
    r2=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%SCRIPT, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("script keys", list(r2.keys()) if r2 else None)
    print("success", r2.get("success") if r2 else None)
    print("result", str(r2.get("result"))[:3000] if r2 else None)
    print("command_log", str(r2.get("command_result"))[:3000] if r2 else None)
    # dump full
    for k,v in (r2 or {}).items():
        s=str(v)
        if len(s)>500: s=s[:500]+"..."
        print("K",k,"=",s)
finally:
    remote.stop()