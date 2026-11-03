# -*- coding: utf-8 -*-
import os, sys, time
REMOTE_MOD = r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
sys.path.insert(0, REMOTE_MOD)
import remote_execution as re

STMT = r'''
import unreal
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
print("bp", bp, type(bp), bp.get_class().get_name() if bp else None)
print("dir_scs", [x for x in dir(bp) if "scs" in x.lower() or "simple" in x.lower() or "construct" in x.lower()])
for name in ("simple_construction_script","SimpleConstructionScript","generated_class"):
    try:
        v = bp.get_editor_property(name)
        print("prop", name, v, type(v))
    except Exception as e:
        print("prop_fail", name, e)
try:
    print("attr", bp.simple_construction_script)
except Exception as e:
    print("attr_fail", e)
try:
    gc = bp.generated_class()
    print("gen", gc)
except Exception as e:
    print("gen_fail", e)
# try cast
try:
    b2 = unreal.Blueprint.cast(bp)
    print("cast", b2)
    if b2:
        print("cast_scs", b2.get_editor_property("simple_construction_script"))
except Exception as e:
    print("cast_fail", e)
'''

def main():
    remote = re.RemoteExecution()
    remote.start()
    try:
        node_id = None
        for i in range(8):
            time.sleep(0.7)
            nodes = remote.remote_nodes
            if nodes:
                node_id = nodes[0]["node_id"]; break
        if not node_id:
            print("NO_NODES"); return 2
        remote.open_command_connection(node_id)
        # ExecuteFile with short probe code (multi-statement)
        result = remote.run_command(STMT, unattended=True, exec_mode=re.MODE_EXEC_FILE)
        print("RESULT", result)
        return 0 if result and result.get("success") else 3
    except Exception as e:
        print("ERR", e); return 4
    finally:
        try: remote.stop()
        except Exception: pass

if __name__ == "__main__":
    sys.exit(main() or 0)
