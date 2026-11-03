import os, glob
root = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Dungeon-Remastered-1.0-main\addons\kaykit_dungeon_remastered\Assets\obj"
files = sorted(glob.glob(os.path.join(root, "**", "floor*.obj"), recursive=True))
print("count", len(files))
for path in files:
    xs,ys,zs=[],[],[]
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                p=line.split()
                if len(p)>=4:
                    xs.append(float(p[1])); ys.append(float(p[2])); zs.append(float(p[3]))
    name=os.path.basename(path)
    if not xs:
        print(name, "NO_VERTS"); continue
    print("%s n=%d X[%.4f,%.4f] Y[%.4f,%.4f] Z[%.4f,%.4f] hY=%.4f hZ=%.4f" % (
        name, len(xs), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), max(ys)-min(ys), max(zs)-min(zs)))
