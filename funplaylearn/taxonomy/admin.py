from django.contrib import admin
from .models import Palika, OrganizationType, SchoolType, Class, Weekday

# Register your models here.
admin.site.register(Palika)
admin.site.register(OrganizationType)
admin.site.register(SchoolType)
admin.site.register(Class)
admin.site.register(Weekday)
