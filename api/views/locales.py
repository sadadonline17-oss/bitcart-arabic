from fastapi import APIRouter

from api.ext.locales import (
    get_gulf_locales,
    get_locale_currency,
    get_locale_currency_symbol,
    get_locale_native_name,
    get_supported_arabic_locales,
    is_rtl_locale,
)
from api.ext.moneyformat import currency_table

router = APIRouter()


@router.get("/locales/arabic")
async def get_arabic_locales() -> dict:
    gulf_locales = get_gulf_locales()
    all_arabic = get_supported_arabic_locales()
    return {
        "gulf": [{"code": code, "name": get_locale_native_name(code), "currency": get_locale_currency(code)} for code in gulf_locales],
        "all": [{"code": code, "name": get_locale_native_name(code), "currency": get_locale_currency(code)} for code in all_arabic],
    }


@router.get("/locales/{locale}")
async def get_locale_info(locale: str) -> dict:
    return {
        "code": locale,
        "name": get_locale_native_name(locale),
        "currency": get_locale_currency(locale),
        "currency_symbol": get_locale_currency_symbol(locale),
        "rtl": is_rtl_locale(locale),
    }


@router.get("/currencies/localized")
async def get_localized_currencies(locale: str | None = None) -> dict:
    if locale and locale.startswith("ar"):
        return {
            "locale": locale,
            "rtl": is_rtl_locale(locale),
            "currencies": currency_table.get_all_currencies_with_ar(),
        }
    return {
        "locale": locale or "en",
        "rtl": False,
        "currencies": currency_table.get_all_currencies_with_ar(),
    }
