from yoomoney import Quickpay, Client
import config


class Payment:
    client_id = config.CLIENT_ID
    receiver = config.RECEIVER
    token = config.YOOMONEY_TOKEN

    def __init__(self):
        self.client = Client(self.token)

    def create_bill(self, sum, label):
        quickpay = Quickpay(
            receiver=self.receiver,
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=sum,
            label=label
        )
        return quickpay.redirected_url

    def is_paid(self, label):
        # history = self.client.operation_history(label=label)
        # try:
        #     return history.operations[-1].status == "success"
        # except IndexError:
        #     return False
        return True

