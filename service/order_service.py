from service.models import Order
from service.service import BaseService
import requests
from urllib.parse import quote


class OrderService(BaseService):
    def __init__(self):
        super().__init__(Order)

    def save(self, order: Order) -> None:
        # cursor = self.conn.cursor()
        # cursor.execute(f"""INSERT INTO orders (user_id, subject_id, order_type_id, order_text, is_urgent, status_id, freelancer_id) VALUES
        #                 ('{order.user_id}', '{order.subject_id}', '{order.order_type_id}', '{order.order_text}', '{order.is_urgent}', '{order.status_id}', """ + (f"'{order.freelancer_id}'" if order.freelancer_id else "NULL)"))
        # self.conn.commit()
        # cursor.close()
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=create_order&user_id={order.user_id}&subject_id={order.subject_id}&order_type_id={order.order_type_id}&order_type_id={order.order_type_id}&order_text={quote(order.order_text)}&is_urgent={int(order.is_urgent)}")
        try:
            return s.json()['data']['id']
        except KeyError:
            return None

    def update(self, order: Order) -> None:
        # cursor = self.conn.cursor()
        # cursor.execute(f"""UPDATE orders SET user_id = '{order.user_id}',
        #                                     subject_id = '{order.subject_id}',
        #                                     order_type_id = '{order.order_type_id}',
        #                                     order_text = '{order.order_text}',
        #                                     is_urgent = '{order.is_urgent}',
        #                                     status_id = '{order.status_id}',
        #                                     freelancer_id = """ + (f"'{order.freelancer_id}'" if order.freelancer_id else "NULL") + f""" WHERE id = {order.id}""")
        # self.conn.commit()
        # cursor.close()
        if order.freelancer_id != None:
            s = requests.get(f"http://f1091403.xsph.ru/?action=update_order_status&order_id={order.id}&status_id={order.status_id}&freelancer_id={order.freelancer_id}")
        else:
            s = requests.get(f"http://f1091403.xsph.ru/?action=update_order_status&order_id={order.id}&status_id={order.status_id}&freelancer_id=null")

    # def delete(self, order: Order) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM orders WHERE id = {order.id}")
    #     self.conn.commit()
    #     cursor.close()

    def get_orders_by_status_id(self, status_id: int):
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM {self.clazz.__tablename__} WHERE status_id = {status_id} ORDER BY id")
        # results = cursor.fetchall()
        # cursor.close()
        # return [Order(*result) for result in results]
        results = []
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[status_id]={status_id}").json()
        try:
            for i in s['data']:
                results.append(tuple(i.values()))
            return [Order(*result) for result in results]
        except KeyError:
            return None

    def get_all_user_orders(self, user_id):
        results = []
        s = requests.get(
            f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[user_id]={user_id}").json()
        try:
            for i in s['data']:
                results.append(tuple(i.values()))
            return [Order(*result) for result in results]
        except KeyError:
            return None