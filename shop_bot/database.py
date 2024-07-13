import aiosqlite
from datetime import datetime, timedelta

DB_PATH = 'bot_database.sqlite'


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                status TEXT,
                created_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS failed_sends (
                user_id INTEGER PRIMARY KEY,
                fail_count INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()

# user


async def add_user_if_not_exists(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)) as cursor:
            exists = await cursor.fetchone()
            if not exists:
                await db.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
                await db.commit()
                return True
            return False


async def get_user_balance(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def update_user_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()


async def create_order(order_id, user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        created_at = datetime.now()
        await db.execute('INSERT INTO orders (order_id, user_id, amount, status, created_at) VALUES (?, ?, ?, ?, ?)',
                         (order_id, user_id, amount, 'pending', created_at))
        await db.commit()


async def get_order_by_id(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            # Получение списка имен столбцов
            column_names = [column[0] for column in cursor.description]
            # Преобразование кортежа в словарь
            order = dict(zip(column_names, row))
            return order


async def complete_order(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('completed', order_id))
        await db.commit()


async def cancel_order(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('cancelled', order_id))
        await db.commit()


# admin

async def increment_failed_send(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO failed_sends (user_id, fail_count)
            VALUES (?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET fail_count = fail_count + 1
        ''', (user_id,))
        await db.commit()


async def reset_failed_send(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE failed_sends SET fail_count = 0 WHERE user_id = ?', (user_id,))
        await db.commit()


async def get_failed_send_count(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT fail_count FROM failed_sends WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def get_user_statistics():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            total_users = (await cursor.fetchone())[0]
        async with db.execute('SELECT COUNT(*) FROM failed_sends WHERE fail_count > 4') as cursor:
            inactive_users = (await cursor.fetchone())[0]
        return total_users, inactive_users


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            return await cursor.fetchall()