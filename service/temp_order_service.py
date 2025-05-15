import sqlite3

from service.models import Order

class TempOrderService:
    def __init__(self):
        self.conn = sqlite3.connect("orders.db")

    def save(self, order: Order):
        cursor = self.conn.cursor()
        cursor.execute(f"""INSERT INTO orders (user_id, subject_id, order_type_id, order_text, is_urgent, status_id, freelancer_id) VALUES
                         (?, ?, ?, ?, ?, ?, ?)""",
                       (order.user_id, order.subject_id, order.order_type_id, order.order_text, order.is_urgent, order.status_id, order.freelancer_id))
        self.conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def get_all(self):
        cursor = self.conn.cursor()
        s = cursor.execute("""SELECT * FROM orders""").fetchall()
        self.conn.commit()
        cursor.close()
        return [Order(*result) for result in s]

    def get_by_id(self, order_id):
        cursor = self.conn.cursor()
        s = cursor.execute("""SELECT * FROM orders WHERE id = ?""", (order_id, )).fetchall()
        self.conn.commit()
        cursor.close()
        return Order(*s[0])
