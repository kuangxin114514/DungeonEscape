# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
raw=io.open(p,encoding="utf-8").read().replace("\r\n","\n")
old='''            if key[0] == "exit_d2":
                _print(world, u"按 E 进入2层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "exit_hub":
                _print(world, u"按 E 返回主城", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "gate":
                _print(world, u"按 E 进入地下城", (1.0, 0.85, 0.2, 1.0), 2.0)
            else:
                _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 2.0)'''
new='''            if key[0] == "exit_d2":
                _print(world, u"按 E 进入2层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "exit_d3":
                _print(world, u"按 E 进入3层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] in ("exit_hub", "exit_hub_d2"):
                _print(world, u"按 E 返回主城", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "gate":
                _print(world, u"按 E 进入地下城", (1.0, 0.85, 0.2, 1.0), 2.0)
            else:
                _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 2.0)'''
if old not in raw:
    print("HINT_PRINT_MISSING")
else:
    raw=raw.replace(old,new,1)
    print("hints_ok")
io.open(p,"w",encoding="utf-8",newline="\n").write(raw)
compile(raw,p,"exec")
print("syntax_ok")
