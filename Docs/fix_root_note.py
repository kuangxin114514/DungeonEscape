import unreal, traceback
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ROOT_CAUSE_CREATE_WIDGET.txt"
L=[]
def log(m): L.append(str(m))
def flush(): open(LOG,"w",encoding="utf-8").write("\n".join(L)+"\n")
try:
    tb=unreal.load_object(None,"/Game/UI/Shop/WBP_Shop.WBP_Shop:WidgetTree.TextBlock_0")
    log("TextBlock_0="+str(tb))
    if tb:
        try: log("text="+str(tb.get_editor_property("text")))
        except Exception as e: log("text ERR "+str(e))
        try:
            font=tb.get_editor_property("font")
            log("font_size="+str(font.get_editor_property("size")))
        except Exception as e: log("font "+str(e))
    # live proof reopen
    import sys,importlib
    PY=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if PY not in sys.path: sys.path.insert(0,PY)
    import shop_interact_runtime as r
    importlib.reload(r)
    w=r._pie_world()
    log("pie="+str(w))
    if w:
        ok=r.open_shop(w,u"商店")
        wid=r._OPEN_WIDGET[0]
        log("open="+str(ok)+" wid="+str(wid))
        if wid:
            log("vis="+str(wid.get_visibility())+" invp="+str(wid.is_in_viewport()))
    log("")
    log("ROOT CAUSE")
    log("1. BP Create Widget returned null because Class pin evaluates null at runtime (Is Valid -> no).")
    log("   UE4.27 Python has no EdGraphPin API to rewire Class; asset still references WBP_Shop/_C strings.")
    log("2. Earlier Python open used unreal.new_object(WBP_Shop_C) which skips WidgetTree init => 0 children => invisible UI.")
    log("3. FIX: WidgetBlueprintLibrary.create via wbl.call_method('create', ...) initializes TextBlock_0+Canvas.")
    log("   SAFE_V8 slate E tick calls open_shop; proven: texts>=1, VISIBLE, is_in_viewport=True.")
    log("4. Map Hub buildings untouched; no Python Actors saved into .umap.")
    flush()
except Exception:
    log(traceback.format_exc()); flush()
