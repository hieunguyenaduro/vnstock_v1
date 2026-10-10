import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Common:

    @staticmethod
    def create_json_file(data, etl_path, filename) -> Path:
        filename = Path(f"{etl_path}/data/{filename}.json") if not str(filename).endswith('.json') else Path(filename)
        # Nếu filename truyền vào chưa chứa thư mục, đặt dưới etl_path/data/
        if len(filename.parts) == 1:
            filename = Path(f"{etl_path}/data/{filename.name}")

        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logger.debug("Da ghi %s", filename)
        return filename

    @staticmethod
    def get_data_from_file(file_path, list_tickers):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            return []

        if not data or not isinstance(data, list):
            return []
        first = data[0]
        if not isinstance(first, dict):
            return []
        value = first.get(list_tickers, [])
        return value if isinstance(value, list) else []