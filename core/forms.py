from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Machine, RepairRequest, MaintenanceHistory  # <-- THÊM MaintenanceHistory vào đây

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Email"))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': _("Tên đăng nhập"),
            'password1': _("Mật khẩu"),
            'password2': _("Xác nhận mật khẩu"),
        }

class MachineForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label=_("Ngày bắt đầu nhận máy")
    )

    class Meta:
        model = Machine
        fields = ['machine_code', 'name', 'location', 'classification_level', 'status', 'start_date']
        labels = {
            'machine_code': _("Mã máy"),
            'name': _("Tên máy"),
            'location': _("Vị trí"),
            'classification_level': _("Phân cấp"),
            'status': _("Trạng thái"),
            'start_date': _("Ngày bắt đầu nhận máy"),
        }

class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['machine', 'description']
        labels = {
            'machine': _("Chọn máy"),
            'description': _("Mô tả sự cố"),
        }

class MachineStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Machine.STATUS, label=_("Trạng thái mới"))

class ConfirmRepairForm(forms.ModelForm):
    class Meta:
        model = MaintenanceHistory
        fields = ['action_taken', 'cost']
        labels = {
            'action_taken': _("Hành động đã thực hiện"),
            'cost': _("Chi phí"),
        }

class UpdateStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Machine.STATUS, label="Trạng thái mới")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Mô tả cập nhật", required=False)