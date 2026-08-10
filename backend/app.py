from flask import Flask, jsonify, request, render_template, redirect, url_for
from pathlib import Path
import sys

# ============================================================
# DOSYA YOLLARI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

# ============================================================
# DATABASE MODÜLÜ
# ============================================================

sys.path.insert(0, str(BASE_DIR))

from database import (
    init_database,
    search_stores,
    search_personnel,
    create_corporate_sale,
    create_instore_sale
)

# ============================================================
# FLASK UYGULAMASI
# ============================================================

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static"
)

# ============================================================
# VERİTABANINI BAŞLAT
# ============================================================

init_database()

# ============================================================
# ANA SAYFA
# ============================================================

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    dashboard_file = FRONTEND_DIR / "dashboard.html"

    if dashboard_file.exists():
        return render_template("dashboard.html")

    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Prim Hesaplama Sistemi</title>
    </head>
    <body>

        <h1>Prim Hesaplama Sistemi</h1>

        <p>Dashboard dosyası henüz oluşturulmadı.</p>

        <p>Flask sistemi çalışıyor.</p>

    </body>
    </html>
    """


# ============================================================
# KURUMSAL SATIŞ SAYFASI
# ============================================================

@app.route("/corporate-sales")
def corporate_sales_page():
    return render_template("corporate_sales.html")


# ============================================================
# INSTORE SATIŞ SAYFASI
# ============================================================

@app.route("/instore-sales")
def instore_sales_page():
    return render_template("instore_sales.html")


# ============================================================
# VERİ AKTARMA SAYFASI
# ============================================================

@app.route("/import")
def import_page():
    return render_template("import.html")


# ============================================================
# MAĞAZA ARAMA API
# ============================================================

@app.route("/api/stores/search", methods=["GET"])
def api_search_stores():

    search = request.args.get(
        "q",
        ""
    ).strip()

    try:

        stores = search_stores(search)

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
# PERSONEL ARAMA API
# ============================================================

@app.route("/api/personnel/search", methods=["GET"])
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
# KURUMSAL SATIŞ EKLEME API
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

        store_id = int(
            data["store_id"]
        )

        personnel_id = int(
            data["personnel_id"]
        )

        year = int(
            data["year"]
        )

        week = int(
            data["week"]
        )

        amount = float(
            data["amount"]
        )

        description = data.get(
            "description"
        )

        record_id = create_corporate_sale(
            store_id=store_id,
            personnel_id=personnel_id,
            year=year,
            week=week,
            amount=amount,
            description=description
        )

        return jsonify({
            "success": True,
            "message": "Kurumsal satış başarıyla eklendi.",
            "id": record_id
        })

    except KeyError as error:

        return jsonify({
            "success": False,
            "message": (
                f"Eksik alan: {error}"
            )
        }), 400

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Sayısal alanları kontrol edin."
        }), 400

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# INSTORE SATIŞ EKLEME API
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

        store_id = int(
            data["store_id"]
        )

        personnel_id = int(
            data["personnel_id"]
        )

        year = int(
            data["year"]
        )

        week = int(
            data["week"]
        )

        amount = float(
            data["amount"]
        )

        description = data.get(
            "description"
        )

        record_id = create_instore_sale(
            store_id=store_id,
            personnel_id=personnel_id,
            year=year,
            week=week,
            amount=amount,
            description=description
        )

        return jsonify({
            "success": True,
            "message": "InStore satışı başarıyla eklendi.",
            "id": record_id
        })

    except KeyError as error:

        return jsonify({
            "success": False,
            "message": (
                f"Eksik alan: {error}"
            )
        }), 400

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Sayısal alanları kontrol edin."
        }), 400

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ============================================================
# SAĞLIK / DURUM KONTROLÜ
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
# 404 HATASI
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

        <p>
            İstenen sayfa mevcut değil.
        </p>

        <a href="/dashboard">
            Dashboard'a dön
        </a>

    </body>
    </html>
    """, 404


# ============================================================
# GENEL HATA YAKALAMA
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "success": False,
        "message": "Sunucu tarafında bir hata oluştu."
    }), 500


# ============================================================
# UYGULAMAYI ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
