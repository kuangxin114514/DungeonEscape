import bpy, json, bmesh
from collections import defaultdict
GLB = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_knight_head_islands.json"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

def islands(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table()
    seen=set(); groups=[]
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; comp=[]
        while stack:
            cur=stack.pop()
            if cur.index in seen: continue
            seen.add(cur.index); comp.append(cur)
            for e in cur.link_edges:
                ov=e.other_vert(cur)
                if ov.index not in seen: stack.append(ov)
        groups.append(comp)
    out=[]
    mw=obj.matrix_world
    for g in groups:
        coords=[mw @ v.co for v in g]
        xs=[c.x for c in coords]; ys=[c.y for c in coords]; zs=[c.z for c in coords]
        out.append({"verts":len(g),"xmin":min(xs),"xmax":max(xs),"ymin":min(ys),"ymax":max(ys),"zmin":min(zs),"zmax":max(zs),
                    "avg":[sum(xs)/len(xs),sum(ys)/len(ys),sum(zs)/len(zs)]})
    bm.free(); return out

result={}
for name in ["Knight_Head","Knight_Helmet","Knight_Cape","Knight_Body"]:
    o=bpy.data.objects.get(name)
    if not o: continue
    isl=islands(o)
    isl.sort(key=lambda x: -x["verts"])
    result[name]=isl
    print("===", name, "islands", len(isl))
    for i,g in enumerate(isl):
        print(i, "verts", g["verts"], "z", round(g["zmin"],3), round(g["zmax"],3), "y", round(g["ymin"],3), round(g["ymax"],3), "avg", [round(v,3) for v in g["avg"]])

# also compare helmet-only tall verts vs head
helmet=bpy.data.objects["Knight_Helmet"]
head=bpy.data.objects["Knight_Head"]
# UV / material - sample face centers high up on head
bm=bmesh.new(); bm.from_mesh(head.data); bm.faces.ensure_lookup_table()
mw=head.matrix_world
tall=[]
for f in bm.faces:
    c=mw @ f.calc_center_median()
    if c.z > 1.85:
        tall.append({"z":c.z,"y":c.y,"x":c.x,"i":f.index})
tall.sort(key=lambda t:-t["z"])
result["head_tall_faces_zgt_1.85"]=tall[:40]
print("tall faces", len(tall))
bm.free()
json.dump(result, open(OUT,"w",encoding="utf-8"), indent=2)
print("WROTE", OUT)
