import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-before-deploying')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'real_trader.db')
