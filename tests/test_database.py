import pytest
import os
from database import Database

def test_database_creation_and_encryption(tmp_path):
    fake_db_file = os.path.join(tmp_path, "test_chats.db")
    
    db = Database(password="test_password_123", db_path=fake_db_file)
    
    db._save()
    
    assert os.path.exists(fake_db_file) == True
    
    with open(fake_db_file, "rb") as f:
        raw_data = f.read()
    
    assert b"active_chat" not in raw_data

def test_create_chat_and_save_history(tmp_path):
    fake_db_file = os.path.join(tmp_path, "test_chats2.db")
    db = Database(password="my_secret", db_path=fake_db_file)
    
    chat_id = db.create_chat("Test Project")
    
    assert chat_id == "chat_1"
    assert db.data["chats"]["chat_1"]["name"] == "Test Project"
    assert db.data["active_chat"] == "chat_1"
    
    db.add_message("user", "Привет, ИИ")
    db.add_message("assistant", "Привет, человек!")
    
    history = db.get_active_history()
    assert len(history) == 2
    assert history[0]["content"] == "Привет, ИИ"
    
    db2 = Database(password="my_secret", db_path=fake_db_file)
    
    loaded_history = db2.get_active_history()
    assert len(loaded_history) == 2
    assert loaded_history[1]["role"] == "assistant"

def test_wrong_password_fails(tmp_path):
    fake_db_file = os.path.join(tmp_path, "test_chats3.db")
    
    db1 = Database(password="correct_pass", db_path=fake_db_file)
    db1.create_chat("Secret Chat")
    
    with pytest.raises(SystemExit):
        Database(password="wrong_pass", db_path=fake_db_file)