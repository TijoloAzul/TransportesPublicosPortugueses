import psycopg2

class db_manager:

    def __init__(self, conf):
        self.db_host = conf['host']
        self.db_name = conf['database']
        self.db_user = conf['user']
        self.db_password = conf['password']

    def open(self):
        self.conn = psycopg2.connect(
            host = self.db_host, 
            dbname = self.db_name, 
            user = self.db_user, 
            password = self.db_password)

    def select(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def execute_1(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            self.conn.commit()

    def execute(self, sql, params = None):
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()