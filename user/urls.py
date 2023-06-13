from django.urls import path
from . import views

urlpatterns = [
    path('userhome', views.userhome, name='userhome'),
    path('usersignin', views.usersignin, name='usersignin'),
    path('userlogout', views.userlogout, name='userlogout'),
    path('usersignup', views.usersignup, name='usersignup'),
    path('bookings', views.bookings, name='bookings'),
    path('book/<str:id>', views.book, name='book'),
    path('msg', views.msg, name='msg'),
    path('certificatespage', views.certificatespage, name='certificatespage'),
    path('', views.index, name='index')
]
