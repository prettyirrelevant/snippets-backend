import secrets


def generate_uid():
    return secrets.token_hex(16)
