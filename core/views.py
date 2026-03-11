from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _

from .models import Machine, RepairRequest, MaintenanceHistory, Profile
from .forms import RepairRequestForm, MachineForm, MachineStatusForm, UserRegistrationForm, ConfirmRepairForm

@login_required
def dashboard(request):
    """Hiển thị dashboard với máy lọc theo level."""
    user_level = request.user.profile.level
    machines = Machine.objects.filter(classification_level__lte=user_level)
    pending_count = User.objects.filter(is_active=False).count() if user_level == 3 else 0
    return render(request, 'dashboard.html', {'machines': machines, 'pending_count': pending_count})

@login_required
def machine_detail(request, pk):
    """Chi tiết máy, lọc quyền."""
    user_level = request.user.profile.level
    machine = get_object_or_404(Machine, pk=pk, classification_level__lte=user_level)
    repairs = RepairRequest.objects.filter(machine=machine)
    return render(request, 'machine_detail.html', {'machine': machine, 'repairs': repairs})

@login_required
@login_required
def create_repair(request):
    if request.user.profile.level < 1:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = RepairRequestForm(request.POST)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.requested_by = request.user
            repair.save()
            # Tạo history ban đầu khi yêu cầu sửa
            MaintenanceHistory.objects.create(
                machine=repair.machine,
                technician=request.user,
                action_taken=repair.description,
                cost=0,
                start_repair_date=timezone.now(),
                end_repair_date=None  # Chờ xác nhận
            )
            messages.success(request, _("Yêu cầu sửa chữa đã được tạo!"))
            return redirect('dashboard')
    else:
        form = RepairRequestForm()
    return render(request, 'repair_create.html', {'form': form})

@login_required
def create_machine(request):
    """Thêm máy mới, level >=1."""
    if request.user.profile.level < 1:
        return HttpResponseForbidden()
    if request.method == "POST":
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.created_by = request.user
            machine.save()
            return redirect("dashboard")
    else:
        form = MachineForm()
    return render(request, "create_machine.html", {"form": form})

@login_required
def update_machine(request, pk):
    """Sửa thông tin máy, level >=2."""
    if request.user.profile.level < 2:
        return HttpResponseForbidden()
    machine = get_object_or_404(Machine, pk=pk, classification_level__lte=request.user.profile.level)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            return redirect('machine_detail', pk=pk)
    else:
        form = MachineForm(instance=machine)
    return render(request, 'update_machine.html', {'form': form, 'machine': machine})

@login_required
def update_machine_status(request, pk):
    """Cập nhật status máy, level >=1."""
    if request.user.profile.level < 1:
        return HttpResponseForbidden()
    machine = get_object_or_404(Machine, pk=pk, classification_level__lte=request.user.profile.level)
    if request.method == 'POST':
        form = MachineStatusForm(request.POST)
        if form.is_valid():
            machine.status = form.cleaned_data['status']
            machine.save()
            return redirect('machine_detail', pk=pk)
    else:
        form = MachineStatusForm(initial={'status': machine.status})
    return render(request, 'update_status.html', {'form': form, 'machine': machine})

@login_required
def confirm_repair(request, repair_pk):
    if request.user.profile.level < 1:
        return HttpResponseForbidden()
    repair = get_object_or_404(RepairRequest, pk=repair_pk)
    if repair.machine.classification_level > request.user.profile.level:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ConfirmRepairForm(request.POST)
        if form.is_valid():
            repair.status = 'done'
            repair.save()
            # Update history
            history = MaintenanceHistory.objects.filter(machine=repair.machine, end_repair_date=None).last()
            if history:
                history.action_taken = form.cleaned_data['action_taken']
                history.cost = form.cleaned_data['cost']
                history.end_repair_date = timezone.now()
                history.save()
            repair.machine.status = 'working'
            repair.machine.save()
            messages.success(request, _("Đã xác nhận sửa chữa hoàn thành!"))
            return redirect('machine_detail', pk=repair.machine.pk)
    else:
        form = ConfirmRepairForm(initial={'action_taken': repair.description})
    return render(request, 'confirm_repair.html', {'form': form, 'repair': repair})

def register(request):
    """Đăng ký tài khoản, chờ duyệt."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Profile.objects.create(user=user, level=0)
            return redirect('login')  # Hoặc trang thông báo chờ duyệt
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def pending_requests(request):
    """Danh sách yêu cầu duyệt, chỉ level 3."""
    if request.user.profile.level != 3:
        return HttpResponseForbidden()
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'pending_requests.html', {'pending_users': pending_users})

@login_required
def approve_user(request, pk):
    """Duyệt user, gán level, chỉ level 3."""
    if request.user.profile.level != 3:
        return HttpResponseForbidden()
    user = get_object_or_404(User, pk=pk, is_active=False)
    if request.method == 'POST':
        level = request.POST.get('level')
        if level in ['1', '2', '3']:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.level = int(level)
            profile.save()
            user.is_active = True
            user.save()
            return redirect('pending_requests')
    return render(request, 'approve_user.html', {'user_to_approve': user})