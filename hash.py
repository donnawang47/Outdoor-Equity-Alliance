import werkzeug.security

def main():
    h = werkzeug.security.generate_password_hash('')