#!/usr/bin/env python3

import os
import re

total = 0
for file in os.listdir("tests/"):
    if not file.startswith("test"):
        continue
    with open(f"tests/{file}") as fin:
        vals = [int(i) for i in re.findall(r"@(?:weight|partial_credit)\((\d+)\)",fin.read())]
        total += sum(vals)
    print(f"{file}\t{sum(vals)}")
print(f"Total\t{total}")
    