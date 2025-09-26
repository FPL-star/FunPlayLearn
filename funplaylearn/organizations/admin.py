from django.contrib import admin
from organizations.models import Organization, Role


admin.site.register(Organization)
admin.site.register(Role)
