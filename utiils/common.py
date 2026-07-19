import json
from pathlib import Path

class Common:

    @staticmethod
    def create_json_file(data, etl_path, filename):
        if not filename.endswith('.json'):
            filename = Path(f"{etl_path}/data/{filename}.json")

        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
