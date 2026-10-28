from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "hospital", "created_by", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = ("name", "email", "license_number", "hospital")
    readonly_fields = ("id", "created_by", "created_at", "updated_at")
    ordering = ("-created_at",)
