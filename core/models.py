from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    machine_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    STATUS = [
        ('working', 'Hoạt động'),
        ('broken', 'Hỏng'),
        ('maintenance', 'Đang sửa'),
    ]

    status = models.CharField(max_length=20, choices=STATUS, default='working')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

class RepairRequest(models.Model):

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)

    description = models.TextField()

    STATUS = [
        ('pending', 'Chờ sửa'),
        ('processing', 'Đang sửa'),
        ('done', 'Đã sửa'),
    ]

    status = models.CharField(max_length=20, choices=STATUS, default='pending')

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
class MaintenanceHistory(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_taken = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maintenance {self.machine.machine_code}"