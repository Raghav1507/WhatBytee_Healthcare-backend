from django.apps import AppConfig


class MappingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mappings"
    label = "mappings"
    verbose_name = "Patient-Doctor Mappings"
