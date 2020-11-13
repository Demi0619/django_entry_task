from pay_server.celery_settings import app
from pay_app.models import Transaction, Wallet
from celery.utils.log import get_task_logger
from django.core.exceptions import EmptyResultSet, ObjectDoesNotExist


logger = get_task_logger(__name__)


@app.task(bind=True, default_retry_delay=5, max_retries=3)
def process1(self, transaction_id, wallet_id):
    transaction = Transaction.objects.get(pk=transaction_id)
    receiver_wallet = Wallet.objects.get(pk=wallet_id)
    print(receiver_wallet)
    if transaction.status == 1:
        logger.info('Update transaction status to settled after 1 minutes')
        try:
            Transaction.objects.filter(pk=transaction_id).update(status=3)
        except EmptyResultSet as exc1:
            raise self.retry(exc=exc1)
        try:
            receiver_wallet.balance += transaction.amount
            receiver_wallet.save()
        except ObjectDoesNotExist as exc2:
            raise self.retry(exc=exc2)    # add rollback logic


@app.task(bind=True, default_retry_delay=5, max_retries=3)
def process2(self, transaction_id):
    transaction = Transaction.objects.get(pk=transaction_id)
    if transaction.status == 3:
        logger.info('Update transaction status to succeed after 10 minutes')
        try:
            Transaction.objects.filter(pk=transaction_id).update(status=7)
        except EmptyResultSet as exc3:
            raise self.retry(exc=exc3)