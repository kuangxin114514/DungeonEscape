# -*- coding: utf-8 -*-
import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
print("blueprints", [x for x in dir(unreal) if "lueprint" in x.lower()][:80])
print("get_path_name", unreal.get_path_name)
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
print("bp_path", unreal.get_path_name(bp))
print("bp_outer", unreal.get_outer(bp))
n=0
for o in unreal.ObjectIterator():
    try:
        outer = unreal.get_outer(o)
    except Exception:
        continue
    if outer == bp:
        print("child", unreal.get_path_name(o), unreal.get_class(o).get_name() if hasattr(unreal.get_class(o),"get_name") else unreal.get_class(o))
        n+=1
print("nchildren", n)
# Also try EditorAssetLibrary.load_blueprint_class
for attr in dir(unreal.EditorAssetLibrary):
    if "blue" in attr.lower() or "class" in attr.lower():
        print("eal", attr)
# compile exists?
print("compile_fn", hasattr(unreal, "KismetSystemLibrary"))
# Try creating SCS node via AssetEditor
try:
    subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    print("aes", subsystem)
except Exception as e:
    print("aes_fail", e)
'''
remote = re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(8):
        time.sleep(0.6)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; break
    remote.open_command_connection(node_id)
    r=remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
    print("success", r.get("success"), "result", r.get("result"))
    for o in r.get("output") or []:
        print(o.get("output"))
finally:
    remote.stop()
