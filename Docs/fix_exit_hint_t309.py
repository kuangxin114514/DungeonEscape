# -*- coding: utf-8 -*-
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
s = io.open(p, encoding="utf-8").read()
i = s.find('if key[0] == "exit":')
print("i", i)
print(repr(s[i:i+160]))
# Replace any exit hint that mentions hub return
import re
ns, n = re.subn(
    r'(if key\[0\] == "exit":\s*_print\(world,\s*u")([^"]*)(")',
    r'\1按 E 进入2层\3',
    s,
    count=1,
)
print("n", n)
if n:
    io.open(p, "w", encoding="utf-8").write(ns)
    print("hint fixed")
else:
    # fallback: find line with exit print
    for line in s.splitlines():
        if "exit" in line and "_print" in line:
            print("LINE", repr(line))