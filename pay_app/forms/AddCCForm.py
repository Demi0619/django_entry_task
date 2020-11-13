from django import forms


class AddCCForm(forms.Form):
    card_number = forms.CharField(max_length=32, label='card_number')
    expire_date = forms.CharField(max_length=8, label='expire_date')
    payment_token = forms.CharField(max_length=128, label='payment_token')