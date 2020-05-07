import os
import psycopg2

class PostgresDriver:

    def __init__(self):

        self.dbname = 'postgres' # self.get_env_value('DATABASE_NAME')
        self.user = 'postgres' # self.get_env_value('DATABASE_USER')
        self.password = 'postgres' # self.get_env_value('DATABASE_PASSWORD')
        self.host = 'postgres' # self.get_env_value('DATABASE_HOST')
        self.port = 5432 # int(self.get_env_value('DATABASE_PORT'))

        try:
            self.connection = psycopg2.connect(f"dbname={self.dbname} user={self.user} password={self.password} host={self.host} port={self.port}")
            self.cursor = self.connection.cursor() 
        except Exception as e:
            print(f"[!] {e}")

    def get_env_value(self, env_variable):
        try:
            return os.environ[env_variable]
        except KeyError:
            error_msg = 'Set the {} environment variable'.format(env_variable)
            raise ImproperlyConfigured(error_msg)
    
    def select_all(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
