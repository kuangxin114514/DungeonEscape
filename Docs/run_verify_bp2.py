import sys,time,traceback
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_verify_bp.txt"
# Keep script short to avoid JSON truncate; write file inside UE
code=r'''
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_verify_bp.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    assets=unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit", recursive=True, include_folder=False)
    L("count="+str(len(assets)))
    for a in assets:
        if "BP_" in a or "ABP_" in a or "BS_" in a or "GM_" in a:
            L(a)
    # ABP ascii tokens
    uasset=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitLocomotion.uasset"
    data=open(uasset,"rb").read()
    text="".join(chr(b) if 32<=b<127 else " " for b in data)
    for k in ["Speed","Direction","IsInAir","BlendSpace","GetVelocity","TryGetPawnOwner","VSize","BS_KayKit","StateMachine","Locomotion"]:
        L("ABP has %s: %s"%(k, k in text))
    # BP path candidates from disk
    flush()
except Exception as e:
    L("ERR "+repr(e))
    flush()
'''
open(OUT,"w").write("starting\n")
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.4)
        if remote.remote_nodes: break
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    # write code to file then exec to avoid escaping hell
    p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_tmp_verify_bp.py"
    open(p,"w",encoding="utf-8").write(code)
    r=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%p.replace("\\","/"), unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success") if r else None)
    print("result", str(r.get("result"))[:1000] if r else None)
finally:
    remote.stop()