import bpy, json, os
GLB = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_knight_mesh_inspect.json"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
rows = []
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    bb = [list(v) for v in o.bound_box]
    xs=[v[0] for v in bb]; ys=[v[1] for v in bb]; zs=[v[2] for v in bb]
    parent = o.parent.name if o.parent else None
    pbone = o.parent_bone if o.parent_type=="BONE" else None
    mats=[(s.material.name if s.material else None) for s in o.material_slots]
    # sample vertex colors / avg world z
    mw=o.matrix_world
    coords=[mw @ v.co for v in o.data.vertices]
    if coords:
        avg=(sum(c.x for c in coords)/len(coords), sum(c.y for c in coords)/len(coords), sum(c.z for c in coords)/len(coords))
        mx=max(c.z for c in coords); mn=min(c.z for c in coords)
    else:
        avg=(0,0,0); mx=mn=0
    rows.append({"name":o.name,"verts":len(o.data.vertices),"parent":parent,"parent_type":o.parent_type,"parent_bone":pbone,"mats":mats,"avg":avg,"zmin":mn,"zmax":mx,"bbox_min":[min(xs),min(ys),min(zs)],"bbox_max":[max(xs),max(ys),max(zs)]})
rows.sort(key=lambda r:r["name"])
json.dump(rows, open(OUT,"w",encoding="utf-8"), indent=2)
print("WROTE", OUT, "count", len(rows))
for r in rows:
    print(r["name"], "verts", r["verts"], "parent", r["parent"], r["parent_bone"], "z", round(r["zmin"],3), round(r["zmax"],3), "avg", [round(x,3) for x in r["avg"]])
