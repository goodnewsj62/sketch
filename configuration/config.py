import secrets

class Setup:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://suser:suser@localhost:5432/sketch'
    SECRETE_KEY= secrets.token_hex(32)