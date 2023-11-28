import os
import re
inf = open("in.txt", "r", encoding="utf-8")
inx = inf.read()
inx = re.sub(r"[^a-zA-Z\n ąćśńłóężź]+", "", inx)
inx = inx.split(" ")
dictA = open("dict.txt", "a", encoding="utf-8")
dictR = open("dict.txt", "r", encoding="utf-8")
try:
    if os.stat("dict.txt").st_size == 0:
        inx = set(inx)
        for word in inx:
            dictA.write(word.lower() + "\n")
    else:
        dictRv = dictR.read()
        dictRv = dictRv.split("\n")
        not_in_dict = set(inx) - set(dictRv)
        not_in_dict = set(not_in_dict)
        for word in not_in_dict:
            dictA.write(word.lower() + "\n")
except Exception as e:
    print(f"ERROR: {e}")
    