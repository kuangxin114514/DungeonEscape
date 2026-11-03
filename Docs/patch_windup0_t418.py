# -*- coding: utf-8 -*-
from __future__ import print_function
import io,re
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw=io.open(p,encoding="utf-8").read()
raw2,n=re.subn(r"ATTACK_WINDUP\s*=\s*[0-9.]+","ATTACK_WINDUP = 0.0",raw,count=1)
print("n",n)
io.open(p,"w",encoding="utf-8",newline="\n").write(raw2)
