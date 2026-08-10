from flask import Flask, jsonify, request, render_template, redirect, url_for
from pathlib import Path
import sys
import csv
import io

# ============================================================
# DOSYA YOLLARI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

# ============================================================
# DATABASE
# ============================================================

sys.path.insert(0, str(BASE_DIR))

from database import (
    init_database,
    get_connection,
    search_stores,
    search_personnel,
    create_store,
    create_personnel,
    create_sale,
    create_corporate_sale,
    create_instore_sale,
    save_target
)

# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static"
)

init_database()


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def clean_value(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_number(value):
    """
    Excel'den gelen satış/hedef tutarlarını sayıya çevirir.
    Örnek:
    125000
    125.000
    125.000,50
    125000,50
    """

    value = clean_value(value)

    if not value:
        return 0.0

    value = value.replace("₺", "")
    value = value.replace("TL", "")
    value = value.replace(" ", "")

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "")
            value = value.replace(",", ".")
        else:
            value = value.replace(",", "")

    elif "," in value:
        value = value.replace(",", ".")

    elif value.count(".") > 1:
        value = value.replace(".", "")

    try:
        return float(value)
    except ValueError:
        raise ValueError(
            f"Geçersiz sayısal değer: {value}"
        )


def read_uploaded_file(file):
    """
    Basit CSV aktarımı için yardımcı fonksiyon.
    Excel tarafındaki dosya CSV olarak gönderilirse çalışır.
    """

    if file is None:
        raise ValueError("Dosya gönderilmedi.")

    raw = file.read()

    if not raw:
        raise ValueError("Dosya boş.")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1254")

    return list(
        csv.DictReader(
            io.StringIO(text)
        )
    )


# ============================================================
# ANA SAYFA
# ============================================================

