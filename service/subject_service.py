from service.models import Subject
from service.service import BaseService


class SubjectService(BaseService):
    def __init__(self):
        super().__init__(Subject)

    # def save(self, subject: Subject) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"INSERT INTO subjects (name) VALUES ('{subject.name}')")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def update(self, subject: Subject) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"""UPDATE subjects SET name = '{subject.name}' WHERE id = {subject.id}""")
    #     self.conn.commit()
    #     cursor.close()
    #
    # def delete(self, subject: Subject) -> None:
    #     cursor = self.conn.cursor()
    #     cursor.execute(f"DELETE FROM subjects WHERE id = {subject.id}")
    #     self.conn.commit()
    #     cursor.close()