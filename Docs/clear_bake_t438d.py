# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r'C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Docs\\clear_bake_t438d.txt'
lines=[]
def L(s):
 lines.append(str(s)); print(s)
unreal.EditorLevelLibrary.load_level('/Game/Maps/Dungeon/Map_Dungeon2')
world=unreal.EditorLevelLibrary.get_editor_world()
L('world='+str(world.get_path_name() if world else None))
ws=world.get_world_settings()
ws.set_editor_property('force_no_precomputed_lighting', True)
L('ForceNo=True')
# invalidate lighting build data on world if property exists
try:
 unreal.SystemLibrary.execute_console_command(world, 'r.ForceDebugViewModes 0')
except Exception:
 pass
try:
 unreal.EditorLevelLibrary.save_current_level()
 L('saved')
except Exception as e:
 L('save ERR '+str(e))
built='/Game/Maps/Dungeon/Map_Dungeon2_BuiltData'
L('BuiltData exists='+str(unreal.EditorAssetLibrary.does_asset_exist(built)))
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
