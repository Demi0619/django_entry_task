import functools

from django.http import HttpResponseRedirect
from django.shortcuts import reverse


def check_user_login(func):
    """ check if user authenticate when every request received"""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('pay_app:index'))
    return wrapper


