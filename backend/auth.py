from functools import wraps

from flask import (
    session,
    jsonify
)


# =========================================================
# KULLANICILAR
# =========================================================
#
# Şimdilik test amacıyla kullanıcı bilgisi burada tutuluyor.
#
# Kullanıcı:
# admin
#
# Şifre:
# admin123
#
# Daha sonraki aşamada kullanıcıları veritabanına
# taşıyacağız.
# =========================================================

USERS = {

    "admin": {

        "password": "admin123",

        "role": "reporting"

    }

}


# =========================================================
# KULLANICI DOĞRULAMA
# =========================================================

def authenticate_user(
    username,
    password
):

    user = USERS.get(
        username
    )

    if user is None:

        return None

    if user["password"] != password:

        return None

    return {

        "username": username,

        "role": user["role"]

    }


# =========================================================
# GİRİŞ YAP
# =========================================================

def login_user(
    username,
    password
):

    user = authenticate_user(
        username,
        password
    )

    if user is None:

        return False

    session.clear()

    session["logged_in"] = True

    session["username"] = (
        user["username"]
    )

    session["role"] = (
        user["role"]
    )

    return True


# =========================================================
# ÇIKIŞ YAP
# =========================================================

def logout_user():

    session.clear()


# =========================================================
# OTURUM KONTROLÜ
# =========================================================

def is_logged_in():

    return session.get(
        "logged_in",
        False
    ) is True


# =========================================================
# OTURUMDAKİ KULLANICI
# =========================================================

def get_current_user():

    if not is_logged_in():

        return None

    return {

        "username": session.get(
            "username"
        ),

        "role": session.get(
            "role"
        )

    }


# =========================================================
# ROL KONTROLÜ
# =========================================================

def has_role(role):

    if not is_logged_in():

        return False

    return (
        session.get("role") == role
    )


# =========================================================
# RAPORLAMA EKİBİ KONTROLÜ
# =========================================================

def reporting_required(function):

    @wraps(function)
    def wrapper(
        *args,
        **kwargs
    ):

        if not is_logged_in():

            return jsonify({

                "success": False,

                "message": (
                    "Oturum açmanız gerekiyor."
                )

            }), 401


        if not has_role(
            "reporting"
        ):

            return jsonify({

                "success": False,

                "message": (
                    "Bu işlem için "
                    "yetkiniz bulunmuyor."
                )

            }), 403


        return function(
            *args,
            **kwargs
        )


    return wrapper