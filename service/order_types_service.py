from service.models import OrderType
from service.service import BaseService
import requests

class OrderTypeService(BaseService):
    def __init__(self):
        super().__init__(OrderType)

    # def save(self, order_type: OrderType) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"INSERT INTO order_types (name, price, deadline, subject_id) VALUES ('{order_type.name}', '{order_type.price}', '{order_type.deadline}', '{order_type.subject_id}')")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def update(self, order_type: OrderType) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""UPDATE order_types SET name = '{order_type.name}',
    #                                             price = '{order_type.price}',
    #                                             deadline = '{order_type.deadline}',
    #                                             subject_id = '{order_type.subject_id}' WHERE id = {order_type.id}""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def delete(self, order_type: OrderType) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM order_types WHERE id = {order_type.id}")
    #     self.conn.commit()
    #     cursor.close()

    def get_all_by_subject(self, subject_id: int):
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM order_types WHERE subject_id = {subject_id}")
        # results = cursor.fetchall()
        # cursor.close()
        # return [OrderType(*result) for result in results]
        results = []
        s = requests.get(
            f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[subject_id]={subject_id}").json()
        try:
            for i in s['data']:
                results.append(tuple(i.values()))
            return [OrderType(*result) for result in results]
        except KeyError:
            return None
