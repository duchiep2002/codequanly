from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MachineForm, RepairRequestForm
from .models import Machine, RepairRequest


@login_required
def dashboard(request):
    machines = Machine.objects.select_related("created_by").all().order_by("machine_code")
    return render(request, "dashboard.html", {"machines": machines})


@login_required
def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    repairs = RepairRequest.objects.filter(machine=machine).select_related("requested_by").order_by("-report_date", "-created_at")
    return render(
        request,
        "machine_detail.html",
        {
            "machine": machine,
            "repairs": repairs,
        },
    )


@login_required
def create_repair(request):
    if request.method == "POST":
        form = RepairRequestForm(request.POST)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.requested_by = request.user
            repair.save()
            return redirect("dashboard")
    else:
        form = RepairRequestForm()

    return render(request, "repair_create.html", {"form": form})


@login_required
def create_machine(request):
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
