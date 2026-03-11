from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Profile(models.Model):
    LEVEL_CHOICES = [
        (0, _('Chờ duyệt')),
        (1, _('Cấp 1')),
        (2, _('Cấp 2')),
        (3, _('Cấp 3 - Quản lý cao nhất')),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Tài khoản"))
    level = models.IntegerField(choices=LEVEL_CHOICES, default=0, verbose_name=_("Cấp quyền"))

    def __str__(self):
        return f"{self.user.username} - {self.get_level_display()}"

    class Meta:
        verbose_name = _("Hồ sơ người dùng")
        verbose_name_plural = _("Hồ sơ người dùng")

class Machine(models.Model):
    CLASSIFICATION_LEVEL = [
        (1, _('Cấp 1')),
        (2, _('Cấp 2')),
        (3, _('Cấp 3')),
    ]
    machine_code = models.CharField(max_length=50, unique=True, verbose_name=_("Mã máy"))
    name = models.CharField(max_length=200, verbose_name=_("Tên máy"),default='hiep')
    location = models.CharField(max_length=200, verbose_name=_("Vị trí"))
    classification_level = models.IntegerField(choices=CLASSIFICATION_LEVEL, default=1, verbose_name=_("Phân cấp"))
    
    STATUS = [
        ('working', _('Hoạt động')),
        ('broken', _('Hỏng')),
        ('maintenance', _('Đang bảo trì/sửa chữa')),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default='working', verbose_name=_("Trạng thái"))
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Người tạo"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Máy móc")
        verbose_name_plural = _("Máy móc")

class RepairRequest(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name=_("Máy móc"))
    description = models.TextField(verbose_name=_("Mô tả sự cố"))
    
    STATUS = [
        ('pending', _('Chờ xử lý')),
        ('processing', _('Đang sửa')),
        ('done', _('Đã hoàn thành')),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default='pending', verbose_name=_("Trạng thái yêu cầu"))
    
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Người yêu cầu"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))

    class Meta:
        verbose_name = _("Yêu cầu sửa chữa")
        verbose_name_plural = _("Yêu cầu sửa chữa")

class MaintenanceHistory(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name=_("Máy móc"))
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Kỹ thuật viên"))
    action_taken = models.TextField(verbose_name=_("Hành động đã thực hiện"))
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Chi phí"))
    start_repair_date = models.DateTimeField(default=timezone.now, verbose_name=_("Ngày bắt đầu sửa"))
    end_repair_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Ngày hoàn thành sửa/bảo hành"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo lịch sử"))

    def __str__(self):
        return f"Bảo trì {self.machine.machine_code}"

    class Meta:
        verbose_name = _("Lịch sử bảo trì")
        verbose_name_plural = _("Lịch sử bảo trì")