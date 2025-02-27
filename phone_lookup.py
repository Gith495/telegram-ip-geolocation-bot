import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import sqlite3

def create_database():
    conn = sqlite3.connect("phone_info.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS phone_data (
                        phone_number TEXT PRIMARY KEY,
                        country TEXT,
                        operator TEXT,
                        breaches TEXT)''')
    conn.commit()
    conn.close()

def save_to_database(phone_number, country, operator, breaches):
    conn = sqlite3.connect("phone_info.db")
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO phone_data VALUES (?, ?, ?, ?)", (phone_number, country, operator, str(breaches)))
    conn.commit()
    conn.close()

def get_phone_info(phone_number):
    try:
        # Парсим номер
        parsed_number = phonenumbers.parse(phone_number, None)
        
        # Получаем страну и регион
        country = geocoder.description_for_number(parsed_number, "en")
        operator = carrier.name_for_number(parsed_number, "en")
        
        # Проверяем утечки данных (пример с Have I Been Pwned)
        hibp_api_key = "YOUR_HIBP_API_KEY"  # Замените на свой API-ключ
        hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{phone_number}"
        headers = {"hibp-api-key": hibp_api_key}
        response = requests.get(hibp_url, headers=headers)
        
        if response.status_code == 200:
            breaches = response.json()
        else:
            breaches = "No breaches found or API limit reached"
        
        # Сохраняем в базу данных
        save_to_database(phone_number, country, operator, breaches)
        
        return {
            "phone_number": phone_number,
            "country": country,
            "operator": operator,
            "breaches": breaches
        }
    except Exception as e:
        return {"error": str(e)}

# Создаем базу данных
create_database()

# Пример использования
phone = "+14155552671"  # Введите номер телефона
info = get_phone_info(phone)
print(info)
