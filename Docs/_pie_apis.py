
import unreal
LOG=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\fix_t206.txt'
lines=[]
def log(m): lines.append(str(m))
# list EditorLevelLibrary callables with play
ell = unreal.EditorLevelLibrary
names = [n for n in dir(ell) if 'play' in n.lower() or 'pie' in n.lower() or 'simulat' in n.lower() or 'session' in n.lower()]
log('ELL '+str(names))
# LevelEditorSubsystem?
for name in ['LevelEditorSubsystem','UnrealEditorSubsystem','EditorUtilityLibrary','GameplayStatics']:
    log(name+' '+str(hasattr(unreal, name)))
# try start play via console on editor world
w = unreal.EditorLevelLibrary.get_editor_world()
log('editor_world '+str(w))
# check current pie
try:
    log('pieF '+str(unreal.EditorLevelLibrary.get_pie_worlds(False)))
except Exception as e:
    log('pieF err '+str(e))
try:
    log('pieT '+str(unreal.EditorLevelLibrary.get_pie_worlds(True)))
except Exception as e:
    log('pieT err '+str(e))
# inspect play_simulate
try:
    log('play_sim doc '+str(getattr(ell.editor_play_simulate,'__doc__',None)))
except Exception as e:
    log(str(e))
# try LevelEditorPlaySettings
try:
    ps = unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    log('PlaySettings '+str(ps))
    for prop in ['play_net_mode','game_gets_mouse_control','use_mouse_for_touch','play_in_editor']:
        try:
            log(prop+'='+str(ps.get_editor_property(prop)))
        except Exception as e:
            log(prop+' err '+str(e))
except Exception as e:
    log('PS '+str(e))
open(LOG,'w',encoding='utf-8').write('\\n'.join(lines)+'\\n')
