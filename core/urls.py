from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('machine/<int:pk>/', views.machine_detail, name='machine_detail'),
    path('repair/create/', views.create_repair, name='create_repair'),
    path('machine/add/', views.create_machine, name='create_machine'),
]