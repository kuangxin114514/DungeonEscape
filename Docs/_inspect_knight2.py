import bpy, json
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
path = r'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb'
bpy.ops.import_scene.gltf(filepath=path)
out=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','ARMATURE'): continue
    parent=o.parent.name if o.parent else None
    pbone=o.parent_bone if o.parent_type=='BONE' else None
    ptype=o.parent_type
    dims=list(o.dimensions)
    loc=list(o.location)
    wloc=list(o.matrix_world.translation)
    vg=[g.name for g in getattr(o,'vertex_groups',[])]
    # check if skinned
    has_arm = any(m.type=='ARMATURE' for m in o.modifiers) if o.type=='MESH' else False
    out.append({'n':o.name,'t':o.type,'parent':parent,'ptype':ptype,'pbone':pbone,'dims':[round(x,3) for x in dims],'wloc':[round(x,3) for x in wloc],'vg':vg[:8],'mod_arm':has_arm})
# world bounds all body (Knight_*)
mn=Vector((1e9,1e9,1e9)); mx=Vector((-1e9,-1e9,-1e9))
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('Knight_'): continue
    for c in o.bound_box:
        w=o.matrix_world @ Vector(c)
        mn=Vector((min(mn.x,w.x),min(mn.y,w.y),min(mn.z,w.z)))
        mx=Vector((max(mx.x,w.x),max(mx.y,w.y),max(mx.z,w.z)))
print('JSONSTART')
print(json.dumps({'body_size':[round(mx.x-mn.x,3),round(mx.y-mn.y,3),round(mx.z-mn.z,3)],'body_min':[round(v,3) for v in mn],'body_max':[round(v,3) for v in mx],'objs':out}, indent=2))
print('JSONEND')
arm=bpy.data.objects.get('Rig')
if arm:
    print('BONES', [b.name for b in arm.data.bones])
