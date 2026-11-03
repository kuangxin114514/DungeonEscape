import unreal, json
out = {}
# EditorLevelLibrary APIs
ell = []
if hasattr(unreal, "EditorLevelLibrary"):
    ell = [n for n in dir(unreal.EditorLevelLibrary) if not n.startswith("_")]
out["ell"] = ell
# EditorFilterLibrary / EditorActorSubsystem
out["has_EAS"] = hasattr(unreal, "EditorActorSubsystem")
out["libs"] = sorted([n for n in dir(unreal) if n.startswith("Editor") or "Actor" in n and "Library" in n])
# Find preview BP_KayKitKnight actors and list ALL components
previews = []
for obj in unreal.ObjectIterator(unreal.load_class(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")):
    pn = obj.get_path_name()
    if "Transient" in pn or "World_" in pn:
        info = {"path": pn, "name": obj.get_name()}
        try:
            comps = obj.get_components_by_class(unreal.ActorComponent)
            info["comps"] = []
            for c in (comps or []):
                ci = {"n": c.get_name(), "c": c.get_class().get_name()}
                if c.get_class().get_name() == "StaticMeshComponent":
                    try: ci["mesh"] = str(c.get_editor_property("static_mesh"))
                    except Exception: pass
                    try: ci["socket"] = str(c.get_attach_socket_name()) if hasattr(c,"get_attach_socket_name") else None
                    except Exception: pass
                    try:
                        parent = c.get_attach_parent()
                        ci["parent"] = parent.get_name() if parent else None
                    except Exception as e:
                        ci["parent"] = str(e)[:40]
                info["comps"].append(ci)
        except Exception as e:
            info["err"] = str(e)
        previews.append(info)
out["previews_n"] = len(previews)
out["previews"] = previews[:8]

# Try EditorLevelLibrary.spawn_actor_from_class in current level - DANGEROUS for Map_Hub
# Instead spawn in editor world without saving
# Check get_editor_world
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    out["world"] = str(world)
    out["world_name"] = world.get_name() if world else None
except Exception as e:
    out["world_err"] = str(e)

# Can we use Actor.add_component_by_class on a PREVIEW actor and then somehow promote?
# Or use Blueprint create from selected after spawning in a NEW temp level without LoadMap of Map_Hub
# EditorLevelLibrary.new_level / new_blank_map?
out["ell_level"] = [n for n in ell if "level" in n.lower() or "map" in n.lower() or "spawn" in n.lower() or "actor" in n.lower() or "select" in n.lower() or "blueprint" in n.lower() or "component" in n.lower()]

# Try: use unreal.AssetToolsHelpers to create blueprint from class with factory, then
# inspect if we can use "add_component" on factory - no

# CRITICAL HACK: use export/import of DefaultProperties via Config
# Or use StaticMeshComponent socket attachment on SK asset itself via Sockets with preview
sk = unreal.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
skel = sk.skeleton
# Try add socket with property
out["skel_methods"] = [n for n in dir(skel) if not n.startswith("_") and ("socket" in n.lower() or "Socket" in n)]
out["sk_methods"] = [n for n in dir(sk) if not n.startswith("_") and ("socket" in n.lower() or "Socket" in n)]

# Read existing sockets via get_socket_by_name on mesh component CDO
gc = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C")
cdo = unreal.get_default_object(gc)
mesh = None
try:
    mesh = cdo.get_editor_property("mesh")
except Exception:
    mesh = getattr(cdo, "mesh", None)
out["mesh_comp"] = str(mesh)
if mesh:
    out["mesh_methods_sock"] = [n for n in dir(mesh) if "socket" in n.lower() or "Socket" in n or "attach" in n.lower()]
    for sname in ["handslot_r", "handslot_l", "hand_r", "hand_l", "weapon_r"]:
        try:
            t = mesh.get_socket_transform(sname, unreal.RelativeTransformSpace.RTS_COMPONENT)
            out["sock_"+sname] = str(t)
        except Exception as e:
            out["sock_"+sname] = str(e)[:80]
        try:
            exists = mesh.does_socket_exist(sname)
            out["exists_"+sname] = exists
        except Exception as e:
            out["exists_"+sname] = str(e)[:60]

open(r"C:/Users/86178/Documents/Unreal Projects/DungeonEscape/Docs/probe_scs12.json","w",encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
print("ell_level", out.get("ell_level"))
print("libs", out.get("libs")[:40])
print("previews", out.get("previews_n"))
if out.get("previews"):
    print("preview0 comps", json.dumps(out["previews"][0].get("comps"), indent=2)[:2000])
print("handslot_r", out.get("exists_handslot_r"), out.get("sock_handslot_r"))
print("handslot_l", out.get("exists_handslot_l"), out.get("sock_handslot_l"))
print("world", out.get("world_name"))