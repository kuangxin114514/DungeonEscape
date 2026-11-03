# -*- coding: utf-8 -*-
import unreal
LOG=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_probe_gold_wbp.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("PROBE311: "+str(m))
for path in ("/Game/UI/HUD/WBP_PlayerGold","/Game/UI/HUD/WBP_PlayerHealthBar"):
    log("=== "+path)
    for base in (unreal.Widget, unreal.TextBlock, unreal.ProgressBar, unreal.CanvasPanel, unreal.UserWidget):
        n=0
        for o in unreal.ObjectIterator(base):
            try:
                pn=o.get_path_name()
            except Exception:
                continue
            if path.split("/")[-1] not in pn:
                continue
            n+=1
            if n<=12:
                log("%s %s %s"%(base.__name__ if hasattr(base,'__name__') else base, o.get_name(), pn[-120:]))
        log("count %s = %d"%(str(base), n))
open(LOG,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", LOG)