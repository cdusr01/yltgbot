import requests

from service.models import Freelancer
from service.service import BaseService


class FreelancerService(BaseService):
    def __init__(self):
        super().__init__(Freelancer)

    def get_by_user_id(self, user_id: int):
        s = requests.get(
            f"http://f1091403.xsph.ru/index.php?action=get&table=freelancers&&filters[user_id]={user_id}").json()
        try:
            return Freelancer(*tuple(s['data'][-1].values()))
        except KeyError:
            return None

    def update(self, freelancer: Freelancer) -> None:
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
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=update_freelancer&user_id={freelancer.id}&amount={freelancer.amount}&salary={freelancer.salary}")

    # def save(self, freelancer: Freelancer) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""INSERT INTO freelancers (user_id, login, passwd, amount, salary) VALUES
    #                     ('{freelancer.user_id}', '{freelancer.login}', '{freelancer.passwd}', '{freelancer.amount}', {freelancer.salary})""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def update(self, freelancer: Freelancer) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""UPDATE freelancers SET user_id = '{freelancer.user_id}',
    #                                         login = '{freelancer.login}',
    #                                         passwd = '{freelancer.passwd}',
    #                                         amount = '{freelancer.amount}',
    #                                         salary = '{freelancer.salary}' WHERE id = {freelancer.id}""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def delete(self, freelancer: Freelancer) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM freelancers WHERE id = {freelancer.id}")
    #     self.conn.commit()
    #     cursor.close()
