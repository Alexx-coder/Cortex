import json
import os
import hashlib
import base64
from cryptography.fernet import Fernet

DEFAULT_DB_PATH = os.path.expanduser("~/.cortex/chats.db")

class Database:
    def __init__(self, password: str, db_path: str = None):
        # Если путь не указан (как при обычном запуске), используем стандартный
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # Делаем 32-байтный ключ из пароля
        key_bytes = hashlib.sha256(password.encode('utf-8')).digest()
        # Fernet требует ключ в формате Base64. Переводим.
        self.key = base64.urlsafe_b64encode(key_bytes)
        self.cipher = Fernet(self.key)
        self.data = self._load()

    def _load(self):
        # Используем self.db_path вместо старого DB_PATH
        if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            return {"active_chat": None, "chats": {}}

        with open(self.db_path, "rb") as f:
            encrypted_data = f.read()

        if not encrypted_data:
            return {"active_chat": None, "chats": {}}

        try:
            # Дешифруем сырые байты из файла
            decrypted_bytes = self.cipher.decrypt(encrypted_data)
            json_string = decrypted_bytes.decode('utf-8')
            return json.loads(json_string)
        except Exception as e:
            print(f"[ERROR] Failed to decrypt database. Wrong password? Details: {e}")
            exit(1)

    def _save(self):
        json_string = json.dumps(self.data, indent=4, ensure_ascii=False)
        
        try:
            # Шифруем строку JSON, получаем байты
            encrypted_data = self.cipher.encrypt(json_string.encode('utf-8'))
            
            # Используем self.db_path!
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Записываем зашифрованные байты
            with open(self.db_path, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"[ERROR] Failed to save database: {e}")

    def create_chat(self, chat_name: str):
        chat_id = f"chat_{len(self.data['chats']) + 1}"
        self.data['chats'][chat_id] = {
            "name": chat_name,
            "history": []
        }
        self.data['active_chat'] = chat_id
        self._save()
        return chat_id

    def get_active_history(self):
        chat_id = self.data.get('active_chat')
        if not chat_id or chat_id not in self.data['chats']:
            return []
        return self.data['chats'][chat_id]['history']

    def add_message(self, role: str, content: str):
        chat_id = self.data.get('active_chat')
        if not chat_id or chat_id not in self.data['chats']:
            return
        self.data['chats'][chat_id]['history'].append({"role": role, "content": content})
        self._save()

    def list_chats(self):
        return [f"{cid}: {info['name']} ({len(info['history'])} messages)" for cid, info in self.data['chats'].items()]

    def switch_chat(self, chat_id: str):
        if chat_id in self.data['chats']:
            self.data['active_chat'] = chat_id
            self._save()
            return True
        return False