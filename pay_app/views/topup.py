from pay_app.models import User, Wallet, Channel
from pay_app.forms import TopupWallet
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, render
from django.contrib import messages
from pay_app.commons.decorators import check_user_login


@check_user_login
def topup(request, wallet_id):
    """ page to topup wallet """
    if request.method != 'POST':
        form = TopupWallet()
    else:
        form = TopupWallet(request.POST)
        if form.is_valid():
            wallet = Wallet.objects.filter(wallet_id=wallet_id).first()
            wallet_channel = Channel.objects.get(channel_id=1)
            if wallet_channel.channel_status == 1:  # check wallet status
                if wallet.status ==1 or wallet.status == 2:
                    wallet.balance += form.cleaned_data['amount']*100
                    # add amount empty/wrong type/negative/too big check and handles
                    wallet.save()
                    return HttpResponseRedirect(reverse('pay_app:home'))
                else:
                    messages.error(request, 'failed, your wallet is not available')
            else:
                messages.error(request, 'failed, your wallet is not available')
    context = {'form': form, 'wallet_id': wallet_id}
    return render(request, 'topup.html', context)