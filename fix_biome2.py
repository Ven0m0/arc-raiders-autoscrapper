import json
with open('biome.json', 'r') as f:
    data = json.load(f)
if 'ignore' in data['files']:
    data['files']['ignore'] = data['files']['ignore']
if 'ignoreUnknown' in data['files']:
    data['files']['ignoreUnknown'] = data['files']['ignoreUnknown']
if 'includes' in data['files']:
    data['files']['includes'] = data['files']['includes']

with open('biome.json', 'w') as f:
    json.dump(data, f, indent=2)
