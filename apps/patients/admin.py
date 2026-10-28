from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "age", "gender", "created_by", "created_at")
    list_filter = ("gender", "created_at")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("id", "created_by", "created_at", "updated_at")
    ordering = ("-created_at",)
