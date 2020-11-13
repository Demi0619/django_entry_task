from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse


def logout_view(request):

    """log the user out."""

    logout(request)
    return HttpResponseRedirect(reverse('pay_app:index'))