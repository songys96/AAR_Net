import json

with open("etc/train.json", "r") as f:
    data = json.load(f)
    a = len(data['images'])

with open("etc/test.json", "r") as f:
    data = json.load(f)
    b = len(data['images'])

print(a/(a+b))