from pay_app.models import Transaction, User, Wallet, CreditCard
from pay_app.forms import PaymentForm
from django.contrib import messages
from pay_app.task import process2, process1
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, render
from pay_app.commons.decorators import check_user_login


@check_user_login
def make_payment(request, **kwargs):
    """make payment page"""
    payer_channel_id = int(kwargs.pop('channel_id'))
    if request.method != 'POST':
        form = PaymentForm(payer=request.user, payer_channel=payer_channel_id)
    else:
        form = PaymentForm(request.POST, payer=request.user, payer_channel=payer_channel_id)
        # check whether it's valid:
        if form.is_valid():
            # save the data to transaction db
            new_transaction = Transaction()
            payer = User.objects.get(user_name=request.user)
            new_transaction.payer_id = payer.user_id
            new_transaction.receiver = User.objects.get(user_name=form.cleaned_data['receiver_name'])
            new_transaction.payer_channel_id = payer_channel_id
            new_transaction.receiver_channel_id = 1
            new_transaction.amount = form.cleaned_data['amount']*100
            if payer_channel_id == 1:
                new_transaction.payer_wallet_id = form.cleaned_data['payer_method']
            if payer_channel_id == 2:
                new_transaction.payer_cc_id = form.cleaned_data['payer_method']
            receiver_wallet = Wallet.objects.filter(user_id=new_transaction.receiver.user_id).first()
            new_transaction.receiver_wallet_id = receiver_wallet.wallet_id
            # add more checks here
            new_transaction.status = 1
            new_transaction.save()
            if payer_channel_id == 1:  # deduct money from payer's wallet
                payer_wallet = Wallet.objects.get(wallet_id=form.cleaned_data['payer_method'])
                if payer_wallet.balance >= new_transaction.amount:  # check if have enough balance
                    payer_wallet.balance -= new_transaction.amount
                    payer_wallet.save()
                    process1.apply_async(args=[new_transaction.transaction_id, receiver_wallet.wallet_id], countdown=10)
                    process2.apply_async(args=[new_transaction.transaction_id], countdown=20)
                    return HttpResponseRedirect(reverse('pay_app:history'))
                else:
                    new_transaction.status = 0  #
                    messages.error(request, "error, no enough balance ")
            if payer_channel_id == 2:  # provide card_info, money deduct done in 3-rd party
                payer_cc = CreditCard.objects.get(card_id=form.cleaned_data['payer_method'])
                process1.apply_async(args=[new_transaction.transaction_id, receiver_wallet.wallet_id], countdown=10)
                process2.apply_async(args=[new_transaction.transaction_id], countdown=25)
                return HttpResponseRedirect(reverse('pay_app:history'))
    context = {'form': form, 'channel_id': payer_channel_id}
    return render(request, 'payment.html', context)