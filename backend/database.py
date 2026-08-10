import sqlite3
from pathlib import Path


# ============================================================
# DOSYA YOLLARI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "prim_hesaplama.db"


# ============================================================
# VERİTABANI BAĞLANTISI
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# VERİTABANINI OLUŞTUR
# ============================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # MAĞAZALAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_code TEXT NOT NULL UNIQUE,

            store_name TEXT NOT NULL,

            city TEXT,

            district TEXT,

            neighborhood TEXT,

            active INTEGER NOT NULL DEFAULT 1

        )
    """)

    # --------------------------------------------------------
    # PERSONELLER
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_code TEXT NOT NULL UNIQUE,

            personnel_name TEXT NOT NULL,

            store_id INTEGER NOT NULL,

            title TEXT,

            active INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (store_id)
                REFERENCES stores(id)

        )
    """)

    # --------------------------------------------------------
    # NORMAL SATIŞLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            amount REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)

    # --------------------------------------------------------
    # KURUMSAL SATIŞLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corporate_sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            amount REAL NOT NULL DEFAULT 0,

            description TEXT,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)

    # --------------------------------------------------------
    # INSTORE SATIŞLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instore_sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            amount REAL NOT NULL DEFAULT 0,

            description TEXT,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)

    # --------------------------------------------------------
    # HEDEFLER
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            store_id INTEGER NOT NULL,

            target_amount REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            UNIQUE (
                year,
                week,
                store_id
            )

        )
    """)

    # --------------------------------------------------------
    # PRİM BAREMLERİ
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commission_bands (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            minimum_percentage REAL NOT NULL,

            maximum_percentage REAL,

            commission_rate REAL NOT NULL DEFAULT 0

        )
    """)

    # --------------------------------------------------------
    # İNDEKSLER
    # --------------------------------------------------------

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_personnel_store
        ON personnel(store_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_sales_store_week
        ON sales(store_id, year, week)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_sales_personnel_week
        ON sales(personnel_id, year, week)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_corporate_store_week
        ON corporate_sales(store_id, year, week)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_corporate_personnel_week
        ON corporate_sales(personnel_id, year, week)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_instore_store_week
        ON instore_sales(store_id, year, week)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_instore_personnel_week
        ON instore_sales(personnel_id, year, week)
    """)

    connection.commit()

    connection.close()


# ============================================================
# MAĞAZA ARAMA
# ============================================================

def search_stores(search=""):

    connection = get_connection()

    cursor = connection.cursor()

    search_value = f"%{search.strip()}%"

    cursor.execute("""
        SELECT
            id,
            store_code,
            store_name,
            city,
            district,
            neighborhood
        FROM stores
        WHERE active = 1
          AND (
                store_code LIKE ?
                OR store_name LIKE ?
                OR city LIKE ?
                OR district LIKE ?
                OR neighborhood LIKE ?
          )
        ORDER BY store_code
        LIMIT 50
    """, (
        search_value,
        search_value,
        search_value,
        search_value,
        search_value
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# PERSONEL ARAMA
# ============================================================

def search_personnel(
    store_id,
    search=""
):

    connection = get_connection()

    cursor = connection.cursor()

    search_value = f"%{search.strip()}%"

    cursor.execute("""
        SELECT
            id,
            personnel_code,
            personnel_name,
            store_id,
            title
        FROM personnel
        WHERE active = 1
          AND store_id = ?
          AND (
                personnel_code LIKE ?
                OR personnel_name LIKE ?
          )
        ORDER BY personnel_name
        LIMIT 50
    """, (
        store_id,
        search_value,
        search_value
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# KURUMSAL SATIŞ EKLE
# ============================================================

def create_corporate_sale(
    store_id,
    personnel_id,
    year,
    week,
    amount,
    description=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO corporate_sales (
            year,
            week,
            store_id,
            personnel_id,
            amount,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        year,
        week,
        store_id,
        personnel_id,
        amount,
        description
    ))

    record_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return record_id


# ============================================================
# INSTORE SATIŞ EKLE
# ============================================================

def create_instore_sale(
    store_id,
    personnel_id,
    year,
    week,
    amount,
    description=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO instore_sales (
            year,
            week,
            store_id,
            personnel_id,
            amount,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        year,
        week,
        store_id,
        personnel_id,
        amount,
        description
    ))

    record_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return record_id


# ============================================================
# NORMAL SATIŞ EKLE
# ============================================================

def create_sale(
    store_id,
    personnel_id,
    year,
    week,
    amount
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sales (
            year,
            week,
            store_id,
            personnel_id,
            amount
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        year,
        week,
        store_id,
        personnel_id,
        amount
    ))

    record_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return record_id


# ============================================================
# MAĞAZA EKLE
# ============================================================

def create_store(
    store_code,
    store_name,
    city=None,
    district=None,
    neighborhood=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stores (
            store_code,
            store_name,
            city,
            district,
            neighborhood
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        store_code,
        store_name,
        city,
        district,
        neighborhood
    ))

    record_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return record_id


# ============================================================
# PERSONEL EKLE
# ============================================================

def create_personnel(
    personnel_code,
    personnel_name,
    store_id,
    title=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO personnel (
            personnel_code,
            personnel_name,
            store_id,
            title
        )
        VALUES (?, ?, ?, ?)
    """, (
        personnel_code,
        personnel_name,
        store_id,
        title
    ))

    record_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return record_id


