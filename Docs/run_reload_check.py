import sys,time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote=re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(20):
        time.sleep(0.3)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; break
    if not node_id:
        print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    stmt=(
        "import importlib,sys\n"
        "sys.path.insert(0,r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Content\\Python')\n"
        "import shop_interact_runtime as r\n"
        "importlib.reload(r)\n"
        "open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/reload_ok.txt','w').write('reload_ok '+str(hasattr(r,'open_shop'))+'\\n')\n"
        "print('RELOAD_OK')"
    )
    # single line
    stmt="p=r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Content/Python/shop_interact_runtime.py'; import importlib,sys; sys.path.insert(0,r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Content\\Python'); import shop_interact_runtime as r; importlib.reload(r); open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/reload_ok.txt','w',encoding='utf-8').write('ok\\n'); print('RELOAD_OK')"
    r=remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    for o in (r.get("output") or [])[-8:]:
        print(o.get("type"), (o.get("output") or "")[:160])
finally:
    remote.stop()
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_ok.txt",encoding="utf-8").read() if __import__('os').path.exists(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_ok.txt") else "NO")
# show lines around tick patch
$i=400; Get-Content "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py" | Select-Object -Skip 400 -First 25 | ForEach-Object -Begin {$n=401} -Process { "$n`:$_"; $n++ }
