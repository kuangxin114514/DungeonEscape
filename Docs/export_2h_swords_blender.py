import bpy, os
from mathutils import Matrix

OUT_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx"
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\export_2h_swords.log"
SCALE = 100.0
JOBS = [
    (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Assets\gltf\sword_2handed.gltf", "SM_KayKitSword_2H.fbx"),
    (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Assets\gltf\sword_2handed_color.gltf", "SM_KayKitSword_2H_Color.fbx"),
]

def wlog(m):
    print(m)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

os.makedirs(OUT_DIR, exist_ok=True)
open(LOG, "w", encoding="utf-8").write("begin 2h swords\n")

for src, out_name in JOBS:
    wlog("IMPORT " + src)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    wlog("meshes=" + str([m.name for m in meshes]))
    if not meshes:
        raise RuntimeError("no mesh in " + src)
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
    # apply object transforms then uniform scale to cm
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in meshes:
        o.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # select only meshes for export
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    out = os.path.join(OUT_DIR, out_name)
    bpy.ops.export_scene.fbx(
        filepath=out,
        use_selection=True,
        object_types={"MESH"},
        apply_scale_options="FBX_SCALE_NONE",
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        path_mode="COPY",
        embed_textures=True,
    )
    wlog("WROTE " + out + " size=" + str(os.path.getsize(out)))

wlog("DONE")