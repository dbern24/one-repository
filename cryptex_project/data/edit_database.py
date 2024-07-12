import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Обновление балансов для приведения их к правильному формату
cursor.execute('''UPDATE users SET balance = CAST(balance AS NUMERIC(10, 2))''')

# Сохранение изменений
conn.commit()

# Закрытие соединения
conn.close()
