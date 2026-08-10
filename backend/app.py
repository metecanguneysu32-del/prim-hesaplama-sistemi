from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    redirect,
    url_for
)

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

sys.path.insert(
    0,
    str(BASE_DIR)
)

from database import (
    init_database,
    search_stores,
    search_personnel,
    create_corporate_sale,
    create_instore_sale
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


# ============================================================
# VERİTABANINI BAŞLAT
# ============================================================

init_database()


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

    dashboard_file = (
        FRONTEND_DIR /
        "dashboard.html"
    )

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

        <h1>
            Prim Hesaplama Sistemi
        </h1>

        <p>
            Dashboard dosyası henüz oluşturulmadı.
        </p>

        <p>
            Sistem çalışıyor.
        </p>

    </body>
    </html>
    """


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
# MAĞAZA ARAMA API
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

            "message":
                f"Mağaza araması sırasında hata oluştu: {error}"

        }), 500


# ============================================================
# PERSONEL ARAMA API
# ============================================================

@app.route(
    "/api/personnel/search",
    methods=["GET"]
)
def api_search_personnel():

    store_id =
        request.args.get(
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

            "message":
                "Mağaza seçilmedi."

        }), 400


    try:

        personnel = search_personnel(
            store_id,
            search
        )


        return jsonify({

            "success": True,

            "personnel":
                personnel

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                f"Personel araması sırasında hata oluştu: {error}"

        }), 500


# ============================================================
# KURUMSAL SATIŞ KAYDETME API
# ============================================================

@app.route(
    "/api/corporate-sales",
    methods=["POST"]
)
def api_create_corporate_sale():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Gönderilen veri okunamadı."

        }), 400


    required_fields = [

        "year",

        "week",

        "store_id",

        "personnel_id",

        "amount"

    ]


    for field in required_fields:

        if field not in data:

            return jsonify({

                "success": False,

                "message":
                    f"{field} alanı eksik."

            }), 400


    try:

        year = int(
            data["year"]
        )

        week = int(
            data["week"]
        )

        store_id = int(
            data["store_id"]
        )

        personnel_id = int(
            data["personnel_id"]
        )

        amount = float(
            data["amount"]
        )

        description = (
            data.get(
                "description"
            )
            or None
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Gönderilen veriler geçersiz."

        }), 400


    if year < 2000:

        return jsonify({

            "success": False,

            "message":
                "Geçersiz yıl."

        }), 400


    if week < 1 or week > 53:

        return jsonify({

            "success": False,

            "message":
                "Hafta 1 ile 53 arasında olmalıdır."

        }), 400


    if amount <= 0:

        return jsonify({

            "success": False,

            "message":
                "Satış tutarı 0'dan büyük olmalıdır."

        }), 400


    try:

        record_id =
            create_corporate_sale(

                store_id=store_id,

                personnel_id=personnel_id,

                year=year,

                week=week,

                amount=amount,

                description=description

            )


        return jsonify({

            "success": True,

            "message":
                "Kurumsal satış başarıyla kaydedildi.",

            "id":
                record_id

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                f"Kurumsal satış kaydedilemedi: {error}"

        }), 500


# ============================================================
# INSTORE SATIŞ KAYDETME API
# ============================================================

@app.route(
    "/api/instore-sales",
    methods=["POST"]
)
def api_create_instore_sale():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Gönderilen veri okunamadı."

        }), 400


    required_fields = [

        "year",

        "week",

        "store_id",

        "personnel_id",

        "amount"

    ]


    for field in required_fields:

        if field not in data:

            return jsonify({

                "success": False,

                "message":
                    f"{field} alanı eksik."

            }), 400


    try:

        year = int(
            data["year"]
        )

        week = int(
            data["week"]
        )

        store_id = int(
            data["store_id"]
        )

        personnel_id = int(
            data["personnel_id"]
        )

        amount = float(
            data["amount"]
        )

        description = (
            data.get(
                "description"
            )
            or None
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Gönderilen veriler geçersiz."

        }), 400


    if year < 2000:

        return jsonify({

            "success": False,

            "message":
                "Geçersiz yıl."

        }), 400


    if week < 1 or week > 53:

        return jsonify({

            "success": False,

            "message":
                "Hafta 1 ile 53 arasında olmalıdır."

        }), 400


    if amount <= 0:

        return jsonify({

            "success": False,

            "message":
                "Satış tutarı 0'dan büyük olmalıdır."

        }), 400


    try:

        record_id =
            create_instore_sale(

                store_id=store_id,

                personnel_id=personnel_id,

                year=year,

                week=week,

                amount=amount,

                description=description

            )


        return jsonify({

            "success": True,

            "message":
                "InStore satış başarıyla kaydedildi.",

            "id":
                record_id

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                f"InStore satış kaydedilemedi: {error}"

        }), 500


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

        "message":
            "Prim hesaplama sistemi çalışıyor."

    })


# ============================================================
# UYGULAMAYI ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )