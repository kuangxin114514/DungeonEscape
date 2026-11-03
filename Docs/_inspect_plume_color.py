import bpy, bmesh, json
from mathutils import Color
GLB = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb"
TEX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Textures\knight_texture.png"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_knight_plume_color.json"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
img = bpy.data.images.load(TEX)
w,h = img.size
px = list(img.pixels)  # rgba float

def sample(u,v):
    u = u % 1.0; v = v % 1.0
    x = min(w-1, max(0, int(u * w)))
    y = min(h-1, max(0, int(v * h)))
    i = (y*w + x)*4
    return px[i], px[i+1], px[i+2]

def analyze(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    # connected components of verts
    seen=set(); islands=[]
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; comp=set()
        while stack:
            cur=stack.pop()
            if cur.index in seen: continue
            seen.add(cur.index); comp.add(cur.index)
            for e in cur.link_edges:
                ov=e.other_vert(cur)
                if ov.index not in seen: stack.append(ov)
        islands.append(comp)
    mw=obj.matrix_world
    rows=[]
    for ii,comp in enumerate(islands):
        # faces fully in island
        cols=[]; zs=[]; ys=[]
        for f in bm.faces:
            if not all(v.index in comp for v in f.verts):
                continue
            c = mw @ f.calc_center_median(); zs.append(c.z); ys.append(c.y)
            if uv_layer:
                for loop in f.loops:
                    u,v = loop[uv_layer].uv
                    cols.append(sample(u,v))
        if not cols:
            continue
        r=sum(c[0] for c in cols)/len(cols); g=sum(c[1] for c in cols)/len(cols); b=sum(c[2] for c in cols)/len(cols)
        rows.append({"island":ii,"verts":len(comp),"faces_sampled":len(cols),"avg_rgb":[r,g,b],
                     "redness": r - (g+b)/2, "zmin":min(zs),"zmax":max(zs),"ymin":min(ys),"ymax":max(ys),
                     "zavg":sum(zs)/len(zs),"yavg":sum(ys)/len(ys)})
    rows.sort(key=lambda x: -x["redness"])
    bm.free(); return rows

head=bpy.data.objects["Knight_Head"]
rows=analyze(head)
json.dump(rows, open(OUT,"w",encoding="utf-8"), indent=2)
print("Knight_Head islands by redness:")
for r in rows:
    print("isl", r["island"], "verts", r["verts"], "rgb", [round(x,3) for x in r["avg_rgb"]], "redness", round(r["redness"],3),
          "z", round(r["zmin"],3), round(r["zmax"],3), "yavg", round(r["yavg"],3))
