from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Machine(models.Model):
    machine_code = models.CharField(max_length=50, unique=True, verbose_name="Mã hiệu máy")
    machine_name = models.CharField(max_length=200, verbose_name="Tên máy")
    location = models.CharField(max_length=200, verbose_name="Phân xưởng")

    STATUS = [
        ("working", "Hoạt động"),
        ("broken", "Hỏng"),
        ("maintenance", "Đang sửa"),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default="working", verbose_name="Tình trạng máy")

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine_code} - {self.machine_name}"


class RepairRequest(models.Model):
    REPORTER_LEVEL = [
        ("assurer", "Người bảo đảm"),
        ("need_assurance", "Người cần bảo đảm"),
    ]
    ASSURANCE_STATUS = [
        ("pending", "Chờ bảo đảm"),
        ("assured", "Đã bảo đảm"),
        ("rejected", "Không bảo đảm"),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name="Máy")
    report_date = models.DateField(default=timezone.localdate, verbose_name="Ngày nhập")
    description = models.TextField(verbose_name="Tình trạng máy")
    repair_requirement = models.TextField(default="", verbose_name="Yêu cầu sửa chữa")
    assurance_status = models.CharField(
        max_length=20, choices=ASSURANCE_STATUS, default="pending", verbose_name="Tình trạng bảo đảm"
    )
    reporter_level = models.CharField(
        max_length=20, choices=REPORTER_LEVEL, default="need_assurance", verbose_name="Cấp nhập liệu"
    )

    STATUS = [
        ("pending", "Chờ xử lý"),
        ("processing", "Đang xử lý"),
        ("done", "Hoàn tất"),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.machine_code} - {self.report_date}"


class MaintenanceHistory(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_taken = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maintenance {self.machine.machine_code}"
