from service.models import Status
from service.service import BaseService


class StatusService(BaseService):
    def __init__(self):
        super().__init__(Status)

    # def save(self, status: Status) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"INSERT INTO statuses (state) VALUES ('{status.state}')")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def update(self, status: Status) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""UPDATE statuses SET state = '{status.state}' WHERE id = {status.id}""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def delete(self, status: Status) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM statuses WHERE id = {status.id}")
    #     self.conn.commit()
    #     cursor.close()