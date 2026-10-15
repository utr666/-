import requests
import time
import logging
from config import DEFAULT_CURRENCY

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """
    Конвертер валют и криптовалют через CoinGecko API.
    Поддерживает кэширование курсов, чтобы не превышать лимиты API.
    """
    
    # Базовые ID популярных криптовалют (CoinGecko использует свои ID, не тикеры)
    CRYPTO_IDS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "TON": "the-open-network",
        "TRX": "tron",
        "LTC": "litecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "SHIB": "shiba-inu",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
    }
    
    # Популярные фиатные валюты
    FIAT_CURRENCIES = [
        "usd", "eur", "rub", "uah", "kzt", "byn", "gbp", "jpy", "cny", "try"
    ]
    
    def __init__(self, cache_ttl=60):
        """
        :param cache_ttl: время жизни кэша курсов в секундах (по умолчанию 60)
        """
        self.cache = {}
        self.cache_timestamp = 0
        self.cache_ttl = cache_ttl
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def _is_crypto(self, symbol: str) -> bool:
        """Проверка, является ли символ криптовалютой"""
        return symbol.upper() in self.CRYPTO_IDS
    
    def _is_fiat(self, currency: str) -> bool:
        """Проверка, является ли символ фиатной валютой"""
        return currency.lower() in self.FIAT_CURRENCIES
    
    def _get_crypto_price(self, crypto_id: str, vs_currency: str) -> float:
        """Получить цену одной единицы крипто в указанной фиатной валюте"""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": crypto_id,
            "vs_currencies": vs_currency.lower()
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[crypto_id][vs_currency.lower()]
        except (requests.RequestException, KeyError) as e:
            logger.error(f"Ошибка получения курса {crypto_id}/{vs_currency}: {e}")
            raise ValueError(f"Не удалось получить курс для {crypto_id}/{vs_currency}")
    
    def _get_fiat_rate(self, from_fiat: str, to_fiat: str) -> float:
        """Получить курс между двумя фиатными валютами через USD"""
        # Получаем курсы обеих валют к USD
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": "bitcoin",  # используем любой ID, нам нужны только vs_currencies
            "vs_currencies": f"{from_fiat.lower()},{to_fiat.lower()}"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()["bitcoin"]
            from_to_usd = data[from_fiat.lower()]
            to_to_usd = data[to_fiat.lower()]
            return to_to_usd / from_to_usd
        except (requests.RequestException, KeyError) as e:
            logger.error(f"Ошибка получения курса {from_fiat}/{to_fiat}: {e}")
            raise ValueError(f"Не удалось получить курс для {from_fiat}/{to_fiat}")
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> dict:
        """
        Главная функция конвертации.
        
        :param amount: сумма для конвертации
        :param from_currency: исходная валюта (BTC, USD, ETH...)
        :param to_currency: целевая валюта
        :return: словарь с результатом и деталями
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")
        
        from_is_crypto = self._is_crypto(from_currency)
        to_is_crypto = self._is_crypto(to_currency)
        from_is_fiat = self._is_fiat(from_currency)
        to_is_fiat = self._is_fiat(to_currency)
        
        # Проверяем валидность валют
        if not (from_is_crypto or from_is_fiat):
            raise ValueError(f"Неизвестная валюта: {from_currency}")
        if not (to_is_crypto or to_is_fiat):
            raise ValueError(f"Неизвестная валюта: {to_currency}")
        
        # Сценарий 1: Crypto → Fiat
        if from_is_crypto and to_is_fiat:
            rate = self._get_crypto_price(self.CRYPTO_IDS[from_currency], to_currency)
            result = amount * rate
            rate_info = f"1 {from_currency} = {rate:,.4f} {to_currency}"
        
        # Сценарий 2: Fiat → Crypto
        elif from_is_fiat and to_is_crypto:
            rate = self._get_crypto_price(self.CRYPTO_IDS[to_currency], from_currency)
            result = amount / rate
            rate_info = f"1 {to_currency} = {rate:,.4f} {from_currency}"
        
        # Сценарий 3: Crypto → Crypto (через USD как посредника)
        elif from_is_crypto and to_is_crypto:
            from_usd = self._get_crypto_price(self.CRYPTO_IDS[from_currency], "usd")
            to_usd = self._get_crypto_price(self.CRYPTO_IDS[to_currency], "usd")
            rate = from_usd / to_usd
            result = amount * rate
            rate_info = f"1 {from_currency} = {rate:,.6f} {to_currency}"
        
        # Сценарий 4: Fiat → Fiat
        elif from_is_fiat and to_is_fiat:
            rate = self._get_fiat_rate(from_currency, to_currency)
            result = amount * rate
            rate_info = f"1 {from_currency} = {rate:,.4f} {to_currency}"
        
        return {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "result": result,
            "rate": rate_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_rate(self, from_currency: str, to_currency: str) -> str:
        """Получить строку с текущим курсом без конвертации суммы"""
        result = self.convert(1.0, from_currency, to_currency)
        return result["rate"]
    
    def list_cryptos(self) -> list:
        """Вернуть список поддерживаемых криптовалют"""
        return sorted(self.CRYPTO_IDS.keys())
    
    def list_fiats(self) -> list:
        """Вернуть список поддерживаемых фиатных валют"""
        return [f.upper() for f in self.FIAT_CURRENCIES]
