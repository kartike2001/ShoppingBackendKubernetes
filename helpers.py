import random
import string


def escape_sql(value):
    value = value.replace("'", "''")
    value = value.replace("\\", "\\\\")
    value = value.replace("\0", "")
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\b", "\\b")
    value = value.replace("\t", "\\t")
    value = value.replace("\x1a", "\\Z")
    return value


def escape_html(value):
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace("&", "&amp;")
    value = value.replace('"', "&quot;")
    value = value.replace("'", "&#x27;")
    value = value.replace("/", "&#x2F;")
    return value


def sanitize_input(value):
    if isinstance(value, str):
        return escape_html(escape_sql(value))
    elif isinstance(value, (int, float)):
        return value
    else:
        raise ValueError("Unsupported input type")


def generate_token():
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=200))
    return token