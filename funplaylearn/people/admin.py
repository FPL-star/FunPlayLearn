from django.contrib import admin
from people.models import Person, FPLMember
from people.forms import FPLMemberForm, PersonForm
from organizations.models import Role


class RoleFilter(admin.SimpleListFilter):
    title = "Role"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        return [(r.id, str(r)) for r in Role.objects.all()]

    def queryset(self, request, qs):
        return qs.filter(person__role__id=self.value()) if self.value() else qs


class NonFPLPersonFilter(admin.SimpleListFilter):
    title = "FPL Membership Status"
    parameter_name = "fpl_status"

    def lookups(self, request, model_admin):
        return (("non_fpl", "Non-FPL Members Only"), ("fpl", "FPL Members Only"))

    def queryset(self, request, qs):
        if self.value() == "non_fpl":
            return qs.filter(fpl_member__isnull=True)
        if self.value() == "fpl":
            return qs.filter(fpl_member__isnull=False)
        return qs


class PalikaAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            return qs.filter(palika=request.user.fpl_member.palika)
        except:
            return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser or getattr(request.user, "fpl_member", None)

    def _user_can_access_object(self, user, obj):
        return (
            getattr(user, "fpl_member", None) and user.fpl_member.palika == obj.palika
        )

    def has_view_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or (not obj and self.has_module_permission(request))
            or self._user_can_access_object(request.user, obj)
        )

    has_add_permission = has_change_permission = has_delete_permission = (
        has_view_permission
    )


@admin.register(FPLMember)
class FPLMemberAdmin(PalikaAdminMixin, admin.ModelAdmin):
    form = FPLMemberForm
    readonly_fields = ("updated_at",)
    list_display = (
        "person",
        "role",
        "palika",
        "start_date",
        "active",
        "agreement",
        "updated_at",
    )
    list_filter = ("active", "agreement", "palika", "start_date", RoleFilter)
    search_fields = (
        "person__first_name",
        "person__last_name",
        "person__contact__email",
    )
    fieldsets = (
        ("Basic Information", {"fields": ("first_name", "last_name", "photo", "bio")}),
        (
            "Organizational Information",
            {"fields": ("role", "palika", "start_date", "active", "agreement")},
        ),
        (
            "Contact Information",
            {
                "fields": ("email", ("phone_country_code", "phone_number"), "address"),
                "classes": ("collapse",),
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
                "classes": ("collapse",),
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
                "classes": ("collapse",),
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
                "classes": ("collapse",),
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
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(ordering="person__role__name", description="Role")
    def role(self, obj):
        return obj.person.role.name if obj.person.role else "-"


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonForm
    list_display = ("full_name", "organization", "role", "has_contact_info")
    list_filter = ("role", "gender", "role__organization", NonFPLPersonFilter)
    search_fields = ("first_name", "last_name", "contact__email")
    ordering = ("last_name", "first_name")
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("first_name", "last_name", "role", "gender", "photo", "bio")},
        ),
        (
            "Contact Information",
            {
                "fields": ("email", ("phone_country_code", "phone_number"), "address"),
                "classes": ("collapse",),
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
                "classes": ("collapse",),
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
        return bool(
            obj.contact
            and any([obj.contact.email, obj.contact.phone_number, obj.contact.address])
        )

    has_contact_info.boolean, has_contact_info.short_description = (
        True,
        "Has Contact Info",
    )
