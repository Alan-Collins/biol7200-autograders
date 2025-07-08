#!/usr/bin/env python3

import os
import re

for file in os.listdir("tests/"):
    if not file.startswith("test"):
        continue
    with open(f"tests/{file}") as fin:
        vals = [int(i) for i in re.findall(r"@weight\((\d+)\)",fin.read())]
    print(f"{file}\t{sum(vals)}")
    