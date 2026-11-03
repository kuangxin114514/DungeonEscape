import unreal

paths = [
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:SimpleConstructionScript",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight.SimpleConstructionScript",
 "/Game/Characters/Player/KayKit/BP_KayKitKnight:SimpleConstructionScript",
]
for p in paths:
    o = unreal.load_object(None, p)
    print("load", p, "->", o)

bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
# try find objects with outer = bp
try:
    # iterate package
    pkg = bp.get_outer()
    print("outer", pkg, type(pkg))
    # get package name
    pname = bp.get_path_name()
    print("path", pname)
except Exception as e:
    print("outer err", e)

# try unreal.EditorAssetLibrary.find_asset_data
ad = unreal.EditorAssetLibrary.find_asset_data("/Game/Characters/Player/KayKit/BP_KayKitKnight")
print("asset_data", ad)
print("asset_class", ad.asset_class)

# Generated class path
gc_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C"
gc = unreal.load_object(None, gc_path)
print("gc", gc)
if gc:
    cdo = unreal.get_default_object(gc)
    print("cdo", cdo)
    try:
        # get all component templates from CDO
        for attr in ["root_component", "mesh", "capsule_component"]:
            try:
                print(attr, cdo.get_editor_property(attr) if hasattr(cdo,"get_editor_property") else getattr(cdo, attr, None))
            except Exception as e:
                print(attr, e)
        comps = cdo.get_components_by_class(unreal.SceneComponent)
        print("scene comps", len(comps))
        for c in comps:
            print(" ", c.get_name(), c.get_class().get_name())
    except Exception as e:
        print("comps err", e)

# Try new_object SCS_Node with outer
scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:SimpleConstructionScript")
print("scs direct", scs)
if scs is None:
    # enumerate subobjects via Package
    try:
        import unreal as u
        # AssetRegistry
        ar = unreal.AssetRegistryHelpers.get_asset_registry()
        print("ar ok")
    except Exception as e:
        print(e)

# Can we use ObjectIterator?
try:
    for obj in unreal.ObjectIterator(unreal.Class.cast(unreal.find_object(None, "/Script/Engine.SimpleConstructionScript"))):
        pn = obj.get_path_name()
        if "KayKitKnight" in pn:
            print("ITER SCS", pn, obj)
except Exception as e:
    print("iter err", e)

try:
    cls = unreal.find_object(None, "/Script/Engine.SCS_Node")
    for obj in unreal.ObjectIterator(unreal.Class.cast(cls)):
        pn = obj.get_path_name()
        if "KayKitKnight" in pn:
            print("ITER NODE", pn)
except Exception as e:
    print("iter node err", e)