'''Defines URL patterns for pay_app.'''

from django.urls import path
from django.contrib.auth import views as auth_views
from pay_app import views

urlpatterns = [
    # index page
    path('', views.index, name='index'),
    # home page
    path('home/', views.homeview, name='home'),
    # Login page
    path('login/', auth_views.LoginView.as_view(template_name='login.html'),
    name='login'),
    # logout page
    path('logout/', views.logout_view, name='logout'),
    # signup page
    path('signup/', views.signup, name='signup'),
    # add credit card page
    path('add_cc/', views.add_cc, name='add_cc'),
    path('topup/<wallet_id>', views.topup, name='topup'),
    # pay page
    path('make_payment/<channel_id>', views.make_payment, name='make_payment'),
    path('history/', views.history, name='history'),
    path('void/<transaction_id>', views.void, name='void'),
    path('refund/<transaction_id>', views.refund, name= 'refund')
    # path('api/v1/user_info/', views.user_list, name='user_info'),

    ]
