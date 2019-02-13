from os import environ


class DatabaseConfig:
    def __init__(self):
        self.db_host = environ.get('DB_HOST', 'localhost')
        self.db_port = environ.get('DB_PORT', '5423')
        self.db_user = environ.get('DB_USER')
        self.db_password = environ.get('DB_PASSWORD')
        self.db_name = environ.get('DB_NAME', 'postgres')
