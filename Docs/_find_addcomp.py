import re
path = r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll"
with open(path,"rb") as f: data=f.read()
keys = [b"AddComponentsToBlueprint", b"CreateBlueprintFromActor", b"AddNewComponent", b"AddComponent", b"HarvestComponentsFromActors"]
for key in keys:
    print("===", key.decode())
    found=set()
    for m in re.finditer(rb"[?A-Za-z_][A-Za-z0-9_@$?]{0,220}"+re.escape(key)+rb"[A-Za-z0-9_@$?]{0,120}", data):
        s=m.group().decode("ascii","ignore")
        if len(s)<200: found.add(s)
    for s in sorted(found)[:40]:
        print(s)
    print("count", len(found))
