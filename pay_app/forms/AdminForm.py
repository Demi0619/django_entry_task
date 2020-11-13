from django import forms


class TransactionActionForm(forms.Form):
    transaction_id = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='transaction_id')
    payer_id = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='payer_id')
    receiver = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='receiver')
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='amount')
