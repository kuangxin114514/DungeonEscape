import unreal, sys, importlib, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_e_proof.txt"
L=[]
def log(m):
    L.append(str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    src=open(PY+r"\shop_interact_runtime.py",encoding="utf-8").read()
    log("has_call_method="+str("call_method" in src))
    log("has_paint="+str("_paint_shop_texts" in src))
    log("has_get_pie="+str("get_pie_worlds" in src))
    log("SAFE_V8="+str("SAFE_V8" in src))
    # show _pie_world snippet
    i=src.find("def _pie_world")
    log("pie_world_snip="+repr(src[i:i+280]))
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    w=r._pie_world()
    log("pie="+str(w))
    if not w:
        log("PROOF_E=False no pie"); flush(); raise SystemExit
    # close then handle_interact (same as pressing E)
    r.close_shop(w)
    ok=r.handle_interact(w)
    log("handle_interact="+str(ok))
    wid=r._OPEN_WIDGET[0]
    log("widget="+str(wid))
    n=0
    if wid:
        base=wid.get_path_name()
        for o in unreal.ObjectIterator(unreal.TextBlock):
            try:
                pn=o.get_path_name()
            except Exception:
                continue
            if base in pn:
                n+=1
                try:
                    o.set_text(unreal.Text("SHOP"))
                except Exception:
                    pass
            if n>=2: break
        log("texts=%d vis=%s invp=%s"%(n,wid.get_visibility(),wid.is_in_viewport()))
    log("PROOF_E="+str(bool(ok and wid and n>0 and wid.is_in_viewport())))
    # BP CreateWidget node presence
    n_cw=0
    for o in unreal.ObjectIterator():
        try:
            pn=o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight" in pn and "K2Node_CreateWidget" in pn:
            n_cw+=1
            log("CW "+pn)
        if n_cw>5: break
    log("createwidget_nodes="+str(n_cw))
    flush()
except Exception:
    log(traceback.format_exc()); flush()
