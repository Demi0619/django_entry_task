from django.contrib.auth.forms import UserCreationForm
from pay_app.models import User, Wallet
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse


def signup(request):
    """new user signup"""
    if request.method != 'POST':
        # Display blank registration form.
        form = UserCreationForm()
    else:
        # Process completed form.
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            # save new user to User table
            # exception checks
            user = User(user_name=new_user.username)
            # save new user to UserChannel table

            user.save()
            # open wallet for new created user
            wallet = Wallet(user_id=user.user_id, status=1, channel_category=1)
            wallet.save()
            # Log the user in and then redirect to home page.
            authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('pay_app:home'))

        # save newly registered userinfo to db

    context = {'form': form}
    return render(request, 'signup.html', context)