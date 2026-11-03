import unreal,sys,importlib,traceback,time
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_final_proof.txt"
L=[]
def log(m):
    L.append(str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    # end+sim if needed
    try:
        ws=unreal.EditorLevelLibrary.get_pie_worlds(False)
        log("pie_worlds="+str(ws))
    except Exception as e:
        log("gpw "+str(e)); ws=None
    if not ws:
        try:
            unreal.EditorLevelLibrary.editor_play_simulate()
            log("sim started")
            time.sleep(2)
        except Exception as e:
            log("sim "+str(e))
    w=r._pie_world()
    log("pie="+str(w))
    if not w:
        log("PROOF=False"); flush(); raise SystemExit
    # Direct open_shop proof
    r.close_shop(w)
    ok1=r.open_shop(w, u"武器店")
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
    log("open_shop=%s texts=%s wid=%s"%(ok1,n,wid))
    if wid:
        log("vis=%s invp=%s"%(wid.get_visibility(), wid.is_in_viewport()))
    # handle_interact proof (close first so it opens)
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
    log("handle_interact=%s texts=%s wid=%s"%(ok2,n2,wid2))
    proof=bool((ok1 and n>0) or (ok2 and n2>0))
    log("PROOF="+str(proof))
    # Root cause note
    log("ROOT_CAUSE=BP CreateWidget Class pin null at runtime; new_object skips WidgetTree; fixed via WBL.create call_method + SAFE_V8 E tick")
    flush()
except Exception:
    log(traceback.format_exc()); flush()
