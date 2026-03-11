from django.urls import path
from . import views

urlpatterns = [
    #path('', views.machine_list, name='machine_list'),
    path('', views.dashboard, name='dashboard'),
    path('machine/<int:pk>/', views.machine_detail, name='machine_detail'),
    path('repair/create/', views.create_repair, name='create_repair'),
    path('machine/add/', views.create_machine, name='create_machine'),
    path('machine/<int:pk>/update/', views.update_machine, name='update_machine'),
    path('machine/<int:pk>/update-status/', views.update_machine_status, name='update_machine_status'),
    path('repair/<int:repair_pk>/confirm/', views.confirm_repair, name='confirm_repair'),
    path('register/', views.register, name='register'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('approve-user/<int:pk>/', views.approve_user, name='approve_user'),
    path('users/', views.users_list, name='users_list'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('export/excel/', views.export_machines_excel, name='export_excel'),
    path('export/pdf/', views.export_machines_pdf, name='export_pdf'),
]