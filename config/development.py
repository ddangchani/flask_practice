from config.default import *

db = {
    'user': 'root',
    'password': 'dangchan',
    'host' : 'localhost',
    'port' : '3306',
    'database' : 'pybo'
}

SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "dev"