@app.route("/")
def index():
    return redirect(
        url_for("dashboard")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    dashboard_file = FRONTEND_DIR / "dashboard.html"

    if dashboard_file.exists():
        return render_template(
            "dashboard.html"
        )

    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Prim Hesaplama Sistemi</title>
    </head>
    <body>

        <h1>Prim Hesaplama Sistemi</h1>

        <p>Dashboard dosyası bulunamadı.</p>

    </body>
    </html>
    """


# ============================================================
# VERİ AKTARMA
# ============================================================

@app.route("/import")
@app.route("/veri-aktarma")
def import_page():
    return render_template(
        "import.html"
    )


# ============================================================
# KURUMSAL SATIŞ SAYFASI
# ============================================================

@app.route("/corporate-sales")
def corporate_sales_page():
    return render_template(
        "corporate_sales.html"
    )


# ============================================================
# INSTORE SATIŞ SAYFASI
# ============================================================

@app.route("/instore-sales")
def instore_sales_page():
    return render_template(
        "instore_sales.html"
    )


# ============================================================
# MAĞAZA ARAMA
# ============================================================

@app.route(
    "/api/stores/search",
    methods=["GET"]
)
def api_search_stores():

    search = request.args.get(
        "q",
        ""
    ).strip()

    try:

        stores = search_stores(
            search
        )

        return jsonify({
            "success": True,
            "stores": stores
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error),
            "stores": []
        }), 500


# ============================================================
# PERSONEL ARAMA
# ============================================================

@app.route(
    "/api/personnel/search",
    methods=["GET"]
)
def api_search_personnel():

    store_id = request.args.get(
        "store_id",
        type=int
    )

    search = request.args.get(
        "q",
        ""
    ).strip()

    if not store_id:

        return jsonify({
            "success": False,
            "message": "store_id gereklidir.",
            "personnel": []
        }), 400

    try:

        personnel = search_personnel(
            store_id,
            search
        )

        return jsonify({
            "success": True,
            "personnel": personnel
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error),
            "personnel": []
        }), 500


# ============================================================
# MAĞAZA EXCEL AKTARIMI
# ============================================================

@app.route(
    "/api/import/stores",
    methods=["POST"]
)
def import_stores():

    try:

        file = request.files.get(
            "file"
        )

        rows = read_uploaded_file(
            file
        )

        created = 0
        updated = 0

        connection = get_connection()
        cursor = connection.cursor()

        for row in rows:

            store_code = clean_value(
                row.get("Mağaza Kodu")
                or row.get("magaza_kodu")
                or row.get("store_code")
            )

            store_name = clean_value(
                row.get("Mağaza Adı")
                or row.get("magaza_adi")
                or row.get("store_name")
            )

            if not store_code:
                continue

            if not store_name:
                continue

            cursor.execute(
                """
                SELECT id
                FROM stores
                WHERE store_code = ?
                """,
                (store_code,)
            )

            existing = cursor.fetchone()

            if existing:

                cursor.execute(
                    """
                    UPDATE stores
                    SET store_name = ?
                    WHERE store_code = ?
                    """,
                    (
                        store_name,
                        store_code
                    )
                )

                updated += 1

            else:

                cursor.execute(
                    """
                    INSERT INTO stores (
                        store_code,
                        store_name
                    )
                    VALUES (?, ?)
                    """,
                    (
                        store_code,
                        store_name
                    )
                )

                created += 1

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Mağaza aktarımı tamamlandı.",
            "created": created,
            "updated": updated
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# PERSONEL EXCEL AKTARIMI
# ============================================================

@app.route(
    "/api/import/personnel",
    methods=["POST"]
)
def import_personnel():

    try:

        file = request.files.get(
            "file"
        )

        rows = read_uploaded_file(
            file
        )

        created = 0
        updated = 0
        skipped = 0

        connection = get_connection()
        cursor = connection.cursor()

        for row in rows:

            store_code = clean_value(
                row.get("Mağaza Kodu")
                or row.get("magaza_kodu")
                or row.get("store_code")
            )

            personnel_code = clean_value(
                row.get("Personel Kodu")
                or row.get("personel_kodu")
                or row.get("personnel_code")
            )

            personnel_name = clean_value(
                row.get("Personel Adı")
                or row.get("personel_adi")
                or row.get("personnel_name")
            )

            if (
                not store_code
                or not personnel_code
                or not personnel_name
            ):
                skipped += 1
                continue

            cursor.execute(
                """
                SELECT id
                FROM stores
                WHERE store_code = ?
                """,
                (store_code,)
            )

            store = cursor.fetchone()

            if not store:
                skipped += 1
                continue

            store_id = store["id"]

            cursor.execute(
                """
                SELECT id
                FROM personnel
                WHERE personnel_code = ?
                """,
                (personnel_code,)
            )

            existing = cursor.fetchone()

            if existing:

                cursor.execute(
                    """
                    UPDATE personnel
                    SET personnel_name = ?,
                        store_id = ?
                    WHERE personnel_code = ?
                    """,
                    (
                        personnel_name,
                        store_id,
                        personnel_code
                    )
                )

                updated += 1

            else:

                cursor.execute(
                    """
                    INSERT INTO personnel (
                        personnel_code,
                        personnel_name,
                        store_id
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        personnel_code,
                        personnel_name,
                        store_id
                    )
                )

                created += 1

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Personel aktarımı tamamlandı.",
            "created": created,
            "updated": updated,
            "skipped": skipped
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# HEDEF EXCEL AKTARIMI
# ============================================================

