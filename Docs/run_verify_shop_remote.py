# -*- coding: utf-8 -*-
import os, sys, time
ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
SCRIPT = os.path.join(ROOT, "Docs", "verify_shop_interact.py").replace("\\", "/")
LOG = os.path.join(ROOT, "Docs", "ue_shop_verify_remote.log")
REMOTE_MOD = r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
sys.path.insert(0, REMOTE_MOD)
import remote_execution as re

def main():
    remote = re.RemoteExecution()
    remote.start()
    try:
        node_id = None
        for i in range(20):
            time.sleep(0.7)
            nodes = remote.remote_nodes
            print("try", i, "n", len(nodes) if nodes else 0)
            if nodes:
                node_id = nodes[0]["node_id"]
                print("node", nodes[0].get("project_name"), node_id)
                break
        if not node_id:
            print("NO_NODES")
            open(LOG, "w", encoding="utf-8").write("NO_NODES\n")
            return 2
        remote.open_command_connection(node_id)
        stmt = "p=r'%s'; exec(compile(open(p,encoding='utf-8-sig').read(),p,'exec')); print('REMOTE_DONE')" % SCRIPT
        result = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
        print("RESULT", result)
        open(LOG, "w", encoding="utf-8").write(str(result) + "\n")
        return 0 if result and result.get("success") else 3
    except Exception as e:
        print("REMOTE_ERR", type(e).__name__, e)
        open(LOG, "w", encoding="utf-8").write("REMOTE_ERR %s %s\n" % (type(e).__name__, e))
        return 4
    finally:
        try:
            remote.stop()
        except Exception:
            pass

if __name__ == "__main__":
    sys.exit(main() or 0)
