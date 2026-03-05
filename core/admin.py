from django.contrib import admin
from .models import Machine, RepairRequest, MaintenanceHistory

admin.site.register(Machine)
admin.site.register(RepairRequest)
admin.site.register(MaintenanceHistory)