@app.route(
    "/api/import/targets",
    methods=["POST"]
)
def import_targets():

    try:

        file = request.files.get(
            "file"
        )

        year = request.form.get(
            "year",
            type=int
        )

        week = request.form.get(
            "week",
            type=int
        )

        if not year or not week:
            return jsonify({
                "success": False,
                "message": "Yıl ve hafta seçilmelidir."
            }), 400

        rows = read_uploaded_file(
            file
        )

        count = 0
        skipped = 0

        for row in rows:

            store_code = clean_value(
                row.get("Mağaza Kodu")
                or row.get("magaza_kodu")
                or row.get("store_code")
            )

            target = row.get(
                "Hedef"
            )

            if not store_code or target is None:
                skipped += 1
                continue

            target_amount = normalize_number(
                target
            )

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id
                FROM stores
                WHERE store_code = ?
                """,
                (store_code,)
            )

            store = cursor.fetchone()

            if not store:
                connection.close()
                skipped += 1
                continue

            save_target(
                store_id=store["id"],
                year=year,
                week=week,
                target_amount=target_amount
            )

            connection.close()

            count += 1

        return jsonify({
            "success": True,
            "message": "Hedef aktarımı tamamlandı.",
            "count": count,
            "skipped": skipped
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# PERSONEL BİREYSEL NORMAL SATIŞ EXCEL AKTARIMI
# ============================================================

@app.route(
    "/api/import/sales",
    methods=["POST"]
)
def import_sales():

    try:

        file = request.files.get(
            "file"
        )

        year = request.form.get(
            "year",
            type=int
        )

        week = request.form.get(
            "week",
            type=int
        )

        if not year or not week:
            return jsonify({
                "success": False,
                "message": "Yıl ve hafta seçilmelidir."
            }), 400

        rows = read_uploaded_file(
            file
        )

        count = 0
        skipped = 0

        connection = get_connection()
        cursor = connection.cursor()

        for row in rows:

            store_code = clean_value(
                row.get("Mağaza Kodu")
                or row.get("magaza_kodu")
                or row.get("store_code")
            )

            personnel_code = clean_value(
                row.get("Personel Kodu")
                or row.get("personel_kodu")
                or row.get("personnel_code")
            )

            amount = row.get(
                "Toplam Satış"
            )

            if amount is None:

                amount = row.get(
                    "Bireysel Satış"
                )

            if (
                not store_code
                or not personnel_code
                or amount is None
            ):
                skipped += 1
                continue

            amount = normalize_number(
                amount
            )

            cursor.execute(
                """
                SELECT id
                FROM stores
                WHERE store_code = ?
                """,
                (store_code,)
            )

            store = cursor.fetchone()

            if not store:
                skipped += 1
                continue

            store_id = store["id"]

            cursor.execute(
                """
                SELECT id
                FROM personnel
                WHERE personnel_code = ?
                  AND store_id = ?
                """,
                (
                    personnel_code,
                    store_id
                )
            )

            personnel = cursor.fetchone()

            if not personnel:
                skipped += 1
                continue

            personnel_id = personnel["id"]

            cursor.execute(
                """
                SELECT id
                FROM sales
                WHERE year = ?
                  AND week = ?
                  AND store_id = ?
                  AND personnel_id = ?
                """,
                (
                    year,
                    week,
                    store_id,
                    personnel_id
                )
            )

            existing = cursor.fetchone()

            if existing:

                cursor.execute(
                    """
                    UPDATE sales
                    SET amount = ?
                    WHERE id = ?
                    """,
                    (
                        amount,
                        existing["id"]
                    )
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO sales (
                        year,
                        week,
                        store_id,
                        personnel_id,
                        amount
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        year,
                        week,
                        store_id,
                        personnel_id,
                        amount
                    )
                )

            count += 1

        connection.commit()
        connection.close()

        return jsonify({
            "success": True,
            "message": (
                "Personel bireysel "
                "normal satış aktarımı tamamlandı."
            ),
            "count": count,
            "skipped": skipped
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# KURUMSAL SATIŞ EKLE
# ============================================================

@app.route(
    "/api/corporate-sales",
    methods=["POST"]
)
def api_create_corporate_sale():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        record_id = create_corporate_sale(
            store_id=int(
                data["store_id"]
            ),
            personnel_id=int(
                data["personnel_id"]
            ),
            year=int(
                data["year"]
            ),
            week=int(
                data["week"]
            ),
            amount=float(
                data["amount"]
            ),
            description=data.get(
                "description"
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Kurumsal satış "
                "başarıyla eklendi."
            ),
            "id": record_id
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# INSTORE SATIŞ EKLE
# ============================================================

@app.route(
    "/api/instore-sales",
    methods=["POST"]
)
def api_create_instore_sale():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        record_id = create_instore_sale(
            store_id=int(
                data["store_id"]
            ),
            personnel_id=int(
                data["personnel_id"]
            ),
            year=int(
                data["year"]
            ),
            week=int(
                data["week"]
            ),
            amount=float(
                data["amount"]
            ),
            description=data.get(
                "description"
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "InStore satış "
                "başarıyla eklendi."
            ),
            "id": record_id
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


# ============================================================
# SAĞLIK KONTROLÜ
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health_check():

    return jsonify({
        "success": True,
        "message": (
            "Prim hesaplama sistemi çalışıyor."
        )
    })


# ============================================================
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Sayfa Bulunamadı</title>
    </head>
    <body>

        <h1>Sayfa bulunamadı</h1>

        <p>İstenen sayfa mevcut değil.</p>

        <a href="/dashboard">
            Dashboard'a dön
        </a>

    </body>
    </html>
    """, 404


# ============================================================
# 500
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "message": (
            "Sunucu tarafında bir hata oluştu."
        )
    }), 500


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
