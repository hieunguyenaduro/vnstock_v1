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

    @staticmethod
    def get_data_from_file(file_path, list_tickers):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data[0][list_tickers]