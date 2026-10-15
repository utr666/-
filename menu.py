from crypto_parser import CryptoParser
from converter import CurrencyConverter
from history import HistoryManager
import time

class Menu:
    """Главное меню приложения"""
    
    def __init__(self):
        self.parser = CryptoParser()
        self.converter = CurrencyConverter()
        self.history = HistoryManager()
    
    def clear_screen(self):
        """Очистка экрана (кроссплатформенно)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        print("\n" + "=" * 60)
        print("🚀  CRYPTO TOOLKIT — Твой крипто-помощник")
        print("=" * 60)
    
    def show_main_menu(self):
        self.show_header()
        print("\n📋  ГЛАВНОЕ МЕНЮ")
        print("-" * 60)
        print("  [1] 🧮  Калькулятор (простая конвертация)")
        print("  [2] 📊  Список криптовалют по цене")
        print("  [3] 💱  Конвертер (пакетный режим)")
        print("  [4] 📜  История поиска")
        print("  [5] 🗑️   Очистить историю")
        print("  [0] 🚪  Выход")
        print("-" * 60)
    
    # ============== КНОПКА 1: КАЛЬКУЛЯТОР ==============
    def calculator(self):
        print("\n" + "=" * 60)
        print("🧮  КАЛЬКУЛЯТОР")
        print("=" * 60)
        print("Пример: 1000 USD → BTC, 0.5 ETH → RUB")
        print("(введите 'back' для возврата в меню)\n")
        
        while True:
            try:
                amount_str = input("💰 Сумма (или 'back'): ").strip()
                if amount_str.lower() == 'back':
                    return
                amount = float(amount_str)
                
                from_curr = input("🔄 Из валюты (USD, BTC, ETH...): ").strip()
                to_curr = input("➡️  В валюту (RUB, BTC, EUR...): ").strip()
                
                if not from_curr or not to_curr:
                    print("❌ Укажите обе валюты!")
                    continue
                
                print("⏳ Считаем...")
                result = self.converter.convert(amount, from_curr, to_curr)
                
                print("\n" + "-" * 60)
                print(f"✅ {result['amount']:,.4f} {result['from']}")
                print(f"   = {result['result']:,.6f} {result['to']}")
                print(f"📈 {result['rate']}")
                print("-" * 60)
                
                # Сохраняем в историю
                self.history.save({
                    "type": "Калькулятор",
                    "query": f"{amount} {from_curr} → {to_curr}",
                    "result": f"{result['result']:,.6f} {result['to']}"
                })
                
            except ValueError as e:
                if "could not convert" in str(e).lower():
                    print("❌ Введите число!")
                else:
                    print(f"❌ {e}")
            except KeyboardInterrupt:
                return
    
    # ============== КНОПКА 2: СПИСОК ПО ЦЕНЕ ==============
    def top_by_price(self):
        print("\n" + "=" * 60)
        print("📊  ТОП КРИПТОВАЛЮТ ПО ЦЕНЕ")
        print("=" * 60)
        
        try:
            count_str = input("Сколько монет показать? (по умолчанию 20): ").strip()
            count = int(count_str) if count_str else 20
        except ValueError:
            count = 20
        
        print("⏳ Загружаю данные...")
        coins = self.parser.fetch_top_by_price(limit=count)
        
        if not coins:
            print("❌ Не удалось получить данные.")
            return
        
        print("\n" + "-" * 60)
        print(f"{'#':<4} {'Монета':<20} {'Символ':<8} {'Цена (USD)':<15} {'Кап. ранг'}")
        print("-" * 60)
        
        for i, coin in enumerate(coins, 1):
            price = coin['Price']
            if price >= 1:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.6f}"
            
            rank = coin['Rank'] or '-'
            print(f"{i:<4} {coin['Name']:<20} {coin['Symbol']:<8} {price_str:<15} {rank}")
        
        print("-" * 60)
        
        # Сохраняем в историю
        self.history.save({
            "type": "Список по цене",
            "query": f"Топ-{count} монет",
            "result": f"Показано {len(coins)} монет"
        })
        
        input("\n[Enter] — вернуться в меню")
    
    # ============== КНОПКА 3: КОНВЕРТЕР (ПАКЕТНЫЙ) ==============
    def batch_converter(self):
        print("\n" + "=" * 60)
        print("💱  ПАКЕТНЫЙ КОНВЕРТЕР")
        print("=" * 60)
        print("Конвертирует одну сумму сразу в несколько валют.")
        print("Пример: 1 BTC → USD, EUR, RUB, ETH\n")
        print("(введите 'back' для возврата)\n")
        
        while True:
            try:
                amount_str = input("💰 Сумма (или 'back'): ").strip()
                if amount_str.lower() == 'back':
                    return
                amount = float(amount_str)
                
                from_curr = input("🔄 Из валюты: ").strip()
                to_currs_str = input("➡️  В валюты (через запятую, например USD,EUR,RUB): ").strip()
                
                if not from_curr or not to_currs_str:
                    print("❌ Укажите все значения!")
                    continue
                
                to_currs = [c.strip().upper() for c in to_currs_str.split(',')]
                
                print("⏳ Конвертирую...")
                results = self.converter.batch_convert(amount, from_curr, to_currs)
                
                print("\n" + "-" * 60)
                print(f"💵 {amount:,.4f} {from_curr.upper()} =")
                print("-" * 60)
                
                success_count = 0
                for res in results:
                    if 'error' in res:
                        print(f"  ❌ {res['to']}: {res['error']}")
                    else:
                        print(f"  ✅ {res['result']:,.6f} {res['to']}")
                        success_count += 1
                
                print("-" * 60)
                
                # Сохраняем в историю
                self.history.save({
                    "type": "Пакетный конвертер",
                    "query": f"{amount} {from_curr} → {', '.join(to_currs)}",
                    "result": f"Успешно: {success_count}/{len(results)}"
                })
                
            except ValueError as e:
                if "could not convert" in str(e).lower():
                    print("❌ Введите число!")
                else:
                    print(f"❌ {e}")
            except KeyboardInterrupt:
                return
    
    # ============== КНОПКА 4: ИСТОРИЯ ==============
    def show_history(self):
        print("\n" + "=" * 60)
        print("📜  ИСТОРИЯ ПОИСКА")
        print("=" * 60)
        
        count = self.history.count()
        if count == 0:
            print("\n📭 История пуста. Начните пользоваться приложением!")
            input("\n[Enter] — вернуться")
            return
        
        try:
            limit_str = input(f"Показать записей (всего {count}, Enter = все): ").strip()
            limit = int(limit_str) if limit_str else count
        except ValueError:
            limit = count
        
        self.history.display(limit=limit)
        input("\n[Enter] — вернуться в меню")
    
    # ============== КНОПКА 5: ОЧИСТИТЬ ИСТОРИЮ ==============
    def clear_history(self):
        print("\n" + "=" * 60)
        print("🗑️   ОЧИСТКА ИСТОРИИ")
        print("=" * 60)
        
        count = self.history.count()
        if count == 0:
            print("\n📭 История уже пуста.")
            input("\n[Enter] — вернуться")
            return
        
        print(f"\n⚠️  В истории {count} записей.")
        confirm = input("Вы уверены? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.history.clear()
            print("✅ История успешно очищена!")
        else:
            print("↩️  Отменено.")
        
        input("\n[Enter] — вернуться в меню")
    
    # ============== ГЛАВНЫЙ ЦИКЛ ==============
    def run(self):
        while True:
            self.clear_screen()
            self.show_main_menu()
            
            choice = input("\n👉 Выберите пункт [0-5]: ").strip()
            
            if choice == '1':
                self.clear_screen()
                self.calculator()
            elif choice == '2':
                self.clear_screen()
                self.top_by_price()
            elif choice == '3':
                self.clear_screen()
                self.batch_converter()
            elif choice == '4':
                self.clear_screen()
                self.show_history()
            elif choice == '5':
                self.clear_screen()
                self.clear_history()
            elif choice == '0':
                print("\n👋 До свидания! Спасибо, что пользовались Crypto Toolkit.\n")
                break
            else:
                print("\n❌ Неверный пункт. Попробуйте ещё раз.")
                time.sleep(1)


if __name__ == "__main__":
    menu = Menu()
    menu.run()
