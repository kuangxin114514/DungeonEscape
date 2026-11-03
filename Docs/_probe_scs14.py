import unreal, json, traceback
out = {"log": []}
def log(m):
    out["log"].append(str(m)); print(m)

def find_scs(asset_path):
    # Try common load_object paths
    name = asset_path.rstrip("/").split("/")[-1]
    candidates = [
        asset_path + "." + name + "_C:SimpleConstructionScript_0",
        asset_path + "." + name + ":SimpleConstructionScript_0",
        asset_path + ".SimpleConstructionScript_0",
    ]
    for c in candidates:
        obj = unreal.load_object(None, c)
        if obj:
            log("found scs at %s" % c)
            return obj
    # Iterate SCS class
    scs_cls = unreal.load_class(None, "/Script/Engine.SimpleConstructionScript")
    for obj in unreal.ObjectIterator(scs_cls):
        pn = unreal.Object.get_path_name(obj)
        if name in pn:
            log("iter scs %s" % pn)
            return obj
    return None

def list_outer_objects(asset_path, keywords):
    name = asset_path.rstrip("/").split("/")[-1]
    results = []
    # Use AssetRegistry to get package, then find objects
    pkg = unreal.load_package(asset_path)
    log("pkg %s" % pkg)
    # Iterate all StaticMeshComponent
    for cls_path in ["/Script/Engine.StaticMeshComponent", "/Script/Engine.SCS_Node", "/Script/Engine.SimpleConstructionScript", "/Script/Engine.ChildActorComponent"]:
        cls = unreal.load_class(None, cls_path)
        if not cls:
            continue
        for obj in unreal.ObjectIterator(cls):
            pn = unreal.Object.get_path_name(obj)
            if name in pn:
                results.append((pn, unreal.Object.get_class(obj).get_name()))
    return results

for path in [
    "/Game/Characters/Player/KayKit/Weapons/BP_KayKitSwordActor",
    "/Game/Characters/Player/KayKit/Weapons/BP_KayKitShieldActor",
    "/Game/Characters/Player/KayKit/BP_KayKitKnight",
]:
    log("=== " + path)
    bp = unreal.load_asset(path)
    log("bp=%s exists=%s" % (bp, unreal.EditorAssetLibrary.does_asset_exist(path)))
    if bp:
        for prop in dir(bp):
            if "scs" in prop.lower() or "construction" in prop.lower() or "parent" in prop.lower():
                log("  bpattr %s" % prop)
        try:
            log("  parent_class=%s" % bp.get_editor_property("parent_class"))
        except Exception as e:
            log("  parent_class ERR %s" % e)
    scs = find_scs(path)
    log("scs=%s" % scs)
    objs = list_outer_objects(path, None)
    for pn, cn in objs[:40]:
        log("  %s [%s]" % (pn, cn))

# Create StaticMeshActor-parented BP
factory = unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.StaticMeshActor)
tools = unreal.AssetToolsHelpers.get_asset_tools()
dest_path = "/Game/Characters/Player/KayKit/Weapons"
dest_name = "BP_ProbeStaticMeshParent"
full = dest_path + "/" + dest_name
if unreal.EditorAssetLibrary.does_asset_exist(full):
    unreal.EditorAssetLibrary.delete_asset(full)
new_bp = tools.create_asset(dest_name, dest_path, None, factory)
log("created %s type=%s" % (new_bp, type(new_bp)))
if new_bp:
    unreal.EditorAssetLibrary.save_asset(full)
    scs = find_scs(full)
    log("probe scs=%s" % scs)
    objs = list_outer_objects(full, None)
    for pn, cn in objs:
        log("  P %s [%s]" % (pn, cn))
    # Set static mesh on any SMC template
    sword = unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword")
    for pn, cn in objs:
        if cn == "StaticMeshComponent":
            obj = unreal.load_object(None, pn)
            if obj:
                try:
                    obj.set_editor_property("static_mesh", sword)
                    log("set mesh on %s" % pn)
                except Exception as e:
                    log("setmesh ERR %s" % e)
    # Reparent to KayKitKnight
    parent_cls = unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
    log("parent_cls %s" % parent_cls)
    try:
        new_bp.set_editor_property("parent_class", parent_cls)
        log("reparent OK")
    except Exception as e:
        log("reparent ERR %s" % e)
    # Also try parent_class = the Blueprint's generated class via load
    unreal.EditorAssetLibrary.save_asset(full)
    # compile via load class
    gen = unreal.load_class(None, full + "." + dest_name + "_C")
    log("gen after reparent %s" % gen)
    if gen:
        cdo = unreal.get_default_object(gen)
        try:
            comps = cdo.get_components_by_class(unreal.ActorComponent)
            for c in (comps or []):
                log("CDO %s %s" % (c.get_name(), c.get_class().get_name()))
        except Exception as e:
            log("cdo comps ERR %s" % e)

open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs14.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
log("DONE")