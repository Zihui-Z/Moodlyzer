import os

class Config:
    SECRET_KEY = 'moodlyzer-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False