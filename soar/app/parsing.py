import json


def safe_json_parse(raw: str, required_fields: list, fallback: dict) -> dict:
    try:
        data = json.loads(raw)

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        return data

    except Exception:
        return fallback