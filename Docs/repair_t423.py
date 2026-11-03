# -*- coding: utf-8 -*-
from __future__ import print_function
src = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py.pre_t423_corrupt"
dst = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
data = open(src, "rb").read()

def U(s):
    return s.encode("utf-8")

reps = [
    (b"u\"\xe6\xad\xa6\xe5\x99\xa8\xe5\xba?),", U("u\"\u6b66\u5668\u5e97\"),")),
    (b"u\"\xe9\x98\xb2\xe5\x85\xb7\xe5\xba?),", U("u\"\u9632\u5177\u5e97\"),")),
    (b"u\"\xe5\x9b\x9e\xe8\xa1\x80\xe5\xba?),", U("u\"\u56de\u8840\u5e97\"),")),
    (b"u\"\xe6\xad\xa6\xe5\x99\xa8\xe5\xba?,", U("u\"\u6b66\u5668\u5e97\",")),
    (b"u\"\xe9\x98\xb2\xe5\x85\xb7\xe5\xba?,", U("u\"\u9632\u5177\u5e97\",")),
    (b"u\"\xe5\x9b\x9e\xe8\xa1\x80\xe5\xba?,", U("u\"\u56de\u8840\u5e97\",")),
    (b"u\"\xe5\x89?+\xe7\x9b? \xe5\x90\x8c\xe6\x97\xb6\xe8\xa3\x85\xe5\xa4\x87\"", U("u\"\u52511+\u76fe1 \u540c\u65f6\u88c5\u5907\"")),
    (b"u\"\xe9\x87\x91\xe5\xb8\x81\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x88\xe9\x9c\x80\xe8\xa6?\xef\xbc?,", U("u\"\u91d1\u5e01\u4e0d\u8db3\uff08\u9700\u89815\uff09\",")),
    (b"u\"\xe9\x87\x91\xe5\xb8\x81\xe4\xb8\x8d\xe8\xb6\xb3\xef\xbc\x88\xe9\x9c\x805\xef\xbc?,", U("u\"\u91d1\u5e01\u4e0d\u8db3\uff08\u97005\uff09\",")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe5\x89?\xe6\x88\x90\xe5\x8a\x9f\xef\xbc?5\xe9\x87\x91\xe5\xb8\x81\xef\xbc?,", U("u\"\u8d2d\u4e70\u52511\u6210\u529f\uff08-5\u91d1\u5e01\uff09\",")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe7\x9b?\xe6\x88\x90\xe5\x8a\x9f\xef\xbc?5\xe9\x87\x91\xe5\xb8\x81\xef\xbc?,", U("u\"\u8d2d\u4e70\u76fe1\u6210\u529f\uff08-5\u91d1\u5e01\uff09\",")),
    (b"\"\"\"Bind \xe8\xb4\xad\xe4\xb9\xb0\xe7\x9b? (Button_0) on armor shop.\"\"\"", U("\"\"\"Bind \u8d2d\u4e70\u76fe1 (Button_0) on armor shop.\"\"\"")),
    (b"\"\"\"Bind \xe8\xb4\xad\xe4\xb9\xb0\xe5\x89? (Button_0). Uses callable if available; else tick edge on is_pressed.\"\"\"", U("\"\"\"Bind \u8d2d\u4e70\u52511 (Button_0). Uses callable if available; else tick edge on is_pressed.\"\"\"")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe7\x9b? (5\xe9\x87\x91\xe5\xb8\x81)\"", U("u\"\u8d2d\u4e70\u76fe1 (5\u91d1\u5e01)\"")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe5\x89? (5\xe9\x87\x91\xe5\xb8\x81)\"", U("u\"\u8d2d\u4e70\u52511 (5\u91d1\u5e01)\"")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe7\x9b?\xef\xbc\x88\xe6\x9c\xaa\xe5\xbc\x80\xe6\x94\xbe\xef\xbc\x89\"", U("u\"\u8d2d\u4e70\u76fe2\uff08\u672a\u5f00\u653e\uff09\"")),
    (b"u\"\xe8\xb4\xad\xe4\xb9\xb0\xe5\x89?\xef\xbc\x88\xe6\x9c\xaa\xe5\xbc\x80\xe6\x94\xbe\xef\xbc\x89\"", U("u\"\u8d2d\u4e70\u52512\uff08\u672a\u5f00\u653e\uff09\"")),
    (b"# optional: label Button as \xe5\x89? placeholder", U("# optional: label Button as \u52511 placeholder")),
    (b"u\"\xe5\xb7\xb2\xe6\x89\x93\xe5\xbc\x80\xef\xbc? +", U("u\"\u5df2\u6253\u5f00\uff1a\" +")),
    (b"u\"\xe8\xbf\x9b\xe5\x85\xa5\xe5\x9c\xb0\xe4\xb8\x8b\xe5\x9f\x8e\xe2\x80?,", U("u\"\u8fdb\u5165\u5730\u4e0b\u57ce\u2026\",")),
    (b"u\"\xe8\xbf\x94\xe5\x9b\x9e\xe4\xb8\xbb\xe5\x9f\x8e\xe2\x80?,", U("u\"\u8fd4\u56de\u4e3b\u57ce\u2026\",")),
    (b"u\"\xe6\x8c\xa5\xe7\xa0\x8d\xef\xbc?,", U("u\"\u6325\u780d\uff01\",")),
    (b"u\"\xe6\x8c?E \xe8\xbf\x9b\xe5\x85\xa52\xe5\xb1?,", U("u\"\u6309 E \u8fdb\u51652\u5c42\",")),
    (b"u\"\xe6\x8c?E \xe8\xbf\x9b\xe5\x85\xa53\xe5\xb1?,", U("u\"\u6309 E \u8fdb\u51653\u5c42\",")),
    (b"u\"\xe6\x8c?E \xe8\xbf\x94\xe5\x9b\x9e\xe4\xb8\xbb\xe5\x9f\x8e\"", U("u\"\u6309 E \u8fd4\u56de\u4e3b\u57ce\"")),
    (b"u\"\xe6\x8c?E \xe8\xbf\x9b\xe5\x85\xa5\xe5\x9c\xb0\xe4\xb8\x8b\xe5\x9f?,", U("u\"\u6309 E \u8fdb\u5165\u5730\u4e0b\u57ce\",")),
    (b"u\"\xe6\x8c?E \xe6\x89\x93\xe5\xbc\x80\"", U("u\"\u6309 E \u6253\u5f00\"")),
    (b"\xe9\xab?/", U("\u9ad8\uff0c")),
    (b"\xef\xbc?#", U("\uff09#")),
    (b"\xe7\xa6?cm", U("\u79bbcm")),
    (b"\xef\xbc?\n", U("\uff09\n")),
]
for a, b in reps:
    data = data.replace(a, b)

