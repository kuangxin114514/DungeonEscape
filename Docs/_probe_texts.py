# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_texts.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("PTEXT: "+str(m))
for path in ("/Game/UI/Shop/WBP_Shop","/Game/UI/Shop/WBP_Shop2","/Game/UI/Menus/WBP_MainMenu","/Game/UI/Shop/WBP_Shop_Weapon","/Game/UI/HUD/WBP_PlayerHealthBar"):
    a=unreal.EditorAssetLibrary.load_asset(path)
    log("loaded %s -> %s"%(path,a))
    # list all objects under package
    n_tb=0; n_all=0; samples=[]
    pkg = path
    for o in unreal.ObjectIterator(unreal.Object):
        try:
            pn=o.get_path_name()
        except Exception:
            continue
        if path.split("/")[-1] not in pn:
            continue
        n_all+=1
        cn=o.get_class().get_name() if o.get_class() else "?"
        if "Text" in cn or "Button" in cn or "Image" in cn or "Progress" in cn or "Canvas" in cn:
            if len(samples)<30:
                samples.append("%s %s"%(cn, o.get_name()))
        if cn=="TextBlock":
            n_tb+=1
    log("n_all=%d n_tb=%d samples=%s"%(n_all,n_tb,samples))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")