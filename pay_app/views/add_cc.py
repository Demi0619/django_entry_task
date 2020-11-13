from pay_app.models import User, CreditCard, Channel
from pay_app.forms import AddCCForm
from django.http import HttpResponseRedirect
from django.shortcuts import reverse, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from pay_app.commons.decorators import check_user_login


@check_user_login
def add_cc(request):
    """ page to add credit card """
    if request.method != 'POST':
        form = AddCCForm()
    else:
        form = AddCCForm(request.POST)
        if form.is_valid():
            new_cc = CreditCard()
            try:
                current_user = User.objects.get(user_name=request.user)
            except ObjectDoesNotExist:
                messages.error(request, 'DB error, user cannot found')
            else:
                cc_channel = Channel.objects.get(channel_id=2)
                if cc_channel.channel_status == 1:
                    new_cc.user_id = current_user.user_id
                   # add check for empty/non-char/huge size data received
                    new_cc.card_number = form.cleaned_data['card_number']
                    new_cc.expire_date = form.cleaned_data['expire_date']
                    new_cc.payment_token = form.cleaned_data['payment_token']
                    new_cc.channel_category = 2
                    new_cc.status = 2  # default in whitelist
                # add check for DB
                    new_cc.save()
                    return HttpResponseRedirect(reverse('pay_app:home'))
                else:
                    messages.error(request, 'failed, credit card channel is not available')
    context = {'form': form}
    return render(request, 'add_cc.html', context)