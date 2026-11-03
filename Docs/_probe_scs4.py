import unreal

scs = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C:SimpleConstructionScript_0")
print("scs", scs)
print("type", type(scs))
# dir filtered
attrs = [a for a in dir(scs) if not a.startswith("_")]
print("attrs", attrs)

for name in ["root_nodes", "all_nodes", "RootNodes", "AllNodes", "default_scene_root_node"]:
    try:
        v = scs.get_editor_property(name)
        print("prop", name, type(v), v)
        if hasattr(v, "__iter__") and not isinstance(v, str):
            for i, n in enumerate(v):
                print("  node", i, n, n.get_path_name() if n else None)
                if n:
                    nattrs = [a for a in dir(n) if not a.startswith("_")]
                    print("  node attrs sample", nattrs[:30])
                    for pn in ["component_class", "component_template", "parent_component_or_variable_name",
                               "parent_component_owner_class_name", "attach_to_name", "variable_name",
                               "child_nodes", "CategoryName", "InternalVariableName"]:
                        try:
                            print("   ", pn, n.get_editor_property(pn))
                        except Exception as e:
                            print("   ", pn, "ERR", str(e)[:80])
    except Exception as e:
        print("prop", name, "ERR", e)

# Try methods on scs
for m in ["create_node", "CreateNode", "add_node", "get_all_nodes", "get_root_nodes"]:
    print("has method", m, hasattr(scs, m))

# SCS_Node class
node_cls = unreal.find_object(None, "/Script/Engine.SCS_Node")
print("node_cls", node_cls)

# Try new_object
try:
    new_node = unreal.new_object(unreal.Class.cast(node_cls), scs, unreal.Name("SCS_Node_Sword"))
    print("new_node", new_node)
except Exception as e:
    print("new_object ERR", e)

# Try via string class name
try:
    # In UE4 python, sometimes: unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
    smc = unreal.load_class(None, "/Script/Engine.StaticMeshComponent")
    print("smc class", smc)
except Exception as e:
    print("smc", e)