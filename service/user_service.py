from service.models import User
from service.service import BaseService
import requests
from urllib.parse import quote


class UserService(BaseService):
    def __init__(self):
        super().__init__(User)

    def get_by_user_id(self, user_id: int) -> User:
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'")
        # result = cursor.fetchone()
        # cursor.close()
        # return User(*result) if result else None
        s = requests.get(
            f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[user_id]={user_id}").json()
        try:
            return User(*tuple(s['data'][0].values()))
        except KeyError:
            return None

    def get_by_username(self, user_tag: str) -> User:
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM users WHERE user_tag = '{user_tag}'")
        # result = cursor.fetchone()
        # cursor.close()
        # return User(*result) if result else None
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[user_tag]={quote(user_tag)}").json()
        # print(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&&filters[]={quote(user_tag)}")
        try:
            return User(*tuple(s['data'][0].values()))
        except KeyError:
            return None

    def get_all_admins(self) -> list[User]:
        # cursor = self.conn.cursor()
        # cursor.execute(f"SELECT * FROM users WHERE role_id = '1'")
        # results = cursor.fetchall()
        # cursor.close()
        # return [User(*result) for result in results]
        results = []
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=get&table={self.clazz.__tablename__}&filters[role_id]=1").json()
        try:
            for i in s['data']:
                results.append(tuple(i.values()))
            return [User(*result) for result in results]
        except KeyError:
            return None


    def save(self, user: User) -> None:
        # cursor = self.conn.cursor()
        # cursor.execute(f"INSERT INTO users (user_id, user_tag, role_id) VALUES ('{user.user_id}', '{user.user_tag}', '{user.role_id}')")
        # self.conn.commit()
        # cursor.close()
        s = requests.get(f"http://f1091403.xsph.ru/index.php?action=create_user&user_id={quote(str(user.user_id))}&user_tag={quote(user.user_tag)}&role_id={user.role_id}&balance={user.balance}")

    def update(self, user: User) -> None:
        # cursor = self.conn.cursor()
        # cursor.execute(f"""UPDATE users SET user_id = '{user.user_id}',
        #                                     user_tag = '{user.user_tag}',
        #                                     role_id = '{user.role_id}' WHERE id = {user.id}""")
        # self.conn.commit()
        # cursor.close()
        if user.user_tag != None:
            s = requests.get(f"http://f1091403.xsph.ru/?action=update_user&user_id={quote(str(user.id))}&new_tag={quote(user.user_tag)}&new_role_id={user.role_id}&balance={user.balance}")
        else:
            s = requests.get(f"http://f1091403.xsph.ru/?action=update_user&user_id={quote(str(user.id))}&new_tag={quote(str(user.id))}&new_role_id={user.role_id}&balance={user.balance}")
    #
    # def delete(self, user: User) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM users WHERE id = {user.id}")
    #     self.conn.commit()
    #     cursor.close()