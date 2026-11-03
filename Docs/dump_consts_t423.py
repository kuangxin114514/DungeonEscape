# -*- coding: utf-8 -*-
from __future__ import print_function
import shop_interact_runtime as sir, types, dis, marshal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\t423_consts.txt"
# collect unicode/str consts from module and all functions
ss=set()
def walk(obj, depth=0):
  if depth>4: return
  if isinstance(obj, types.FunctionType):
    walk(obj.__code__, depth+1)
  elif isinstance(obj, types.CodeType):
    for c in obj.co_consts:
      if isinstance(c, (str,)):
        if any(ord(ch)>127 for ch in c):
          ss.add(c)
      elif isinstance(c, types.CodeType):
        walk(c, depth+1)
  elif isinstance(obj, type):
    for n,v in obj.__dict__.items():
      walk(v, depth+1)

for n,v in list(sir.__dict__.items()):
  if isinstance(v, (str,)) and any(ord(ch)>127 for ch in v):
    ss.add(v)
  else:
    walk(v)
# also module docstring etc
lines=sorted(ss)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
print("count",len(lines))