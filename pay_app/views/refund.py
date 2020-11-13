from pay_app.models import Transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, render
from pay_app.commons.decorators import check_user_login


@check_user_login
def refund(request, transaction_id):
    """refund a transaction"""
    if request.method == 'POST':
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        # add check for transaction payer_id == request.user
        if transaction.status == 3:  # check if still refundable
            Transaction.objects.filter(transaction_id=transaction_id).update(status=4)
        else:
            messages.error(request, 'Failed, transaction is not refundable now.')
            # refund_requested, decrease/increase money in admin
    context = {'transaction': transaction}
    return render(request, 'refund.html', context)