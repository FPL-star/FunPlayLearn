from django.contrib import admin
from .models import Palika, OrganizationType, SchoolType, Class, Weekday


# Register your models here.
class ReadOnlyModelAdmin(admin.ModelAdmin):
    """Base admin model for read-only taxonomies"""

    def has_add_permission(self, request):
        """Prevent adding new records"""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing existing records"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting records"""
        return False


@admin.register(Palika)
class PalikaAdmin(admin.ModelAdmin):
    list_display = ("palika_display", "abbr_display")
    search_fields = ("palika", "short_name")
    list_filter = ("short_name",)
    fields = ("palika", "short_name")

    @admin.display(description="Palika")
    def palika_display(self, obj):
        return obj.palika.title()

    @admin.display(description="Abbreviation")
    def abbr_display(self, obj):
        return obj.short_name.upper()


# @admin.register(OrganizationType)
# class OrganizationTypeAdmin(ReadOnlyModelAdmin):
#     pass


# @admin.register(SchoolType)
# class SchoolTypeAdmin(ReadOnlyModelAdmin):
#     pass


# @admin.register(Class)
# class ClassAdmin(ReadOnlyModelAdmin):
#     pass


# @admin.register(Weekday)
# class WeekdayAdmin(ReadOnlyModelAdmin):
#     pass
