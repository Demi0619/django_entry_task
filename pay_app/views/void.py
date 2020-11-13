from pay_app.models import Transaction, Wallet, CreditCard
from django.contrib import messages
from django.shortcuts import render
from pay_app.commons.decorators import check_user_login


@check_user_login
def void(request, transaction_id):
    """void a transaction"""
    if request.method == 'POST':
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        if transaction.status == 1:  # check if txn voidable
            Transaction.objects.filter(transaction_id=transaction_id).update(status=2)
            # add rollback logic if money operation fails (payer_channel not available)
            if transaction.payer_channel_id == 1:  # refund money to payer's wallet
                payer_wallet = Wallet.objects.get(wallet_id=transaction.payer_wallet_id)
                payer_wallet.balance += transaction.amount
                payer_wallet.save()
            if transaction.payer_channel_id == 2:  # provide card_info, increase/decrease money done in 3-rd party
                payer_card = CreditCard.objects.get(card_id=transaction.payer_cc_id)
        else:
            messages.error(request, 'Failed, transaction is not voidable now.')
    context = {'transaction': transaction}
    return render(request, 'void.html', context)