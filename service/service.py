import requests


class BaseService:
    def __init__(self, clazz):
        self.clazz = clazz
        # self.conn = psycopg2.connect(
        #     host="localhost",
        #     user="postgres",
        #     password="root",
        #     database="orders"
        # )

    def get_all(self):
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM {self.clazz.__tablename__} ORDER BY id")
        # results = cursor.fetchall()
        # cursor.close()
        # return [self.clazz(*result) for result in results]
        results = []
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}").json()
        try:
            for i in s['data']:
                results.append(tuple(i.values()))
            return [self.clazz(*result) for result in results]
        except KeyError:
            return None

    def get_by_id(self, id: int):
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM {self.clazz.__tablename__} WHERE id = {id}")
        # result = cursor.fetchone()
        # cursor.close()
        # return self.clazz(*result) if result else None
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&id={id}").json()
        try:
            return self.clazz(*tuple(s['data'].values()))
        except KeyError:
            return None



