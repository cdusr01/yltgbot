from service.models import Role
from service.service import BaseService


class RoleService(BaseService):
    def __init__(self):
        super().__init__(Role)

    # def save(self, role: Role) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"INSERT INTO roles (type, rate) VALUES ('{role.type}', '{role.rate}')")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def update(self, role: Role) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""UPDATE roles SET type = '{role.type}',
    #                                            rate = '{role.rate}' WHERE id = {role.id}""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def delete(self, role: Role) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM roles WHERE id = {role.id}")
    #     self.conn.commit()
    #     cursor.close()