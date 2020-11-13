from django.contrib import admin
from django.template.context_processors import csrf
from django.urls import path,reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from .forms import TransactionActionForm

# Register your models here.

from pay_app.models import Channel, User, Transaction, UserChannel, Wallet, CreditCard

# Register modeladmin


class UserModelAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'show_available_channel')
    search_fields = ('user_id',)
    ordering = ('user_id',)
    readonly_fields = ('user_id',)

    def show_available_channel(self, obj):
        results = Channel.objects.filter(channel_status=1)
        channels = []
        for result in results:
            channels.append(result.channel_name)
        return channels


class ChannelModelAdmin(admin.ModelAdmin):
    list_display = ('channel_id', 'channel_name', 'channel_status',)
    search_fields = ('channel_id',)
    ordering = ('channel_id',)
    readonly_fields = ('channel_id',)


class WalletModelAdmin(admin.ModelAdmin):
    list_display = ('wallet_id', 'user_name', 'status', 'get_balance')
    search_fields = ('wallet_id', 'user_name',)
    ordering = ('wallet_id', )
    # readonly_fields = ('wallet_id', 'userid', )

    def user_name(self,obj):
        user = User.objects.get(user_id=obj.user_id)
        return user.user_name

    def get_balance(self, obj):
        result = obj.balance / 100
        return result
    get_balance.short_description = 'show balance'

    # def has_add_permission(self, request):
        # """ disable add user info in admin"""
        # return False

    def has_delete_permission(self, request, obj=None):
        """ disable add user info in admin"""
        return False


class CreditCardModelAdmin(admin.ModelAdmin):
    list_display = ('card_id', 'user_name', 'card_number', 'expire_date', 'status')
    search_fields = ('card_id', 'user_name',)
    ordering = ('card_id', )
    # readonly_fields = ('card_id', 'user_id', )

    def user_name(self,obj):
        user = User.objects.get(user_id=obj.user_id)
        return user.user_name
    # def has_add_permission(self, request):
        # """ disable add user info in admin"""
        # return False


class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payer_name', 'payer_channel_name', 'receiver_name', 'receiver_channel_name',\
                    'payer_wallet_id','payer_cc_id','receiver_wallet_id', 'status', 'show_amount', 'transaction_actions')
    search_fields = ('transaction_id', 'payer_name', 'receiver_name',)
    ordering = ('-transaction_id',)

    def payer_name(self, obj):
        user = User.objects.get(user_id=obj.payer_id)
        return user.user_name

    def receiver_name(self, obj):
        user = User.objects.get(user_id=obj.receiver_id)
        return user.user_name

    def payer_channel_name(self, obj):
        channel = Channel.objects.get(channel_id=obj.payer_channel_id)
        return channel.channel_name

    def receiver_channel_name(self,obj):
        channel = Channel.objects.get(channel_id=obj.receiver_channel_id)
        return channel.channel_name

    def show_amount(self, obj):
        result = obj.amount / 100
        return result

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # approve refund
            path('approve_refund/<transaction_id>', self.admin_site.admin_view(self.refund_approve),
                 name='refund_approve'),
            path('reject_refund/<transaction_id>', self.admin_site.admin_view(self.refund_rejected),
                 name='refund_rejected'),
        ]
        return custom_urls + urls

    def refund_approve(self, request, transaction_id):
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction_info = {'transaction_id': transaction_id, 'payer_id': transaction.payer_id,
                            'receiver': transaction.receiver.user_name, 'amount': transaction.amount}
        if request.method != 'POST':
            form = TransactionActionForm(transaction_info)
        else:
            form = TransactionActionForm(request.POST, transaction_info)
            # check whether it's valid:
            if form.is_valid():
                if transaction.status == 4:  # check if txn status is refund requested
                    Transaction.objects.filter(transaction_id=transaction_id).update(status=5)
                    # deduct money from receiver, refund money to payer
                    receiver_wallet = Wallet.objects.get(wallet_id=transaction.receiver_wallet_id)
                    if receiver_wallet.balance >= transaction.amount:  # add check for balance not enough
                        receiver_wallet.balance -= transaction.amount
                        receiver_wallet.save()
                        if transaction.payer_channel_id == 1:  # return money to payer's wallet
                            payer_wallet = Wallet.objects.get(wallet_id=transaction.payer_wallet_id)
                            payer_wallet.balance += transaction.amount
                            payer_wallet.save()
                        if transaction.payer_channel_id == 2:  # provide card_info, increase/decrease money done in 3-rd party
                            payer_card = CreditCard.objects.get(card_id=transaction.payer_cc_id)
                        self.message_user(request, 'success! please check in transaction page')
                    else:
                        self.message_user(request, 'failed, no enough money for receiver to refund')
                        Transaction.objects.filter(transaction_id=transaction_id).update(status=4)
                else:
                    self.message_user(request, 'failed, transaction is not refund-requested now.')
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['action'] = 'approve'
        return TemplateResponse(request, 'admin/transaction_action.html', context)

    def refund_rejected(self, request, transaction_id):
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction_info = {'transaction_id': transaction_id, 'payer_id': transaction.payer_id,
                            'receiver': transaction.receiver.user_name, 'amount': transaction.amount}
        if request.method != 'POST':
            form = TransactionActionForm(transaction_info)
        else:
            form = TransactionActionForm(request.POST, transaction_info)
            # check whether it's valid:
            if form.is_valid():
                if transaction.status == 4:
                    Transaction.objects.filter(transaction_id=transaction_id).update(status=6)
                    self.message_user(request, 'success! please check in transaction page')
                else:
                    self.message_user(request, 'failed! transaction is not refund_requested.')
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['action'] = 'approve'
        return TemplateResponse(request, 'admin/transaction_action.html', context)

    def transaction_actions(self, obj):
        if obj.status == 4:
            return format_html(
                '<a class="button" href="{}">approve</a>&nbsp;'
                '<a class="button" href="{}">reject</a>',
                reverse('admin:refund_approve', args=[obj.pk]),
                reverse('admin:refund_rejected', args=[obj.pk]),
            )

    transaction_actions.short_description = 'transaction Actions'
    transaction_actions.allow_tags = True

    def has_add_permission(self, request):
        """ disable add transaction info in admin"""
        return False


admin.site.register(User, UserModelAdmin)
admin.site.register(Wallet, WalletModelAdmin)
admin.site.register(CreditCard, CreditCardModelAdmin)
admin.site.register(Transaction, TransactionModelAdmin)
admin.site.register(Channel, ChannelModelAdmin)

