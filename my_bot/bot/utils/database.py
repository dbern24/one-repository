import aiosqlite
from datetime import datetime, timedelta

DB_PATH = 'data/bot_database.sqlite'


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0,
                invited_by INTEGER,
                reward_status TEXT DEFAULT 'not_received',
                is_verified INTEGER DEFAULT 0,
                FOREIGN KEY(invited_by) REFERENCES users(user_id)
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
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        channel_id TEXT,
                        link TEXT,
                        is_active INTEGER DEFAULT 1
                    )
                ''')
        await db.commit()


# Основные запросы в базу для работы с основными функциями

async def user_exists(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)) as cursor:
            exists = await cursor.fetchone()
            return bool(exists)


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            return await cursor.fetchall()


async def add_user(user_id, invited_by=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO users (user_id, invited_by) VALUES (?, ?)', (user_id, invited_by))
        await db.commit()


async def get_user_balance(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def update_user_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()


async def get_invited_by(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT invited_by FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None


async def update_invited_by(user_id, invited_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET invited_by = ? WHERE user_id = ?', (invited_by, user_id))
        await db.commit()


# Основные запросы в базу для работы с рассылкой
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
        async with db.execute('SELECT COUNT(*) FROM failed_sends WHERE fail_count > 1') as cursor:
            inactive_users = (await cursor.fetchone())[0]
        return total_users, inactive_users


async def update_reward_status(user_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET reward_status = ? WHERE user_id = ?', (status, user_id))
        await db.commit()


async def get_reward_status(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT reward_status FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 'not_received'


async def update_verification_status(user_id, is_verified):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET is_verified = ? WHERE user_id = ?', (is_verified, user_id))
        await db.commit()


async def is_user_verified(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] == 1 if result else False


async def add_channel(name, channel_id, link):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO channels (name, channel_id, link, is_active) VALUES (?, ?, ?, 1)',
                         (name, channel_id, link))
        await db.commit()


async def update_channel_status(channel_id, is_active):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE channels SET is_active = ? WHERE channel_id = ?', (is_active, channel_id))
        await db.commit()


async def remove_channel(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
        await db.commit()


async def get_all_users_v2():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]  # Извлекаем user_id из каждого кортежа


async def get_active_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT name, channel_id, link FROM channels WHERE is_active = 1') as cursor:
            return await cursor.fetchall()


# Запросы в базу для работы с количеством рефералов


async def count_referrals(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users WHERE invited_by = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def count_referral_rewards_for_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users WHERE invited_by = ? AND reward_status = "received"', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def get_top_users_by_referrals():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT u.user_id, u.balance, COUNT(r.user_id) AS referrals
            FROM users u
            LEFT JOIN users r ON r.invited_by = u.user_id
            GROUP BY u.user_id
            ORDER BY referrals DESC, u.balance DESC
            LIMIT 10
        ''') as cursor:
            rows = await cursor.fetchall()
            top_users = []
            for row in rows:
                user_id, balance, referrals = row
                top_users.append({'user_id': user_id, 'balance': balance, 'referrals': referrals})
            return top_users


async def get_top_users_by_balance():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT u.user_id, u.balance, COUNT(r.user_id) AS referrals
            FROM users u
            LEFT JOIN users r ON r.invited_by = u.user_id
            GROUP BY u.user_id
            ORDER BY u.balance DESC, referrals DESC
            LIMIT 10
        ''') as cursor:
            rows = await cursor.fetchall()
            top_users = []
            for row in rows:
                user_id, balance, referrals = row
                top_users.append({'user_id': user_id, 'balance': balance, 'referrals': referrals})
            return top_users

