import json
with open('biome.json', 'r') as f:
    data = json.load(f)
if 'ignores' in data['files']:
    data['files']['ignore'] = data['files'].pop('ignores')
with open('biome.json', 'w') as f:
    json.dump(data, f, indent=2)
