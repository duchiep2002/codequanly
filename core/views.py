from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Q

from .models import Machine, RepairRequest, MaintenanceHistory, Profile, User
from .forms import UserRegistrationForm, MachineForm, RepairRequestForm, UpdateStatusForm, ConfirmRepairForm

from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

@login_required
def dashboard(request):
    user_level = request.user.profile.level
    machines = Machine.objects.filter(classification_level__lte=user_level)
    pending_count = User.objects.filter(is_active=False).count() if user_level == 3 else 0

    # Badge màu trạng thái
    for machine in machines:
        if machine.status == 'working':
            machine.badge = 'bg-success'
        elif machine.status == 'maintenance':
            machine.badge = 'bg-warning'
        else:
            machine.badge = 'bg-danger'

    return render(request, 'dashboard.html', {'machines': machines, 'pending_count': pending_count})
@login_required
def users_list(request):
    if request.user.profile.level != 3:
        return HttpResponseForbidden()
    users = User.objects.all().select_related('profile')
    return render(request, 'users_list.html', {'users': users})

@login_required
def edit_user(request, pk):
    if request.user.profile.level != 3:
        return HttpResponseForbidden()
    user = get_object_or_404(User, pk=pk)
    profile = user.profile
    if request.method == 'POST':
        level = request.POST.get('level')
        is_active = request.POST.get('is_active') == 'on'
        if level in ['1', '2', '3']:
            profile.level = int(level)
            profile.save()
        user.is_active = is_active
        user.save()
        messages.success(request, _("Đã cập nhật thông tin tài khoản!"))
        return redirect('users_list')
    return render(request, 'edit_user.html', {'user_to_edit': user})

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
    if request.user.profile.level < 1:
        return HttpResponseForbidden()
    machine = get_object_or_404(Machine, pk=pk, classification_level__lte=request.user.profile.level)
    if request.method == 'POST':
        form = UpdateStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            description = form.cleaned_data['description']
            machine.status = new_status
            machine.save()
            if new_status in ['broken', 'maintenance'] and description:
                RepairRequest.objects.create(
                    machine=machine,
                    description=description,
                    requested_by=request.user
                )
                messages.info(request, _("Đã tự động tạo yêu cầu sửa chữa với mô tả: ") + description)
            messages.success(request, _("Cập nhật trạng thái thành công!"))
            return redirect('machine_detail', pk=pk)
    else:
        form = UpdateStatusForm(initial={'status': machine.status})
    return render(request, 'update_status.html', {'form': form, 'machine': machine})

@login_required
def export_machines_excel(request):
    if request.user.profile.level < 3:
        return HttpResponseForbidden()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=machines.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = "Danh sách máy móc"

    columns = ['Mã máy', 'Tên máy', 'Vị trí', 'Phân cấp', 'Trạng thái', 'Ngày nhận máy']
    ws.append(columns)

    for machine in Machine.objects.all():
        ws.append([
            machine.machine_code,
            machine.name,
            machine.location,
            f"Cấp {machine.classification_level}",
            machine.get_status_display(),
            machine.start_date.strftime("%d/%m/%Y %H:%M")
        ])

    wb.save(response)
    return response

@login_required
def export_machines_pdf(request):
    if request.user.profile.level < 3:
        return HttpResponseForbidden()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.drawString(100, height - 100, "Danh sách máy móc")
    y = height - 140
    for machine in Machine.objects.all():
        p.drawString(100, y, f"{machine.machine_code} - {machine.name} - {machine.get_status_display()}")
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 100

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="machines.pdf"'
    response.write(pdf)
    return response

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
    if request.user.profile.level != 3:
        return HttpResponseForbidden()
    user = get_object_or_404(User, pk=pk, is_active=False)
    if request.method == 'POST':
        level = request.POST.get('level')
        if level in ['1', '2', '3']:
            profile = user.profile
            profile.level = int(level)
            profile.save()
            user.is_active = True
            user.save()
            # Tự động đăng nhập cho user vừa duyệt (nếu họ truy cập ngay)
            # Nhưng vì đây là admin duyệt, không login hộ, chỉ kích hoạt
            messages.success(request, _("Đã duyệt và kích hoạt tài khoản! User có thể đăng nhập ngay."))
            return redirect('users_list')
    return render(request, 'approve_user.html', {'user_to_approve': user})