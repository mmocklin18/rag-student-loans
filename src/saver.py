import json, os

def save_json(records, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_json_map(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {rec["url"]: rec for rec in data}
    except FileNotFoundError:
        return {}
