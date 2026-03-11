from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('machine/<int:pk>/detail/', views.machine_detail, name='machine_detail'),
    path('repair/create/', views.create_repair, name='create_repair'),
    path('machine/add/', views.create_machine, name='create_machine'),
    path('machine/<int:pk>/update/', views.update_machine, name='update_machine'),
    path('machine/<int:pk>/update-status/', views.update_machine_status, name='update_machine_status'),
    path('repair/<int:repair_pk>/confirm/', views.confirm_repair, name='confirm_repair'),
    path('register/', views.register, name='register'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('approve-user/<int:pk>/', views.approve_user, name='approve_user'),
]