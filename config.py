import os

class Config:
    SECRET_KEY = 'dinesync-secret-key-change-in-production'

    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:niha0401@localhost:54321/restaurant_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    