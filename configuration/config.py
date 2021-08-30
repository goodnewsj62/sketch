import secrets
import os
from ast import literal_eval
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

class Setup:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://suser:suser@localhost:5432/sketch'
    OAUTH_CREDENTIALS = {
        "facebook":{
                        'id': os.getenv('FB_ID'),
                        'secret': os.getenv('FB_SECRET')
                    },
        'twitter':{
                        'id': os.getenv('TW_ID'),
                        'secret': os.getenv('TW_SECRET')
                    },
        'google':{
            'id': os.getenv('G_ID'),
            'secret': os.getenv('G_SECRET')
        }
    }
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TSL = False
    MAIL_USERNAME = "osonwajohn@gmail.com"
    MAIL_PASSWORD = os.getenv("EPASS")
    # MAIL_SUPPRESS_SEND = False

    

    SOCIAL_GOOGLE= {
    'consumer_key': os.getenv('customer_key'),
    'consumer_secret': os.getenv('customer_secret')}
    SECRET_KEY= secrets.token_hex(32)
    UPLOAD_FOLDER = r'/media/'
    ALLOWED_EXTENSIONS= {'jpg'}
    DEBUG= literal_eval(os.getenv('DEBUG'))
