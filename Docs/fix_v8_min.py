# minimal verify — no heavy ObjectIterator logging
import unreal, sys, importlib, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_v8_min.txt"
L=[]
def log(m):
    L.append(str(m))
def flush():
    open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0, PY)
    # quick check create path in file
    src=open(PY+r"\shop_interact_runtime.py",encoding="utf-8").read()
    log("has_call_method="+str("call_method" in src))
    log("has_SAFE_V8="+str("SAFE_V8" in src))
    import shop_interact_runtime as r
    importlib.reload(r)
    w=r._pie_world()
    log("pie="+str(w is not None))
    if w:
        r.close_shop(w)
        ok=r.open_shop(w, u"武器店")
        log("open_shop="+str(ok))
        wid=r._OPEN_WIDGET[0]
        log("widget="+str(wid))
        if wid:
            log("vis="+str(wid.get_visibility()))
            log("invp="+str(wid.is_in_viewport()))
            # light child check: only TextBlock class filter, break early
            base=wid.get_path_name()
            n=0
            for o in unreal.ObjectIterator(unreal.TextBlock):
                try:
                    pn=o.get_path_name()
                except Exception:
                    continue
                if base in pn:
                    n+=1
                    if n>=3: break
            log("text_found="+str(n))
            log("PROOF="+str(ok and n>0 and wid.is_in_viewport()))
        else:
            log("PROOF=False")
    else:
        log("NO_PIE PROOF=False")
except Exception:
    log(traceback.format_exc())
flush()
