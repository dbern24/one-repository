import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.curcor = self.connection.cursor()

    def user_exists(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT * FROM 'users' WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, referrer_id):
        with self.connection:
            if referrer_id != 0:
                return self.curcor.execute("INSERT INTO 'users' ('user_id', 'referrer_id') VALUES (?,?)",
                                           (user_id, referrer_id,))
            else:
                return self.curcor.execute("INSERT INTO 'users' ('user_id') VALUES (?)", (user_id,))

    def get_referrer_id(self, user_id):
        # Выполняем запрос SELECT для получения referrer_id по user_id
        self.curcor.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
        result = self.curcor.fetchone()  # Получаем первую строку результата

        if result:
            return result[0]  # Возвращаем referrer_id
        else:
            return None  # Если пользователь не найден, возвращаем None

    def count_reeferals(self, user_id):
        with self.connection:
            result = self.curcor.execute("SELECT COUNT(id) as count FROM 'users' WHERE referrer_id = ?",
                                         (user_id,)).fetchone()
            if result:
                return result[0]
            else:
                return 0

    def count_total_users(self):
        with self.connection:
            result = self.curcor.execute("SELECT COUNT(id) as count FROM 'users'").fetchone()
            if result:
                return result[0]
            else:
                return 0

    # пошла жара, баланс.

    def get_balance(self, user_id):
        self.curcor.execute("SELECT balance FROM 'users' WHERE user_id=?", (user_id,))
        result = self.curcor.fetchone()
        if result:
            return round(result[0], 2)  # Округляем до двух десятичных знаков
        else:
            return None

    def add_to_balance(self, user_id, amount):
        current_balance = self.get_balance(user_id)
        if current_balance is not None:
            new_balance = round(current_balance + amount, 2)  # Округляем новый баланс
            self.curcor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
            self.connection.commit()

    def subtract_from_balance(self, user_id, amount):
        current_balance = self.get_balance(user_id)
        if current_balance is not None:
            new_balance = round(current_balance - amount, 2)  # Округляем новый баланс
            if new_balance >= 0:
                self.curcor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
                self.connection.commit()
                return True
            else:
                return False
        else:
            return False

    def get_top5_users(self):
        self.curcor.execute("SELECT user_id, ROUND(balance, 2) FROM 'users' ORDER BY balance DESC LIMIT 20")
        top_users = self.curcor.fetchall()
        return top_users

    def get_refreward(self, user_id):
        self.curcor.execute("SELECT refreward FROM users WHERE user_id=?", (user_id,))
        result = self.curcor.fetchone()
        if result:
            return result[0] == 'yes'
        else:
            return None

    def update_refreward(self, user_id, value):
        with self.connection:
            self.curcor.execute("UPDATE users SET refreward=? WHERE user_id=?", (value, user_id))
            self.connection.commit()

    def count_referral_rewards_for_user(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ? AND refreward = 'yes'",
                                             (user_id,)).fetchone()
            if result:
                return result[0]
            else:
                return 0




