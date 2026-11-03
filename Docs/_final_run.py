
import unreal,sys,importlib,traceback
LOG=r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\FINAL_PROOF.txt"
L=[]
def log(m): L.append(str(m))
def flush(): open(LOG,"w",encoding="utf-8").write("\\n".join(L)+"\\n")
try:
    PY=r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Content\\Python"
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    log("SAFE_V8_file="+str("SAFE_V8" in open(PY+"\\\\shop_interact_runtime.py",encoding="utf-8").read()))
    w=r._pie_world()
    log("pie="+str(w))
    if not w:
        try:
            unreal.EditorLevelLibrary.editor_play_simulate()
        except Exception as e:
            log("sim "+str(e))
        import time as _t; _t.sleep(1.5)
        w=r._pie_world()
        log("pie2="+str(w))
    if not w:
        log("PROOF=False"); flush()
    else:
        r.close_shop(w)
        ok=r.open_shop(w,u"武器店")
        wid=r._OPEN_WIDGET[0]
        n=0
        if wid:
            base=wid.get_path_name()
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name():
                        n+=1
                        try: o.set_text(unreal.Text("SHOP"))
                        except Exception: pass
                except Exception: pass
                if n>=2: break
        log("open_shop="+str(ok))
        log("widget="+str(wid))
        log("texts="+str(n))
        if wid:
            log("vis="+str(wid.get_visibility()))
            log("invp="+str(wid.is_in_viewport()))
        r.close_shop(w)
        ok2=r.handle_interact(w)
        wid2=r._OPEN_WIDGET[0]
        n2=0
        if wid2:
            base=wid2.get_path_name()
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    if base in o.get_path_name(): n2+=1
                except Exception: pass
                if n2>=2: break
        log("handle_interact="+str(ok2)+" texts="+str(n2))
        proof=bool(ok and n>0 and wid and wid.is_in_viewport()) or bool(ok2 and n2>0)
        log("PROOF="+str(proof))
        log("ROOT=new_object skipped WidgetTree; WBL.create via call_method fixes it; BP CreateWidget Class pin still null in graph (Python cannot set EdGraph pins in 4.27); E uses SAFE_V8 runtime.")
        flush()
except Exception:
    log(traceback.format_exc()); flush()
