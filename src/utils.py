from werkzeug.security import generate_password_hash, check_password_hash


def check_password_and_generate_hash(password1: str, password2: str) -> str or bool:
    if password1 == password2:
        return generate_password_hash(password1, 'sha256', 16)
    return False


def check_password(password1: str, password2: str) -> bool:
    return check_password_hash(password2, password1)
