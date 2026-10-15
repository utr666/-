from converter import CurrencyConverter

def main():
    converter = CurrencyConverter()
    
    print("=" * 60)
    print("💱 КОНВЕРТЕР ВАЛЮТ И КРИПТОВАЛЮТ (CoinGecko API)")
    print("=" * 60)
    print(f"📊 Доступно криптовалют: {len(converter.list_cryptos())}")
    print(f"💵 Доступно фиатных валют: {len(converter.list_fiats())}")
    print("=" * 60)
    
    while True:
        print("\n🔹 Введите 'q' для выхода")
        print(f"🔹 Доступные крипто: {', '.join(converter.list_cryptos()[:8])}...")
        print(f"🔹 Доступные фиат: {', '.join(converter.list_fiats())}")
        
        try:
            amount_str = input("\n💰 Введите сумму (или 'q' для выхода): ").strip()
            if amount_str.lower() == 'q':
                print("👋 До свидания!")
                break
            
            amount = float(amount_str)
            from_curr = input("🔄 Из какой валюты (например, USD, BTC): ").strip()
            to_curr = input("➡️  В какую валюту (например, RUB, ETH): ").strip()
            
            if not from_curr or not to_curr:
                print("❌ Обе валюты должны быть указаны!")
                continue
            
            print("\n⏳ Получаю актуальный курс...")
            result = converter.convert(amount, from_curr, to_curr)
            
            print("\n" + "=" * 60)
            print("✅ РЕЗУЛЬТАТ КОНВЕРТАЦИИ")
            print("=" * 60)
            print(f"💵 {result['amount']:,.4f} {result['from']}")
            print(f"   ↓")
            print(f"💰 {result['result']:,.6f} {result['to']}")
            print(f"\n📈 Курс: {result['rate']}")
            print(f"🕐 Обновлено: {result['timestamp']}")
            print("=" * 60)
            
        except ValueError as e:
            if "could not convert" in str(e).lower():
                print(f"❌ Некорректная сумма. Введите число.")
            else:
                print(f"❌ Ошибка: {e}")
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем.")
            break
        except Exception as e:
            print(f"❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
