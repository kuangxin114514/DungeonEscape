import bpy, json, os
bpy.ops.wm.read_factory_settings(use_empty=True)
path = r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb'
bpy.ops.import_scene.gltf(filepath=path)
objs = []
for o in bpy.data.objects:
    info = {'name': o.name, 'type': o.type, 'loc': list(o.location), 'dims': list(o.dimensions), 'parent': o.parent.name if o.parent else None}
    if o.type == 'MESH':
        info['verts'] = len(o.data.vertices)
        info['groups'] = [g.name for g in o.vertex_groups]
        info['mat'] = [m.name for m in o.data.materials if m]
    if o.type == 'ARMATURE':
        info['bones'] = [b.name for b in o.data.bones][:40]
        info['nbones'] = len(o.data.bones)
    objs.append(info)
arms = [o for o in bpy.data.objects if o.type=='ARMATURE']
meshes = [o for o in bpy.data.objects if o.type=='MESH']
# bounds of all meshes
mn=[1e9]*3; mx=[-1e9]*3
for o in meshes:
    for corner in o.bound_box:
        w = o.matrix_world @ __import__('mathutils').Vector(corner)
        for i in range(3):
            mn[i]=min(mn[i], w[i]); mx[i]=max(mx[i], w[i])
out = {'nobj': len(objs), 'nmesh': len(meshes), 'narm': len(arms), 'world_size': [mx[i]-mn[i] for i in range(3)], 'world_min': mn, 'world_max': mx, 'objs': objs[:40]}
print('JSONSTART')
print(json.dumps(out, indent=2))
print('JSONEND')
