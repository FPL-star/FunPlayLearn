# admin.py
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib.auth.models import User
from people.models import Person, FPLMember, PersonSensitiveData, PersonEducation
from people.forms import FPLMemberForm


class PalikaAdminMixin(object):
    """

    Mixin to provide palika-based row-level security for ModelAdmins.

    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_palika = request.user.fpl_user.palika
            return qs.filter(palika=user_palika)
        except (AttributeError, FPLMember.DoesNotExist):
            return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser or (
            hasattr(request.user, "fpl_user") and request.user.fpl_user.palika
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not obj:  # List view
            return self.has_module_permission(request)
        return self._user_can_access_object(request.user, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "fpl_user") and request.user.fpl_user.palika

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not obj:
            return self.has_module_permission(request)
        return self._user_can_access_object(request.user, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not obj:
            return self.has_module_permission(request)
        return self._user_can_access_object(request.user, obj)

    def _user_can_access_object(self, user, obj):
        return hasattr(user, "fpl_user") and user.fpl_user.palika == obj.palika


# --- Inlines for FPLMemberAdmin ---


class PersonSensitiveDataInline(admin.TabularInline):
    model = PersonSensitiveData
    extra = 0
    fields = ("date_of_birth", "blood_type", "bank_account", "pan_number")


class PersonEducationInline(admin.TabularInline):
    model = PersonEducation
    extra = 0
    fields = ("level", "institution", "field_of_study", "is_current")


@admin.register(FPLMember)
class FPLMemberAdmin(PalikaAdminMixin, admin.ModelAdmin):
    form = FPLMemberForm  # This is the key line
    inlines = [PersonEducationInline]  # No need for the sensitive data inline
