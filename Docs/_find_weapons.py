import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for name in ["SM_KayKitSword","SM_KayKitShield","BP_KayKitSwordActor","BP_KayKitShieldActor"]:
    fa = unreal.ARFilter(class_names=["StaticMesh","Blueprint","BlueprintGeneratedClass"], package_paths=["/Game"], recursive_paths=True)
    # simpler search
    assets = ar.get_assets_by_package_name # skip
print("---")
for a in ar.get_all_assets():
    n = str(a.asset_name)
    if "KayKit" in n and ("Sword" in n or "Shield" in n or "Knight" in n):
        print(a.object_path)