from unittest.mock import patch
import pytest
import os
import hashlib
from database import Database

def test_database_creation_via_password(tmp_path):
    """Тест: Создание БД через пароль (как в старых версиях)"""
    fake_db_file = os.path.join(tmp_path, "test_pass.db")
    
    db = Database(password="my_secret_password", db_path=fake_db_file)
    db._save()
    
    assert os.path.exists(fake_db_file) == True
    
    with open(fake_db_file, "rb") as f:
        raw_data = f.read()
    
    assert b"active_chat" not in raw_data

def test_database_creation_via_key(tmp_path):
    """Тест: Создание БД через готовые байты ключа (как работает токен сейчас)"""
    fake_db_file = os.path.join(tmp_path, "test_key.db")
    
    # Генерируем ключ точно так же, как это делает runner.py
    raw_key = hashlib.sha256("token_password".encode('utf-8')).digest()
    
    db = Database(key=raw_key, db_path=fake_db_file)
    db._save()
    
    assert os.path.exists(fake_db_file) == True

def test_save_and_load_with_key(tmp_path):
    """Тест: Шифрование и расшифровка данных с использованием ключа"""
    fake_db_file = os.path.join(tmp_path, "test_save_key.db")
    
    raw_key = hashlib.sha256("test_key".encode('utf-8')).digest()
    
    # 1. Создаем и пишем данные
    db1 = Database(key=raw_key, db_path=fake_db_file)
    db1.create_chat("Key Test Chat")
    db1.add_message("user", "Hello Key!")
    
    # 2. "Убиваем" базу из памяти и читаем с диска по ключу
    db2 = Database(key=raw_key, db_path=fake_db_file)
    
    loaded_history = db2.get_active_history()
    assert len(loaded_history) == 1
    assert loaded_history[0]["content"] == "Hello Key!"

def test_wrong_key_fails(tmp_path):
    """Тест: Попытка открыть базу неправильным ключом"""
    fake_db_file = os.path.join(tmp_path, "test_wrong_key.db")
    
    correct_key = hashlib.sha256("correct".encode('utf-8')).digest()
    wrong_key = hashlib.sha256("wrong".encode('utf-8')).digest()
    
    db1 = Database(key=correct_key, db_path=fake_db_file)
    db1.create_chat("Secret")
    
    # Подделываем ввод пользователя (нажимает 'n' когда спрашивает удалить ли базу)
    with patch('builtins.input', return_value='n'):
        with pytest.raises(SystemExit):
            Database(key=wrong_key, db_path=fake_db_file)

def test_clear_chat_history(tmp_path):
    """Тест: Очистка истории чата"""
    fake_db_file = os.path.join(tmp_path, "test_clear.db")
    raw_key = hashlib.sha256("clear".encode('utf-8')).digest()
    
    db = Database(key=raw_key, db_path=fake_db_file)
    db.create_chat("Clear Test")
    db.add_message("user", "Msg 1")
    db.add_message("assistant", "Msg 2")
    
    # Очищаем
    chat_id = db.data.get('active_chat')
    db.data['chats'][chat_id]['history'] = []
    db._save()
    
    # Проверяем
    db2 = Database(key=raw_key, db_path=fake_db_file)
    assert len(db2.get_active_history()) == 0