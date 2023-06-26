'''
URLs
'''
from django.urls import path
from Administrador import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/update-ip-choices/',
         views.update_ip_choices, name='update_ip_choices'),
]
