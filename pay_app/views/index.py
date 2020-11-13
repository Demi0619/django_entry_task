from django.shortcuts import render


def index(request):
    """The index page for pay server (not logged in)"""

    return render(request, 'index.html')