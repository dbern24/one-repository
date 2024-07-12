import sqlite3

# Подключение к базе данных (если базы данных не существует, она будет создана)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Создание таблицы с добавлением столбца refreward
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    referrer_id INTEGER,
                    balance NUMERIC DEFAULT 0,  -- Изменено на NUMERIC
                    refreward TEXT CHECK(refreward IN ('yes', 'no')) DEFAULT 'no'
                )''')

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()
