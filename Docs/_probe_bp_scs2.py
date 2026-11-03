# -*- coding: utf-8 -*-
import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
paths = []
# try find/load SCS as subobject
for name in ("SimpleConstructionScript", "SCS", "SimpleConstructionScript_0"):
    for fn in (unreal.find_object, unreal.load_object):
        try:
            o = fn(bp, name)
            print("found", fn.__name__, name, o, o.get_class().get_name() if o else None)
        except Exception as e:
            print("fail", fn.__name__, name, e)
# iterate outer children via ObjectIterator
try:
    for o in unreal.ObjectIterator(unreal.SimpleConstructionScript):
        if o.get_outer() == bp or str(o.get_path_name()).startswith(bp.get_path_name()):
            print("iter_scs", o.get_path_name(), o)
except Exception as e:
    print("iter_fail", e)
# BlueprintEditorLibrary methods
print("bel", [x for x in dir(unreal.BlueprintEditorLibrary) if "comp" in x.lower() or "scs" in x.lower() or "socket" in x.lower() or "add" in x.lower()])
# Generated class via load_class
cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
print("cls", cls)
if cls:
    cdo = unreal.get_default_object(cls)
    print("cdo", cdo)
    # list components on CDO
    try:
        comps = cdo.get_components_by_class(unreal.ActorComponent)
        print("comps", [(c.get_name(), c.get_class().get_name()) for c in comps])
    except Exception as e:
        print("comps_fail", e)
# try KismetSystemLibrary get_default
'''
remote = re.RemoteExecution(); remote.start()
try:
    node_id=None
    for i in range(8):
        time.sleep(0.6)
        if remote.remote_nodes:
            node_id=remote.remote_nodes[0]["node_id"]; break
    remote.open_command_connection(node_id)
    print(remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE))
finally:
    remote.stop()
