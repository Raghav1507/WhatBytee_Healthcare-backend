from django.contrib import admin

from .models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "assigned_by", "assigned_at")
    list_filter = ("assigned_at",)
    search_fields = ("patient__name", "doctor__name")
    readonly_fields = ("id", "assigned_by", "assigned_at")
    ordering = ("-assigned_at",)
