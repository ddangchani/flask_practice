from config.default import *

db = {
    'user': 'pybo',
    'password': '121421',
    'host' : 'localhost',
    'port' : '0',
    'database' : 'pybo'
}

SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = b"\xd9\xc6F\x99\xb6\xb8:2\xe9\xd6\xc3#\x04\x15\x05\xbd"