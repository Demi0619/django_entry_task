from pay_app.models import User, Transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from pay_app.commons.decorators import check_user_login


@check_user_login
def history(request):
    """show transaction history of this user"""
    if request.user.is_authenticated:
        current_user = User.objects.get(user_name=request.user)
        transactions = Transaction.objects.filter(Q(payer_id=current_user.user_id) | Q(receiver_id=current_user.user_id)).\
            order_by('-transaction_id')
        for transaction in transactions:
            transaction.amount /= 100
        context = {'transactions': transactions, 'current_user': current_user}
        return render(request, 'history.html', context)
    else:
        return HttpResponseRedirect(reverse('pay_app:index'))