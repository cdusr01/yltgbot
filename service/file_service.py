import requests
from urllib.parse import quote

class FileService:
    def get_file(self, order_id):
        s = requests.get(f"http://f1091403.xsph.ru/?action=get_order&id={order_id}").json()
        try:
            return f"http://f1091403.xsph.ru/Orders/{s['data']['user_id']}/{order_id}/customer/{quote(s['data']['files']['customer'][0])}"
        except Exception as e:
            return None


    def post_order_file(self, user_id, order_id, file):
        try:
            with open(file, "rb") as f:
                files = {"file": (file, f)}
                s = requests.post(
                    f"http://f1091403.xsph.ru/?action=upload_file&client_id={user_id}&order_id={order_id}&type=customer",
                    files=files)
                print(s.json())
        except Exception as e:
            print(f"Error: {e}")

    def post_answer_file(self, user_id, order_id, file):
        try:
            with open(file, "rb") as f:
                files = {"file": (file, f)}
                s = requests.post(
                    f"http://f1091403.xsph.ru/?action=upload_file&client_id={user_id}&order_id={order_id}&type=delivery",
                    files=files)
                print(s.json())
        except Exception as e:
            print(f"Error: {e}")

