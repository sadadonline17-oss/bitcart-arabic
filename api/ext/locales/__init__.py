import json
import os
from typing import Any

_locales_data: dict[str, dict[str, Any]] = {}


def _load_locales() -> dict[str, dict[str, Any]]:
    global _locales_data
    if not _locales_data:
        locales_path = os.path.join(os.path.dirname(__file__), "regions.json")
        with open(locales_path) as f:
            _locales_data = json.load(f)
    return _locales_data


def get_locale_data(locale: str) -> dict[str, Any] | None:
    data = _load_locales()
    return data.get(locale)


def get_locale_currency(locale: str) -> str | None:
    data = get_locale_data(locale)
    return data.get("currency") if data else None


def get_locale_currency_symbol(locale: str) -> str | None:
    data = get_locale_data(locale)
    return data.get("currency_symbol") if data else None


def is_rtl_locale(locale: str) -> bool:
    data = get_locale_data(locale)
    return data.get("rtl", False) if data else False


def get_supported_arabic_locales() -> list[str]:
    return [
        "ar-SA",
        "ar-AE",
        "ar-KW",
        "ar-BH",
        "ar-QA",
        "ar-OM",
        "ar-IQ",
        "ar-JO",
        "ar-LB",
        "ar-EG",
        "ar-DZ",
        "ar-MA",
        "ar-TN",
        "ar-LY",
        "ar-SD",
        "ar-SY",
        "ar-YE",
    ]


def get_gulf_locales() -> list[str]:
    return [
        "ar-SA",
        "ar-AE",
        "ar-KW",
        "ar-BH",
        "ar-QA",
        "ar-OM",
    ]


def get_locale_native_name(locale: str) -> str | None:
    data = get_locale_data(locale)
    return data.get("native_name") if data else None