marker = b"u\"\xe8\xbf\x9b\xe5\x85\xa5\xe5\x9c\xb0\xe4\xb8\x8b\xe5\x9f?\xe5\xb1?,"
parts = data.split(marker)
print("enter parts", len(parts))
if len(parts) == 3:
    data = parts[0] + U("u\"\u8fdb\u5165\u5730\u4e0b\u57ce2\u5c42\",") + parts[1] + U("u\"\u8fdb\u5165\u5730\u4e0b\u57ce3\u5c42\",") + parts[2]
elif len(parts) == 2:
    data = parts[0] + U("u\"\u8fdb\u5165\u5730\u4e0b\u57ce2\u5c42\",") + parts[1]

fail_m = b"u\"\xe8\xbf?\xe5\xb1\x82\xe5\xa4\xb1\xe8\xb4? \""
fparts = data.split(fail_m)
print("fail parts", len(fparts))
if len(fparts) == 3:
    data = fparts[0] + U("u\"\u8fdb2\u5c42\u5931\u8d25: \"") + fparts[1] + U("u\"\u8fdb3\u5c42\u5931\u8d25: \"") + fparts[2]
elif len(fparts) == 2:
    data = fparts[0] + U("u\"\u8fdb2\u5c42\u5931\u8d25: \"") + fparts[1]

data = data.replace(b"\xe2\x80?", b"\xe2\x80\x94")
out = bytearray(); i = 0
while i < len(data):
    if i + 3 < len(data) and data[i:i+3] == b"\xe2\x80\x94" and 65 <= data[i+3] <= 122:
        out.extend(b"\xe2\x80\x94 "); i += 3; continue
    out.append(data[i]); i += 1
data = bytes(out)

out = bytearray(); i = 0; left = 0
while i < len(data):
    b = data[i]
    if b < 0x80:
        out.append(b); i += 1; continue
    if 0xC2 <= b <= 0xDF and i+1 < len(data) and 0x80 <= data[i+1] <= 0xBF:
        out.extend(data[i:i+2]); i += 2; continue
    if 0xE0 <= b <= 0xEF and i+2 < len(data) and 0x80 <= data[i+1] <= 0xBF and 0x80 <= data[i+2] <= 0xBF:
        out.extend(data[i:i+3]); i += 3; continue
    if 0xE0 <= b <= 0xEF and i+2 < len(data) and 0x80 <= data[i+1] <= 0xBF and data[i+2] == 0x3F:
        print("still", i, data[i:i+24]); out.extend(b"\xef\xbf\xbd"); left += 1; i += 3; continue
    out.extend(b"\xef\xbf\xbd"); left += 1; i += 1

raw = bytes(out)
text = raw.decode("utf-8")
if "EXIT_RANGE = 750.0" not in text:
    text = text.replace("EXIT_RANGE = 380.0", "EXIT_RANGE = 750.0")
compile(text, "shop_interact_runtime.py", "exec")
open(dst, "wb").write(text.encode("utf-8"))
print("SYNTAX_OK left_bad=", left)
checks = [
    u"\u6b66\u5668\u5e97",
    u"\u9632\u5177\u5e97",
    u"\u6309 E \u8fdb\u51653\u5c42",
    u"\u6309 E \u8fd4\u56de\u4e3b\u57ce",
    u"\u52511+\u76fe1 \u540c\u65f6\u88c5\u5907",
    u"\u8d2d\u4e70\u52511\u6210\u529f",
    u"\u8fdb\u5165\u5730\u4e0b\u57ce3\u5c42",
    "EXIT_RANGE = 750.0",
]
for s in checks:
    print(s, s in text)