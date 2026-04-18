import json


def _normalize_string_list(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        normalized = []
        for entry in value:
            if isinstance(entry, str) and entry not in normalized:
                normalized.append(entry)
        return normalized
    return value


with open('biome.json', 'r') as f:
    data = json.load(f)

files = data.get('files')
if isinstance(files, dict):
    if 'ignore' in files:
        files['ignore'] = _normalize_string_list(files['ignore'])
    if 'ignoreUnknown' in files and isinstance(files['ignoreUnknown'], str):
        lowered = files['ignoreUnknown'].strip().lower()
        if lowered == 'true':
            files['ignoreUnknown'] = True
        elif lowered == 'false':
            files['ignoreUnknown'] = False
    if 'includes' in files:
        files['includes'] = _normalize_string_list(files['includes'])

with open('biome.json', 'w') as f:
    json.dump(data, f, indent=2)
