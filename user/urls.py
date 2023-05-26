from django.urls import path
from . import views

urlpatterns = [
    path('userhome', views.userhome, name='userhome'),
    path('usersignin', views.usersignin, name='usersignin'),
    path('userlogout', views.userlogout, name='userlogout'),
    path('usersignup', views.usersignup, name='usersignup'),
    path('mybookings', views.mybookings, name='mybookings'),
    path('allbookings', views.allbookings, name='allbookings'),
    path('', views.index, name='index')
]
