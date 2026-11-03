
import unreal, sys
PYDIR=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Content\\Python'
LOG=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\fix_t206.txt'
if PYDIR not in sys.path: sys.path.insert(0, PYDIR)
import shop_interact_runtime as r
ws = unreal.EditorLevelLibrary.get_pie_worlds(False) or unreal.EditorLevelLibrary.get_pie_worlds(True) or []
world = ws[0] if ws else None
wid = r._OPEN_WIDGET[0]
invp=False; texts=0
if wid is not None:
    try: invp=bool(wid.is_in_viewport())
    except Exception: pass
    base=wid.get_path_name()
    for o in unreal.ObjectIterator(unreal.TextBlock):
        try:
            if base in o.get_path_name(): texts += 1
        except Exception: pass
open(LOG,'w',encoding='utf-8').write('after_E open=%s invp=%s texts=%s wid=%s\\n' % (wid is not None, invp, texts, wid))
unreal.log('T206_AFTER_E open=%s invp=%s texts=%s' % (wid is not None, invp, texts))
