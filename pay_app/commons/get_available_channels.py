from pay_app.models import Channel, Wallet, CreditCard
from django.db.models import Q


def get_available_channels(user_id, channel_type):
    if channel_type == 'wallet':
        wallet_channel = Channel.objects.get(channel_id=1)
        wallets = None
        if wallet_channel.channel_status == 1:  # check wallet channel status
            query = Q(status=1)  # check user_channel status (b/w)
            query.add(Q(status=2), Q.OR)
            query.add(Q(user_id=user_id), Q.AND)
            wallets = Wallet.objects.filter(query)
        return wallets
    if channel_type == 'credit_card':
        ccs = None
        cc_channel = Channel.objects.get(channel_id=2)
        if cc_channel.channel_status == 1:  # check cc channel status
            query = Q(status=1)  # check user_channel status (b/w)
            query.add(Q(status=2), Q.OR)
            query.add(Q(user_id=user_id), Q.AND)
            ccs = CreditCard.objects.filter(query)
        return ccs


