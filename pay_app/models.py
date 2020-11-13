from django.db import models


class Channel(models.Model):
    channel_id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=50)
    channel_status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'channel'


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    payer_id = models.IntegerField()
    receiver = models.ForeignKey('User', models.DO_NOTHING)
    status = models.IntegerField()
    amount = models.BigIntegerField()
    payer_channel_id = models.IntegerField()
    receiver_channel_id = models.IntegerField(default=1)
    payer_wallet_id = models.IntegerField(default=0)
    payer_cc_id = models.IntegerField(default=0)
    receiver_wallet_id = models.IntegerField(default=0)


    class Meta:
        managed = False
        db_table = 'transaction'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'user'


class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    status = models.IntegerField()
    balance = models.IntegerField(default=0)
    channel_category = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'wallet'


class CreditCard(models.Model):
    card_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    card_number = models.CharField(max_length=32)
    expire_date = models.CharField(max_length=8)
    payment_token = models.CharField(max_length=128, default='')
    status = models.IntegerField()
    channel_category = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'credit_card'


class UserChannel(models.Model):
    uc_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    channel = models.ForeignKey('Channel', models.DO_NOTHING)
    status = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'user_channel'

