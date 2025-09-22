from django.contrib import admin
from organizations.models import Organization, Role
from core.models import OrganizationContact


admin.site.register(Organization)
admin.site.register(Role)
admin.site.register(OrganizationContact)
