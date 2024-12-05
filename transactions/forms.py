from django import forms
from .models import Transaction
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount

#For practice transfer
from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

class TransferForm(forms.Form):
    account_no = forms.CharField(max_length=20, required=True, label='Recipient Account No')
    amount = forms.DecimalField(max_digits=12, decimal_places=2, required=True, label='Amount')

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')  # Current logged-in user's account
        super().__init__(*args, **kwargs)

    def clean_account_no(self):
        account_no = self.cleaned_data.get('account_no')
        print(account_no)
        print(self.account)
        if str(self.account) == str(account_no):
            print("ye")
            raise forms.ValidationError("Same account transfer not possible")
        try:
            recipient_account = UserBankAccount.objects.get(account_no=account_no)
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError("The recipient account was not found.")
        return recipient_account

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        if amount > self.account.balance:
            raise forms.ValidationError("You do not have enough balance to transfer this amount.")
        return amount
