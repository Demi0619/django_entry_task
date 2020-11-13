from pay_app.models import User, Channel, Wallet, CreditCard
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import render
from pay_app.commons.decorators import check_user_login
from pay_app.commons.get_available_channels import get_available_channels


@check_user_login
def homeview(request):
    """ the home page for logged in user to view available channel"""
    try:  # object not exist check
        current_user = User.objects.get(user_name=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'user not exist')
    else:
        context = {}
        wallets = get_available_channels(current_user.user_id, 'wallet')  # get available wallets
        if wallets:
            for wallet in wallets:
                wallet.balance /= 100
        context['wallets'] = wallets
        ccs = get_available_channels(current_user.user_id, 'credit_card')  # get available credit cards
        context['ccs'] = ccs
    return render(request, 'home.html', context)