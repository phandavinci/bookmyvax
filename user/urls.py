from django.urls import path
from . import views

urlpatterns = [
    path('userhome', views.userhome, name='userhome'),
    path('usersignin', views.usersignin, name='usersignin'),
    path('userlogout', views.userlogout, name='userlogout'),
    path('usersignup', views.usersignup, name='usersignup'),
    path('todaybookings', views.todaybookings, name='todaybookings'),
    path('allbookings', views.allbookings, name='allbookings'),
    path('futurebookings', views.futurebookings, name='futurebookings'),
    path('book/<str:id>', views.book, name='book'),
    path('', views.index, name='index')
]
