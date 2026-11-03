import unreal
LOG=r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/_weapon_paths.txt"
out=[]
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_all_assets():
    n = str(a.asset_name)
    p = str(a.object_path)
    if "Sword" in n or "Shield" in n or "sword" in n or "shield" in n:
        out.append("%s | %s | %s" % (a.asset_class, n, p))
    if "KayKit" in n and ("Weapon" in p or "SM_" in n):
        out.append("KAY %s | %s | %s" % (a.asset_class, n, p))
open(LOG,"w",encoding="utf-8").write("\n".join(out))
print("wrote", len(out))