import sqlite3
from pathlib import Path


# ============================================================
# VERİTABANI AYARLARI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "prim_sistemi.db"


# ============================================================
# VERİTABANI BAĞLANTISI
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# VERİTABANI OLUŞTUR
# ============================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # MAĞAZALAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_code TEXT NOT NULL UNIQUE,

            store_name TEXT NOT NULL,

            city TEXT,

            district TEXT,

            neighborhood TEXT,

            is_active INTEGER NOT NULL DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # PERSONELLER
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_code TEXT NOT NULL UNIQUE,

            personnel_name TEXT NOT NULL,

            store_id INTEGER NOT NULL,

            title TEXT,

            is_active INTEGER NOT NULL DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (store_id)
                REFERENCES stores(id)

        )
    """)


    # ========================================================
    # HAFTALIK HEDEFLER
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_targets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            target_amount REAL NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            UNIQUE (
                store_id,
                year,
                week
            )

        )
    """)


    # ========================================================
    # NORMAL SATIŞLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS normal_sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            sales_amount REAL NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)


    # ========================================================
    # KURUMSAL SATIŞLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corporate_sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            amount REAL NOT NULL DEFAULT 0,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)


    # ========================================================
    # INSTORE SATIŞLAR
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instore_sales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            store_id INTEGER NOT NULL,

            personnel_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            amount REAL NOT NULL DEFAULT 0,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (store_id)
                REFERENCES stores(id),

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id)

        )
    """)


    # ========================================================
    # PRİM BAREMLERİ
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commission_scales (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            min_percentage REAL NOT NULL,

            max_percentage REAL,

            commission_rate REAL NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ========================================================
    # PRİM HESAPLAMA SONUÇLARI
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commission_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            personnel_id INTEGER NOT NULL,

            store_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            week INTEGER NOT NULL,

            normal_sales REAL NOT NULL DEFAULT 0,

            corporate_sales REAL NOT NULL DEFAULT 0,

            instore_sales REAL NOT NULL DEFAULT 0,

            total_personnel_sales REAL NOT NULL DEFAULT 0,

            store_turnover REAL NOT NULL DEFAULT 0,

            target_amount REAL NOT NULL DEFAULT 0,

            achievement_percentage REAL NOT NULL DEFAULT 0,

            commission_amount REAL NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (personnel_id)
                REFERENCES personnel(id),

            FOREIGN KEY (store_id)
                REFERENCES stores(id)

        )
    """)


    # ========================================================
    # İNDEKSLER
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_personnel_store
        ON personnel(store_id)
    """)


    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_normal_sales_period
        ON normal_sales(
            store_id,
            personnel_id,
            year,
            week
        )
    """)


    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_corporate_sales_period
        ON corporate_sales(
            store_id,
            personnel_id,
            year,
            week
        )
    """)


    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_instore_sales_period
        ON instore_sales(
            store_id,
            personnel_id,
            year,
            week
        )
    """)


    connection.commit()

    connection.close()


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

    cursor.execute(
        """
        INSERT INTO stores (
            store_code,
            store_name,
            city,
            district,
            neighborhood
        )

        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(store_code)
        DO UPDATE SET

            store_name = excluded.store_name,

            city = excluded.city,

            district = excluded.district,

            neighborhood = excluded.neighborhood

        """,
        (
            store_code,
            store_name,
            city,
            district,
            neighborhood
        )
    )

    connection.commit()

    connection.close()


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

    cursor.execute(
        """
        INSERT INTO personnel (
            personnel_code,
            personnel_name,
            store_id,
            title
        )

        VALUES (?, ?, ?, ?)

        ON CONFLICT(personnel_code)
        DO UPDATE SET

            personnel_name =
                excluded.personnel_name,

            store_id =
                excluded.store_id,

            title =
                excluded.title

        """,
        (
            personnel_code,
            personnel_name,
            store_id,
            title
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# MAĞAZA ARAMA
# ============================================================

def search_stores(
    search=""
):

    connection = get_connection()

    cursor = connection.cursor()


    search_value = f"%{search.strip()}%"


    cursor.execute(
        """
        SELECT
            id,
            store_code,
            store_name,
            city,
            district,
            neighborhood

        FROM stores

        WHERE is_active = 1

        AND (
            store_code LIKE ?
            OR store_name LIKE ?
        )

        ORDER BY store_code

        LIMIT 30

        """,
        (
            search_value,
            search_value
        )
    )


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


    search_value =
        f"%{search.strip()}%"


    cursor.execute(
        """
        SELECT
            id,
            personnel_code,
            personnel_name,
            store_id,
            title

        FROM personnel

        WHERE is_active = 1

        AND store_id = ?

        AND (
            personnel_code LIKE ?
            OR personnel_name LIKE ?
        )

        ORDER BY personnel_name

        LIMIT 30

        """,
        (
            store_id,
            search_value,
            search_value
        )
    )


    rows =
        cursor.fetchall()


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


    cursor.execute(
        """
        INSERT INTO corporate_sales (

            store_id,

            personnel_id,

            year,

            week,

            amount,

            description

        )

        VALUES (?, ?, ?, ?, ?, ?)

        """,
        (
            store_id,
            personnel_id,
            year,
            week,
            amount,
            description
        )
    )


    connection.commit()

    record_id = cursor.lastrowid


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


    cursor.execute(
        """
        INSERT INTO instore_sales (

            store_id,

            personnel_id,

            year,

            week,

            amount,

            description

        )

        VALUES (?, ?, ?, ?, ?, ?)

        """,
        (
            store_id,
            personnel_id,
            year,
            week,
            amount,
            description
        )
    )


    connection.commit()

    record_id =
        cursor.lastrowid


    connection.close()


    return record_id


# ============================================================
# VERİTABANI TESTİ
# ============================================================

if __name__ == "__main__":

    init_database()

    print(
        "Veritabanı başarıyla oluşturuldu:"
    )

    print(
        DATABASE_PATH
    )