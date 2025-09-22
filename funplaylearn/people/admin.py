# admin.py - Updated admin configuration
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.contrib.auth.models import User
from people.models import Person, FPLMember, PersonSensitiveData, PersonEducation
from people.forms import FPLMemberForm, PersonForm
from organizations.models import Role


class RoleFilter(admin.SimpleListFilter):
    title = "Role"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        # Build the choices for the filter dropdown
        return [(r.id, str(r)) for r in Role.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person__role__id=self.value())
        return queryset


class NonFPLPersonFilter(admin.SimpleListFilter):
    title = "FPL Membership Status"
    parameter_name = "fpl_status"

    def lookups(self, request, model_admin):
        return (
            ("non_fpl", "Non-FPL Members Only"),
            ("fpl", "FPL Members Only"),
        )

    def queryset(self, request, queryset):
        if self.value() == "non_fpl":
            return queryset.filter(fpl_member__isnull=True)
        elif self.value() == "fpl":
            return queryset.filter(fpl_member__isnull=False)
        return queryset


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


@admin.register(FPLMember)
class FPLMemberAdmin(PalikaAdminMixin, admin.ModelAdmin):
    form = FPLMemberForm
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "photo",
                    "bio",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Organizational Information",
            {
                "fields": ("role", "palika", "start_date", "active", "agreement"),
                "classes": ("wide",),
            },
        ),
        (
            "Contact Information",
            {
                "fields": ("email", ("phone_country_code", "phone_number"), "address"),
                "classes": ("collapse", "wide"),
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                ),
                "classes": ("collapse", "wide"),
                "description": "Contact information for emergencies",
            },
        ),
        (
            "Education Information",
            {
                "fields": (
                    "edu_level",
                    "edu_institution",
                    "edu_field_of_study",
                    "is_current_edu",
                ),
                "classes": ("collapse", "wide"),
                "description": "Educational background information",
            },
        ),
        (
            "Medical & Financial Information",
            {
                "fields": (
                    "blood_type",
                    "date_of_birth",
                    "gender",
                    "bank_account",
                    "pan_number",
                ),
                "classes": ("collapse", "wide"),
                "description": "Sensitive medical and financial information",
            },
        ),
        (
            "Administrative Information",
            {
                "fields": (
                    "leave_date",
                    "sim_returned",
                    "account_closed",
                    "certificate_issued",
                ),
                "classes": ("collapse", "wide"),
                "description": "Administrative tracking fields",
            },
        ),
    )

    @admin.display(ordering="person__role__name", description="Role")
    def role(self, obj):
        return obj.person.role.name if obj.person.role else "-"

    list_display = (
        "person",
        "role",
        "palika",
        "start_date",
        "active",
        "agreement",
        "updated_at",
    )
    list_filter = (
        "active",
        "agreement",
        "palika",
        "start_date",
        RoleFilter,
    )
    search_fields = (
        "person__first_name",
        "person__last_name",
        "person__contact__email",
    )
    readonly_fields = ("updated_at",)

    def get_form(self, request, obj=None, **kwargs):
        """Override to add help text about automatic user creation"""
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Adding new object
            form.base_fields["first_name"].help_text = (
                "Username will be automatically created as: first_name.last_name@funplaylearn.org"
            )
        return form


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonForm
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("first_name", "last_name", "role", "gender", "photo", "bio"),
                "classes": ("wide",),
            },
        ),
        (
            "Contact Information",
            {
                "fields": ("email", ("phone_country_code", "phone_number"), "address"),
                "classes": (
                    "collapse",
                    "wide",
                ),
                "description": "Optional contact information",
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                ),
                "classes": ("collapse", "wide"),
                "description": "Optional emergency contact information",
            },
        ),
    )

    @admin.display(ordering="role__name", description="Full Name")
    def full_name(self, obj):
        return obj.full_name

    @admin.display(ordering="role__organization__name", description="Organization")
    def organization(self, obj):
        return obj.role.organization.name if obj.role and obj.role.organization else "-"

    def has_contact_info(self, obj):
        if hasattr(obj, "contact") and obj.contact:
            has_info = any(
                [obj.contact.email, obj.contact.phone_number, obj.contact.address]
            )
            return has_info
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["role"].help_text = (
            "Select the person's role in the organization"
        )
        return form

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("role", "contact")

    has_contact_info.short_description = "Has Contact Info"
    has_contact_info.boolean = True

    list_display = ("full_name", "organization", "role", "has_contact_info")
    list_filter = ("role", "gender", "role__organization", NonFPLPersonFilter)
    search_fields = ("first_name", "last_name", "contact__email")
    ordering = ("last_name", "first_name")
