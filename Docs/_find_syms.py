import re, sys
paths = [
    r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Engine.dll",
    r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-UnrealEd.dll",
]
pat = re.compile(rb"CreateNode[@\w]*USimpleConstructionScript[\w@$?]*|AddNode[@\w]*USimpleConstructionScript[\w@$?]*|AddComponentsToBlueprint[\w@$?]*|CreateBlueprintFromActor[\w@$?]*")
# Also simpler: just find ASCII strings containing CreateNode and SimpleConstruction
pat2 = re.compile(rb"[?A-Za-z_][A-Za-z0-9_@$?]{0,200}CreateNode[A-Za-z0-9_@$?]{0,200}")
pat3 = re.compile(rb"[?A-Za-z_][A-Za-z0-9_@$?]{0,200}AddComponentsToBlueprint[A-Za-z0-9_@$?]{0,200}")
for path in paths:
    print("===", path)
    with open(path, "rb") as f:
        data = f.read()
    print("size", len(data))
    found = set()
    for m in pat2.finditer(data):
        s = m.group().decode("ascii", errors="ignore")
        if "SimpleConstruction" in s or "SCS" in s or "CreateNode" in s:
            found.add(s)
    for m in pat3.finditer(data):
        found.add(m.group().decode("ascii", errors="ignore"))
    # Also AddNode
    for m in re.finditer(rb"[?A-Za-z_][A-Za-z0-9_@$?]{0,200}AddNode[A-Za-z0-9_@$?]{0,80}SimpleConstruction[A-Za-z0-9_@$?]{0,80}", data):
        found.add(m.group().decode("ascii", errors="ignore"))
    for s in sorted(found):
        if len(s) < 180:
            print(s)
    print("count", len(found))