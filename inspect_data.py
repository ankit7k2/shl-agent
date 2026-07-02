import json
from collections import Counter

with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

counter = Counter()

for item in data:
    for key in item.get("keys", []):
        counter[key] += 1

print(counter)
