import os, sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
remote = re.RemoteExecution(); remote.start()
try:
    node_id = None
    for i in range(20):
        time.sleep(0.35)
        if remote.remote_nodes:
            node_id = remote.remote_nodes[0]["node_id"]; break
    if not node_id:
        print("NO_NODES"); sys.exit(2)
    remote.open_command_connection(node_id)
    # Short script: inspect BP variables + try set CreateWidget via AssetRegistry / compile
    code = r'''
import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_bp_var.txt"
L=[]
def log(m):
    L.append(str(m)); unreal.log("BV:"+str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    bp=unreal.load_object(None,"/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight")
    log("bp="+str(bp)+" cls="+str(type(bp)))
    for p in ("new_variables","NewVariables","generated_class"):
        try:
            v=bp.get_editor_property(p); log("%s type=%s len=%s"%(p,type(v),len(v) if hasattr(v,'__len__') else 'na'))
            if hasattr(v,'__iter__') and not isinstance(v,str):
                for i,x in enumerate(list(v)[:20]):
                    log("  [%d]=%s"%(i,x))
                    for a in ("var_name","VarName","var_type","VarType","default_value","DefaultValue","pin_type","PinType","property_flags"):
                        try: log("    %s=%s"%(a,x.get_editor_property(a) if hasattr(x,'get_editor_property') else getattr(x,a,None)))
                        except Exception as e: pass
        except Exception as e:
            log("%s ERR %s"%(p,e))
    # Try BlueprintEditorLibrary
    for name in dir(unreal):
        if "Blueprint" in name and ("Editor" in name or "Library" in name):
            log("api "+name)
    # Compile BP
    try:
        unreal.KismetSystemLibrary.execute_console_command(None, "COMPILE /Game/Characters/Player/KayKit/BP_KayKitKnight")
        log("console compile sent")
    except Exception as e:
        log("console "+str(e))
    # Check if PIE still has open widget
    import sys
    sys.path.insert(0,r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
    import shop_interact_runtime as r
    log("OPEN="+str(r._OPEN_WIDGET[0]))
    w=r._pie_world(); log("pie="+str(w))
    # List all UserWidgets in PIE
    if w:
        n=0
        for o in unreal.ObjectIterator(unreal.UserWidget):
            try:
                pn=o.get_path_name()
            except Exception:
                continue
            if "UEDPIE" in pn or "WBP_Shop" in pn:
                log("UW "+pn+" vis="+str(getattr(o,'get_visibility',lambda:None)()))
                n+=1
        log("uw_count="+str(n))
    flush()
except Exception:
    log(traceback.format_exc()); flush()
'''
    open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_bp_var_tmp.py","w",encoding="utf-8").write(code)
    stmt = "exec(compile(open(r'C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_bp_var_tmp.py',encoding='utf-8').read(),'bpvar','exec'))"
    r = remote.run_command(stmt, unattended=True, exec_mode=re.MODE_EXEC_STATEMENT)
    print("success", r.get("success"))
    for o in (r.get("output") or [])[-30:]:
        t=(o.get("output") or "")
        if len(t)>300: t=t[:300]
        print(o.get("type"), t)
finally:
    remote.stop()
print("====")
print(open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_bp_var.txt",encoding="utf-8").read())
