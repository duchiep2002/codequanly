from django import forms

from .models import Machine, RepairRequest


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ["machine_code", "machine_name", "location", "status"]


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = [
            "machine",
            "report_date",
            "reporter_level",
            "description",
            "repair_requirement",
            "assurance_status",
            "status",
        ]
        widgets = {
            "report_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "repair_requirement": forms.Textarea(attrs={"rows": 3}),
        }
