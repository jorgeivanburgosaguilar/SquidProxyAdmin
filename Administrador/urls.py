'''
URLs
'''
from django.urls import path
from Administrador import views

urlpatterns = [
    path('^$', views.index, name='index'),
]
