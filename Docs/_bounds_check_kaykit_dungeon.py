import unreal
p="/Game/Environments/KayKitDungeon/Meshes/Walls/SM_wall"
m=unreal.EditorAssetLibrary.load_asset(p)
bb=m.get_bounding_box()
sx=abs(bb.max.x-bb.min.x); sy=abs(bb.max.y-bb.min.y); sz=abs(bb.max.z-bb.min.z)
open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\import_kaykit_dungeon_bounds.txt","w").write("SM_wall bounds=(%.1f,%.1f,%.1f) path=%s\n"%(sx,sy,sz,p))
print("BOUNDS",sx,sy,sz)
