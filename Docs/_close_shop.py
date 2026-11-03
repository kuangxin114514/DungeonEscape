
import unreal, sys
PYDIR=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Content\\Python'
LOG=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\fix_t206.txt'
if PYDIR not in sys.path: sys.path.insert(0, PYDIR)
import shop_interact_runtime as r
ws = unreal.EditorLevelLibrary.get_pie_worlds(False) or []
world = ws[0] if ws else None
if world:
    r.close_shop(world)
open(LOG,'w',encoding='utf-8').write('closed open=%s tick=%s gen=%s\\n' % (r._OPEN_WIDGET[0] is not None, r._TICK[0] is not None, r._MY_GEN[0]))
