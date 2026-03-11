from django.contrib import admin
from .models import Machine, RepairRequest, MaintenanceHistory, Profile

admin.site.register(Machine)
admin.site.register(RepairRequest)
admin.site.register(MaintenanceHistory)
admin.site.register(Profile)