import sys,time
sys.path.insert(0,r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
code=r'''
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\anim_abp_compile.txt"
lines=[]
def L(m):
    lines.append(str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
try:
    ABP="/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion"
    abp=unreal.EditorAssetLibrary.load_asset(ABP)
    # Blueprint status
    for p in ["status","Status","blueprint_system_version","is_up_to_date","bBeingCompiled"]:
        try:
            L("%s=%s"%(p, abp.get_editor_property(p)))
        except Exception as e:
            L("%s ERR"%p)
    # Try BlueprintEditorLibrary
    L("has BlueprintEditorLibrary=%s"%hasattr(unreal,"BlueprintEditorLibrary"))
    if hasattr(unreal,"BlueprintEditorLibrary"):
        BEL=unreal.BlueprintEditorLibrary
        L("BEL methods=%s"%[n for n in dir(BEL) if not n.startswith("_")])
        try:
            L("compile_status=%s"%BEL.get_blueprint_compile_status(abp) if hasattr(BEL,"get_blueprint_compile_status") else "n/a")
        except Exception as e:
            L("compile_status ERR %s"%e)
        try:
            if hasattr(BEL,"compile_blueprint"):
                BEL.compile_blueprint(abp); L("compiled")
        except Exception as e:
            L("compile ERR %s"%e)
        try:
            if hasattr(BEL,"add_member_variable"):
                L("has add_member_variable")
        except Exception:
            pass
    # Enumerate generated class properties containing air/speed/bool
    abp_c=unreal.EditorAssetLibrary.load_blueprint_class(ABP)
    cdo=unreal.get_default_object(abp_c)
    # Use dir on cdo for custom props - may not show UPROPERTY
    # Try get_editor_property for common TP names
    candidates=["Speed","Direction","YawDelta","IsInAir","IsFalling","bIsInAir","Pitch","Roll","CharacterSpeed","GroundSpeed","ShouldMove","Offset","BaseAimRotation"]
    for c in candidates:
        try:
            L("prop %s=%s"%(c,cdo.get_editor_property(c)))
        except Exception:
            pass
    # Check ASCII for Variable names near NewVariables
    data=open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Characters\Player\KayKit\Animations\ABP_KayKitLocomotion.uasset","rb").read()
    text="".join(chr(b) if 32<=b<127 else "|"| for b in data)
    # find IsInAir contexts
    idx=0
    n=0
    while n<5:
        i=text.find("IsInAir", idx)
        if i<0: break
        L("IsInAir ctx: %s"%repr(text[max(0,i-30):i+40]))
        idx=i+7; n+=1
    idx=0; n=0
    while n<5:
        i=text.find("Speed", idx)
        if i<0: break
        L("Speed ctx: %s"%repr(text[max(0,i-30):i+40]))
        idx=i+5; n+=1
    # Compare with working ThirdPerson AnimBP if present
    tp_candidates=[
      "/Game/Mannequin/Animations/ThirdPerson_AnimBP",
      "/Game/ThirdPersonBP/Characters/ThirdPerson_AnimBP",
      "/Game/ThirdPerson/Characters/ThirdPerson_AnimBP",
    ]
    for t in tp_candidates:
        if unreal.EditorAssetLibrary.does_asset_exist(t):
            L("found TP ABP %s"%t)
            tc=unreal.EditorAssetLibrary.load_blueprint_class(t)
            if tc:
                td=unreal.get_default_object(tc)
                for c in ["Speed","Direction","IsInAir","bIsInAir"]:
                    try: L("  TP.%s=%s"%(c,td.get_editor_property(c)))
                    except Exception: L("  TP.%s missing"%c)
    # list mannequin anims folder
    for folder in ["/Game/Mannequin","/Game/ThirdPersonBP","/Game/ThirdPerson"]:
        if unreal.EditorAssetLibrary.does_directory_exist(folder):
            assets=unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False)
            abps=[a for a in assets if "AnimBP" in a or "ABP_" in a]
            L("%s abps=%s"%(folder, abps[:20]))
    flush()
except Exception as e:
    import traceback
    L("ERR "+traceback.format_exc())
    flush()
'''
# fix typo in code - the "| for b" is wrong
code=code.replace('chr(b) if 32<=b<127 else "|"| for b in data', 'chr(b) if 32<=b<127 else "|" for b in data')
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_tmp_abp_compile.py"
open(p,"w",encoding="utf-8").write(code)
remote=re.RemoteExecution(); remote.start()
try:
    for i in range(20):
        time.sleep(0.4)
        if remote.remote_nodes: break
    remote.open_command_connection(remote.remote_nodes[0]["node_id"])
    r=remote.run_command("exec(open(r'%s',encoding='utf-8').read())"%p.replace("\\","/"), unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success") if r else None)
    print("result", str(r.get("result"))[:1500] if r else None)
finally:
    remote.stop()