from django.urls import path
from . import views

urlpatterns = [
    path('adminhome', views.adminhome, name='adminhome'),
    path('adminsignin/', views.adminsignin, name='adminsignin'),
    path('adminlogout', views.adminlogout, name='adminlogout'),
    path('adminadd', views.adminadd, name='adminadd'),
    path('entriesof/<str:id>', views.entriesof, name='entiresof'),
    path('modify/<str:id>', views.modify, name="modify"),
    #path('confirmvaccination', views.confirmvaccination, name="confirmvaccination"),
    path('scanqr', views.scanqr, name='scanqr')
]
