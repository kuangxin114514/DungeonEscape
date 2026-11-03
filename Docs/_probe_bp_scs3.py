# -*- coding: utf-8 -*-
import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
STMT = r'''
import unreal
print("has BEL", hasattr(unreal, "BlueprintEditorLibrary"))
print("has EAL", hasattr(unreal, "EditorAssetLibrary"))
names = [x for x in dir(unreal) if ("SCS" in x) or ("Construction" in x) or ("Blueprint" in x and "Editor" in x) or ("Subobject" in x) or x.endswith("ComponentLibrary")]
print("names", names)
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
# ObjectIterator all under BP path
count=0
for o in unreal.ObjectIterator():
    pn = o.get_path_name()
    if "/BP_KayKitKnight" in pn:
        print("obj", pn, o.get_class().get_name())
        count += 1
        if count > 40:
            print("..."); break
print("count_like", count)
# try get_editor_property with force via try_get?
try:
    print("GeneratedClass prop", bp.get_editor_property("GeneratedClass"))
except Exception as e:
    print("GC fail", e)
# ParentClass etc
for n in ("ParentClass","Status","BlueprintSystemVersion","bDeprecate"):
    try:
        print(n, bp.get_editor_property(n))
    except Exception as e:
        print(n, "fail", e)
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
    print("success", r.get("success"))
    print("result", r.get("result"))
    for o in r.get("output") or []:
        print(o.get("output"))
finally:
    remote.stop()