# ============================================================
# NORMAL SATIŞ TOPLAMI
# ============================================================

def get_normal_sales_total(
    store_id,
    personnel_id,
    year,
    week
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM sales
        WHERE store_id = ?
          AND personnel_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        personnel_id,
        year,
        week
    ))

    result = cursor.fetchone()[0]

    connection.close()

    return float(result)


# ============================================================
# KURUMSAL SATIŞ TOPLAMI
# ============================================================

def get_corporate_sales_total(
    store_id,
    personnel_id,
    year,
    week
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM corporate_sales
        WHERE store_id = ?
          AND personnel_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        personnel_id,
        year,
        week
    ))

    result = cursor.fetchone()[0]

    connection.close()

    return float(result)


# ============================================================
# INSTORE SATIŞ TOPLAMI
# ============================================================

def get_instore_sales_total(
    store_id,
    personnel_id,
    year,
    week
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM instore_sales
        WHERE store_id = ?
          AND personnel_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        personnel_id,
        year,
        week
    ))

    result = cursor.fetchone()[0]

    connection.close()

    return float(result)


# ============================================================
# PERSONEL TOPLAM SATIŞI
#
# NORMAL + KURUMSAL + INSTORE
# ============================================================

def get_personnel_total_sales(
    store_id,
    personnel_id,
    year,
    week
):

    normal_sales = get_normal_sales_total(
        store_id,
        personnel_id,
        year,
        week
    )

    corporate_sales = get_corporate_sales_total(
        store_id,
        personnel_id,
        year,
        week
    )

    instore_sales = get_instore_sales_total(
        store_id,
        personnel_id,
        year,
        week
    )

    return (
        normal_sales
        + corporate_sales
        + instore_sales
    )


# ============================================================
# MAĞAZA CİROSU
#
# NORMAL + KURUMSAL + INSTORE
# ============================================================

def get_store_total_sales(
    store_id,
    year,
    week
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM sales
        WHERE store_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        year,
        week
    ))

    normal_sales = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM corporate_sales
        WHERE store_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        year,
        week
    ))

    corporate_sales = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(amount),
                0
            )
        FROM instore_sales
        WHERE store_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        year,
        week
    ))

    instore_sales = cursor.fetchone()[0]

    connection.close()

    return float(
        normal_sales
        + corporate_sales
        + instore_sales
    )


# ============================================================
# HEDEF EKLE / GÜNCELLE
# ============================================================

def save_target(
    store_id,
    year,
    week,
    target_amount
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO targets (
            year,
            week,
            store_id,
            target_amount
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT (
            year,
            week,
            store_id
        )

        DO UPDATE SET
            target_amount = excluded.target_amount
    """, (
        year,
        week,
        store_id,
        target_amount
    ))

    connection.commit()

    connection.close()


# ============================================================
# HEDEF GETİR
# ============================================================

def get_target(
    store_id,
    year,
    week
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            target_amount
        FROM targets
        WHERE store_id = ?
          AND year = ?
          AND week = ?
    """, (
        store_id,
        year,
        week
    ))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return 0.0

    return float(
        row["target_amount"]
    )


# ============================================================
# MAĞAZA CİROSU + HEDEF
# ============================================================

def get_store_performance(
    store_id,
    year,
    week
):

    sales = get_store_total_sales(
        store_id,
        year,
        week
    )

    target = get_target(
        store_id,
        year,
        week
    )

    if target > 0:

        achievement_percentage = (
            sales / target
        ) * 100

    else:

        achievement_percentage = 0

    return {
        "sales": sales,
        "target": target,
        "achievement_percentage":
            achievement_percentage
    }
