import json
import os
from datetime import datetime
from config import HISTORY_FILE

class HistoryManager:
    """Менеджер истории поиска и конвертаций"""
    
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создать файл истории, если его нет"""
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def load(self) -> list:
        """Загрузить историю из файла"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save(self, entry: dict):
        """Добавить запись в историю"""
        history = self.load()
        entry['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry['id'] = len(history) + 1
        history.append(entry)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def clear(self):
        """Очистить историю"""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    def display(self, limit: int = 10):
        """Отобразить последние записи"""
        history = self.load()
        if not history:
            print("\n📭 История пуста.")
            return
        
        print(f"\n{'=' * 70}")
        print(f"📜 ИСТОРИЯ (последние {min(limit, len(history))} из {len(history)})")
        print('=' * 70)
        
        for entry in history[-limit:]:
            print(f"\n#{entry['id']} [{entry['timestamp']}]")
            print(f"   Тип: {entry.get('type', 'unknown')}")
            print(f"   Запрос: {entry.get('query', '-')}")
            if 'result' in entry:
                print(f"   Результат: {entry['result']}")
        
        print('=' * 70)
    
    def count(self) -> int:
        """Количество записей"""
        return len(self.load())
