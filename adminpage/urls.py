from django.urls import path
from . import views

urlpatterns = [
    path('adminhome', views.adminhome, name='adminhome'),
    path('adminsignin/', views.adminsignin, name='adminsignin'),
    path('adminlogout', views.adminlogout, name='adminlogout'),
    path('adminadd', views.adminadd, name='adminadd'),
    path('entriesof', views.entriesof, name='entiresof'),
    path('adminsignup', views.adminsignup, name='adminsignup')
]
