import os

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rules.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
