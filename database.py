import sqlite3
from datetime import datetime


DB_NAME = "merrycoin.db"


# =========================
# DATABASE CONNECTION
# =========================

def connect():
    return sqlite3.connect(DB_NAME)


# =========================
# CREATE TABLES
# =========================

def init_db():

    db = connect()
    cursor = db.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            username TEXT,
            coins INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            referred_by INTEGER,
            last_daily TEXT DEFAULT '',
            created_at TEXT
        )
    """)

    # WITHDRAWALS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            method TEXT,
            account TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)

    db.commit()
    db.close()


# =========================
# CREATE USER
# =========================

def create_user(
    user_id,
    first_name,
    username=None,
    referred_by=None
):

    db = connect()
    cursor = db.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    existing = cursor.fetchone()

    if not existing:

        cursor.execute("""
            INSERT INTO users (
                user_id,
                first_name,
                username,
                coins,
                referrals,
                referred_by,
                last_daily,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            first_name,
            username,
            0,
            0,
            referred_by,
            "",
            datetime.now().isoformat()
        ))

    else:

        cursor.execute("""
            UPDATE users
            SET first_name=?,
                username=?
            WHERE user_id=?
        """, (
            first_name,
            username,
            user_id
        ))

    db.commit()
    db.close()


# =========================
# GET USER
# =========================

def get_user(user_id):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            first_name,
            username,
            coins,
            referrals,
            referred_by,
            last_daily,
            created_at
        FROM users
        WHERE user_id=?
    """, (user_id,))

    user = cursor.fetchone()

    db.close()

    return user


# =========================
# ADD COINS
# =========================

def add_coins(user_id, amount):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET coins = coins + ?
        WHERE user_id=?
    """, (
        amount,
        user_id
    ))

    db.commit()

    cursor.execute("""
        SELECT coins
        FROM users
        WHERE user_id=?
    """, (user_id,))

    result = cursor.fetchone()

    db.close()

    if result:
        return result[0]

    return 0


# =========================
# REMOVE COINS
# =========================

def remove_coins(user_id, amount):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET coins = coins - ?
        WHERE user_id=?
        AND coins >= ?
    """, (
        amount,
        user_id,
        amount
    ))

    db.commit()

    success = cursor.rowcount > 0

    db.close()

    return success


# =========================
# SET DAILY BONUS
# =========================

def set_daily(user_id, date):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET last_daily=?
        WHERE user_id=?
    """, (
        date,
        user_id
    ))

    db.commit()
    db.close()


# =========================
# ADD REFERRAL
# =========================

def add_referral(user_id):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET referrals = referrals + 1
        WHERE user_id=?
    """, (user_id,))

    db.commit()
    db.close()


# =========================
# GET ALL USERS
# =========================

def get_all_users():

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            first_name,
            username,
            coins,
            referrals,
            referred_by,
            last_daily,
            created_at
        FROM users
        ORDER BY coins DESC
    """)

    users = cursor.fetchall()

    db.close()

    return users


# =========================
# GET TOP USERS
# =========================

def get_top_users(limit=10):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            first_name,
            username,
            coins
        FROM users
        ORDER BY coins DESC
        LIMIT ?
    """, (limit,))

    users = cursor.fetchall()

    db.close()

    return users


# =========================
# USER COUNT
# =========================

def get_user_count():

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    result = cursor.fetchone()

    db.close()

    return result[0] if result else 0


# =========================
# TOTAL COINS
# =========================

def get_total_coins():

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(coins), 0)
        FROM users
    """)

    result = cursor.fetchone()

    db.close()

    return result[0] if result else 0


# =========================
# CREATE WITHDRAWAL
# =========================

def create_withdrawal(
    user_id,
    amount,
    method,
    account
):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO withdrawals (
            user_id,
            amount,
            method,
            account,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        amount,
        method,
        account,
        "pending",
        datetime.now().isoformat()
    ))

    withdrawal_id = cursor.lastrowid

    db.commit()
    db.close()

    return withdrawal_id


# =========================
# GET WITHDRAWALS
# =========================

def get_withdrawals(status=None):

    db = connect()
    cursor = db.cursor()

    if status:

        cursor.execute("""
            SELECT
                id,
                user_id,
                amount,
                method,
                account,
                status,
                created_at
            FROM withdrawals
            WHERE status=?
            ORDER BY id DESC
        """, (status,))

    else:

        cursor.execute("""
            SELECT
                id,
                user_id,
                amount,
                method,
                account,
                status,
                created_at
            FROM withdrawals
            ORDER BY id DESC
        """)

    withdrawals = cursor.fetchall()

    db.close()

    return withdrawals


# =========================
# UPDATE WITHDRAWAL STATUS
# =========================

def update_withdrawal_status(
    withdrawal_id,
    status
):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE withdrawals
        SET status=?
        WHERE id=?
    """, (
        status,
        withdrawal_id
    ))

    db.commit()

    success = cursor.rowcount > 0

    db.close()

    return success


# =========================
# GET USER WITHDRAWALS
# =========================

def get_user_withdrawals(user_id):

    db = connect()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            id,
            amount,
            method,
            account,
            status,
            created_at
        FROM withdrawals
        WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,))

    withdrawals = cursor.fetchall()

    db.close()

    return withdrawals


# =========================
# INITIALIZE DATABASE
# =========================

init_db()
