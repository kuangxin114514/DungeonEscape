import unreal, re
GAMEFLOW="/Game/Core/GameFlow"
MAPS="/Game/Maps/MainMenu"
MENU="/Game/Maps/MainMenu/Map_MainMenu"
HUB="/Game/Maps/Hub/Map_Hub"
INI=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Config\DefaultEngine.ini"

def ensure(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def create_bp(parent, path, name):
    full=path+"/"+name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    f=unreal.BlueprintFactory(); f.set_editor_property("ParentClass", parent)
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, None, f)
    if bp: unreal.EditorAssetLibrary.save_loaded_asset(bp)
    return unreal.EditorAssetLibrary.load_asset(full)

ensure(MAPS); ensure(GAMEFLOW)
gm=create_bp(unreal.GameModeBase.static_class(), GAMEFLOW, "GM_MainMenu")
try:
    cdo=unreal.get_default_object(gm.generated_class())
    cdo.set_editor_property("default_pawn_class", unreal.SpectatorPawn.static_class())
    unreal.EditorAssetLibrary.save_loaded_asset(gm)
except Exception as e:
    unreal.log_warning(str(e))

if not unreal.EditorAssetLibrary.does_asset_exist(MENU):
    unreal.EditorAssetLibrary.duplicate_asset("Map_MainMenu", MAPS, HUB)

unreal.EditorLoadingAndSavingUtils.load_map(MENU)
for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
    cls=a.get_class().get_name(); lab=a.get_actor_label()
    keep = any(k in cls for k in ("Light","Sky","Fog","Atmosphere","Reflection","PlayerStart","WorldSettings","Brush","PhysicsVolume","Landscape"))
    keep = keep or lab in ("Floor","HubGround_Plane","Menu_Camera","Menu_Title3D")
    if lab.startswith("Hub") or "ThirdPerson" in lab or "Character" in lab:
        keep=False
    if (not keep) and ("WorldSettings" not in cls) and ("Brush" not in cls) and ("PhysicsVolume" not in cls):
        try: unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception: pass

# PlayerStart
has=False
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if "PlayerStart" in a.get_class().get_name():
        has=True; a.set_actor_location(unreal.Vector(0,0,100), False, True)
if not has:
    ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0,0,100), unreal.Rotator())
    if ps: ps.set_actor_label("Menu_PlayerStart")

cam=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-500,0,200), unreal.Rotator(0,0,0))
if cam: cam.set_actor_label("Menu_Camera")

# 3D title fallback
try:
    tr=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(200,0,220), unreal.Rotator(0,180,0))
    if tr:
        tr.set_actor_label("Menu_Title3D")
        c=tr.get_component_by_class(unreal.TextRenderComponent)
        if c:
            c.set_text("地牢逃脱")
            c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            try: c.set_world_size(100)
            except Exception: pass
    tr2=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(200,0,140), unreal.Rotator(0,180,0))
    if tr2:
        tr2.set_actor_label("Menu_Hint3D")
        c=tr2.get_component_by_class(unreal.TextRenderComponent)
        if c:
            c.set_text("主菜单加载中…")
            c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            try: c.set_world_size(28)
            except Exception: pass
except Exception as e:
    unreal.log_warning("text "+str(e))

try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "WorldSettings" in a.get_class().get_name():
            a.set_editor_property("default_game_mode", gm.generated_class())
except Exception as e:
    unreal.log_warning("gm "+str(e))

unreal.EditorLevelLibrary.save_current_level()

with open(INI,"r",encoding="utf-8",errors="ignore") as f: text=f.read()
text=re.sub(r"EditorStartupMap=.*","EditorStartupMap=/Game/Maps/MainMenu/Map_MainMenu",text)
text=re.sub(r"GameDefaultMap=.*","GameDefaultMap=/Game/Maps/MainMenu/Map_MainMenu",text)
with open(INI,"w",encoding="utf-8") as f: f.write(text)
unreal.log("MENU MAP ONLY DONE")
