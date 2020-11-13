from django import forms


class TopupWallet(forms.Form):
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, label='amount')