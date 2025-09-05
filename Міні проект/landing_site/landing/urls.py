from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/order/', views.create_order, name='create_order'),
]
