from django import forms
from pay_app.models import User, Channel, Wallet, CreditCard
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models import Q
from pay_app.commons.get_available_channels import get_available_channels


receiver_choices = []
all_user = User.objects.all()
for user in all_user:
    receiver_choices.append(user.user_name)
# print(receiver_choice)


class PaymentForm(forms.Form):
    error_messages = {
        'no_enough_balance': _("you don't have enough balance for this channel to pay, please choose another channel!"),
        'invalid receiver': _("cannot find receiver,/"
                              " please check if correct name entered or invite your friend to payapp!"),
        'receiver no wallet': _("cannot pay to receiver, please ask him/her to set up wallet"),
        'payer wallet unavailable': _("your wallet is not available, please choose another one"),
        'payer credit card unavailable': _("your credit card is not available, please choose another one"),
    }
    payer_choices = []
    receiver_name = forms.CharField(max_length=50, label='receiver_user_name')
    payer_method = forms.ChoiceField(choices=payer_choices, label='pay with this method')
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, label='amount')

    def __init__(self, *args, **kwargs):
        self.payer_name = kwargs.pop('payer')  # payer_name
        self.payer_channel = kwargs.pop('payer_channel')
        self.payer_choices = []
        self.receiver_choices = receiver_choices
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.payer = User.objects.get(user_name=self.payer_name)
        if self.payer_name in self.receiver_choices:
            self.receiver_choices = receiver_choices.remove(str(self.payer_name))
        if int(self.payer_channel) == 1:  # get all available wallets
            wallets = get_available_channels(self.payer.user_id, 'wallet')
            if wallets:
                for wallet in wallets:
                    self.payer_choices.append((wallet.wallet_id, 'wallet:'+str(wallet.balance/100)))
            self.fields['payer_method'] = forms.ChoiceField(choices=self.payer_choices, label='pay with this channel')
        if int(self.payer_channel) == 2:   # get all available credit card
            cards = get_available_channels(self.payer.user_id, 'credit_card')
            if cards:
                for card in cards:
                    self.payer_choices.append((card.card_id, 'credit card:'+str(card.card_number)))
                self.fields['payer_method'] = forms.ChoiceField(choices=self.payer_choices, label='pay to this channel')

    def clean_receiver_name(self):
        """ check input receiver name in system and has available wallet"""
        if self.cleaned_data.get('receiver_name') in self.receiver_choices:  # receiver in system
            receiver = User.objects.get(user_name=self.cleaned_data.get('receiver_name'))
            wallets = get_available_channels(receiver.user_id, 'wallet')
            if not wallets:
                raise forms.ValidationError(
                    self.error_messages['receiver no wallet'],
                    code='receiver no wallet'
                )
            else:
                return self.cleaned_data['receiver_name']
        else:
            raise forms.ValidationError(
                self.error_messages['invalid receiver'],
                code='invalid receiver'
            )

    def clean_amount(self):
        """ check payer wallet balance, if input amount bigger than balance, return error"""
        if self.payer_channel == 2:  # ignore balance check if not using wallet
            return self.cleaned_data['amount']
        else:
            pay_amount = self.cleaned_data.get('amount')*100
            payer_wallet = Wallet.objects.filter(wallet_id=self.cleaned_data.get('payer_method')).first()
            if payer_wallet is None:
                raise forms.ValidationError(
                    self.error_messages['payer wallet unavailable'],
                    code='payer wallet unavailable'
                )
            else:
                payer_balance = payer_wallet.balance
                if pay_amount > payer_balance:
                    raise forms.ValidationError(
                         self.error_messages['no_enough_balance'],
                         code='no_enough_balance'
                )
                else:
                    return self.cleaned_data['amount']


'''    def clean_payer_method(self):
        """ check if payment channel still available"""
        if self.payer_channel == 1:  # check wallet status
            wallet_channel = Channel.objects.get(channel_id=1)
            wallet = Wallet.objects.get(user_id = self.payer.user_id)
            if wallet_channel.channel_status == 1:
                if wallet.status == 1 or wallet.status == 2:
                    return self.cleaned_data['payer_method']
                else:
                    raise forms.ValidationError(
                        self.error_messages['payer wallet unavailable'],
                        code='payer wallet unavailable'
                    )
        if self.payer_channel == 2:  # check wallet status
            cc_channel = Channel.objects.get(channel_id=2)
            cc = CreditCard.objects.get(user_id=self.payer.user_id)
            if cc_channel.channel_status == 1:
                if cc.status == 1 or cc.status == 2:
                    return self.cleaned_data['payer_method']
                else:
                    raise forms.ValidationError(
                        self.error_messages['payer credit card unavailable'],
                        code='payer credit card unavailable'
                    )'''